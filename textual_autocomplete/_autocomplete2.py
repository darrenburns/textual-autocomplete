from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, ClassVar, Iterable, Literal, cast
from rich.measure import Measurement
from rich.style import Style, StyleType
from rich.text import Text, TextType
from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.css.query import NoMatches
from textual.geometry import Region
from textual.widget import Widget
from textual.widgets import Input, TextArea, OptionList
from textual.widgets.option_list import Option
from textual.widgets.text_area import Selection


@dataclass
class TargetState:
    text: str
    """The content in the target widget."""

    selection: Selection
    """The selection of the target widget."""


class InvalidTarget(Exception):
    """Raised if the target is invalid, i.e. not something which can
    be autocompleted."""


class DropdownItem(Option):
    def __init__(
        self,
        main: TextType,
        left_meta: TextType | None = None,
        right_meta: TextType | None = None,
        search_string: str = "",
        highlight_ranges: Iterable[tuple[int, int]] | None = None,
        highlight_style: StyleType | None = None,
        id: str | None = None,
        disabled: bool = False,
    ) -> None:
        """A single option appearing in the autocompletion dropdown. Each option has up to 3 columns.
        Note that this is not a widget, it's simply a data structure for describing dropdown items.

        Args:
            left: The left column will often contain an icon/symbol, the main (middle)
                column contains the text that represents this option.
            main: The main text representing this option - this will be highlighted by default.
                In an IDE, the `main` (middle) column might contain the name of a function or method.
            right: The text appearing in the right column of the dropdown.
                The right column often contains some metadata relating to this option.
            highlight_ranges: Custom ranges to highlight. By default, the value is None,
                meaning textual-autocomplete will highlight substrings in the dropdown.
                That is, if the value you've typed into the Input is a substring of the candidates
                `main` attribute, then that substring will be highlighted. If you supply your own
                implementation of `items` which uses a more complex process to decide what to
                display in the dropdown, then you can customise the highlighting of the returned
                candidates by supplying index ranges to highlight.
        """
        self.main = Text(main, no_wrap=True) if isinstance(main, str) else main
        self.left_meta = (
            Text(left_meta, no_wrap=True) if isinstance(left_meta, str) else left_meta
        )
        self.right_meta = (
            Text(right_meta, no_wrap=True)
            if isinstance(right_meta, str)
            else right_meta
        )
        self.search_string = search_string
        self.highlight_ranges = highlight_ranges
        self.highlight_style = highlight_style

        prompt = self.main.copy()
        if self.search_string and highlight_style:
            highlight_style = (
                Style.parse(highlight_style)
                if isinstance(highlight_style, str)
                else highlight_style
            )
            if self.highlight_ranges:
                for highlight in self.highlight_ranges:
                    prompt.stylize(highlight_style, *highlight)
            else:
                prompt.highlight_words(
                    [search_string], highlight_style, case_sensitive=False
                )

        # TODO - this is a hack to work around what appears to be an issue in Textual.
        prompt += " "
        super().__init__(prompt, id, disabled)


class AutoCompleteList(OptionList):
    def get_content_width(self, container: events.Size, viewport: events.Size) -> int:
        """Get maximum width of options."""
        console = self.app.console
        options = console.options
        max_width = max(
            (
                Measurement.get(console, options, option.prompt).maximum
                for option in self._options
            ),
            default=4,
        )
        return max_width


class AutoComplete(Widget):
    BINDINGS = [
        Binding("escape", "hide", "Hide dropdown", show=False),
    ]

    DEFAULT_CSS = """\
    AutoComplete {
        layer: textual-autocomplete;
        dock: top;  /* if we dont dock, it appears behind docked widgets */
        height: auto;
        width: auto;
        max-height: 12;
        display: none;
        background: $surface-lighten-1;

        & AutoCompleteList {
            width: auto;
            height: auto;
            border: none;
            padding: 0;
            margin: 0;
            scrollbar-size-vertical: 1;
            scrollbar-size-horizontal: 0;
            scrollbar-gutter: stable;
            &:focus {
                border: none;
                padding: 0;
                margin: 0;
            }
            & > .option-list--option-highlighted {
                color: $text;
                background: $boost;
            }
        }

        & .autocomplete--highlight-match {
            color: $text;
            background: $primary-lighten-1;
        }
    }
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "autocomplete--highlight-match",
        "autocomplete--left-column",
        "autocomplete--main-column",
        "autocomplete--right-column",
    }

    def __init__(
        self,
        target: Input | TextArea | str,
        items: list[DropdownItem] | Callable[[TargetState], list[DropdownItem]],
        completion_strategy: (
            Literal["append", "replace", "insert"]
            | Callable[[str, TargetState], TargetState]
        ) = "replace",
        prevent_default_enter: bool = True,
        prevent_default_tab: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._target = target
        """An Input instance, TextArea instance, or a selector string used to query an Input/TextArea instance.
        
        Must be on the same screen as """
        """The dropdown instance to use."""
        self.completion_strategy = completion_strategy
        self.items = items
        self.prevent_default_enter = prevent_default_enter
        self.prevent_default_tab = prevent_default_tab
        self._last_search_string = ""
        self._target_state = TargetState("", Selection.cursor((0, 0)))

    def compose(self) -> ComposeResult:
        option_list = AutoCompleteList()
        option_list.can_focus = False
        yield option_list

    def on_mount(self) -> None:
        # Subscribe to the target widget's reactive attributes.
        self.target.message_signal.subscribe(self, self._hijack_keypress)
        self.screen.screen_layout_refresh_signal.subscribe(
            self, lambda _event: self._align_to_target()
        )
        self._subscribe_to_target()
        self._handle_target_update()

    def _hijack_keypress(self, event: events.Event) -> None:
        """Hijack some keypress events of the target widget."""

        try:
            option_list = self.option_list
        except NoMatches:
            # This can happen if the event is an Unmount event
            # during application shutdown.
            return

        if isinstance(event, events.Key) and option_list.option_count:
            displayed = self.display
            highlighted = option_list.highlighted or 0
            if event.key == "down":
                event.prevent_default()
                # If you press `down` while in an Input and the autocomplete is currently
                # hidden, then we should show the dropdown.
                if isinstance(self.target, Input):
                    if not displayed:
                        self.display = True
                        highlighted = 0
                    else:
                        highlighted = (highlighted + 1) % option_list.option_count
                option_list.highlighted = highlighted

            elif event.key == "up":
                event.prevent_default()
                highlighted = (highlighted - 1) % option_list.option_count
                option_list.highlighted = highlighted
            elif event.key == "enter":
                if self.prevent_default_enter and displayed:
                    event.prevent_default()
                self._complete_highlighted_item()
            elif event.key == "tab":
                if self.prevent_default_tab and displayed:
                    event.prevent_default()
                self._complete_highlighted_item()
            elif event.key == "escape":
                self.action_hide()

    def action_hide(self) -> None:
        self.styles.display = "none"

    def _complete_highlighted_item(self) -> None:
        if not self.display:
            return

        target = self.target
        completion_strategy = self.completion_strategy
        option_list = self.option_list
        highlighted = option_list.highlighted or 0
        option = cast(DropdownItem, option_list.get_option_at_index(highlighted))
        highlighted_value = option.main.plain
        if isinstance(target, Input):
            if completion_strategy == "replace":
                target.value = ""
                target.insert_text_at_cursor(highlighted_value)
            elif completion_strategy == "insert":
                target.insert_text_at_cursor(highlighted_value)
            elif completion_strategy == "append":
                old_value = target.value
                new_value = old_value + highlighted_value
                target.value = new_value
                target.action_end()
            else:
                if callable(completion_strategy):
                    new_state = completion_strategy(
                        highlighted_value,
                        TargetState(
                            text=target.value,
                            selection=Selection.cursor(0, target.cursor_position),
                        ),
                    )
                    target.value = new_state.text
                    target.cursor_position = new_state.selection.end[1]

        # Hide the dropdown after completion, even if there are still matches.
        self.action_hide()

    @property
    def target(self) -> Input | TextArea:
        """The resolved target widget."""
        if isinstance(self._target, (Input, TextArea)):
            return self._target
        else:
            target = self.screen.query_one(self._target)
            assert isinstance(target, (Input, TextArea))
            return target

    def _subscribe_to_target(self) -> None:
        """Attempt to subscribe to the target widget, if it's available."""
        target = self.target
        if isinstance(target, Input):
            self.watch(target, "value", self._handle_target_update)
            self.watch(target, "cursor_position", self._handle_target_update)
        else:
            self.watch(target, "text", self._handle_target_update)
            self.watch(target, "selection", self._handle_target_update)

    def _align_to_target(self) -> None:
        cursor_x, cursor_y = self.target.cursor_screen_offset

        dropdown = self.query_one(OptionList)
        width, height = dropdown.size
        x, y, _width, _height = Region(
            cursor_x,
            cursor_y + 1,
            width,
            height,
        ).translate_inside(self.screen.region)

        self.styles.offset = x, y

    def _get_target_state(self) -> TargetState:
        target = self.target
        is_text_area = isinstance(target, TextArea)
        return TargetState(
            text=target.text if is_text_area else target.value,
            selection=target.selection
            if is_text_area
            else Selection.cursor((0, target.cursor_position)),
        )

    def _handle_target_update(self) -> None:
        """Called when the state (text or selection) of the target is updated."""
        search_string = self.search_string

        self._target_state = self._get_target_state()
        self._rebuild_options(self._target_state)
        self._align_to_target()

        if len(search_string) == 0:
            self.styles.display = "none"
        elif len(search_string) > len(self._last_search_string):
            self.styles.display = "block" if self.option_list.option_count else "none"

        self._last_search_string = search_string
        print(f"num option = {self.option_list.option_count}")

    def _rebuild_options(self, target_state: TargetState) -> None:
        """Rebuild the options in the dropdown."""
        option_list = self.option_list

        option_list.clear_options()
        matches = self._compute_matches(target_state)
        if matches:
            option_list.add_options(matches)
            option_list.highlighted = 0

    @property
    def search_string(self) -> str:
        """The string that is being used to query the dropdown.

        This may be the text in the target widget, or a substring of that text.
        """
        target = self.target
        if isinstance(target, Input):
            return target.value
        else:
            row, col = target.cursor_location
            line = target.document.get_line(row)

            for index in range(col, -1, -1):
                if not line[index].isalnum():
                    query_string = line[index + 1 : col + 1]
                    return query_string

            return ""

    def _compute_matches(self, target_state: TargetState) -> list[DropdownItem]:
        """Compute the matches based on the target state."""
        items = self.items
        matcher = items if callable(items) else self.matcher
        matches = matcher(target_state)
        return matches

    def matcher(self, target_state: TargetState) -> list[DropdownItem]:
        """Given the state of the target widget, return the DropdownItems
        which match the query string and should be appear in the dropdown."""
        items = self.items
        matches: list[DropdownItem] = []
        assert isinstance(items, list)
        value = target_state.text
        search_string = self.search_string
        print(f"search_string: {search_string!r}")
        highlight_style = self.get_component_rich_style("autocomplete--highlight-match")
        for item in items:
            text = item.main
            if value.lower() in text.plain.lower():
                matches.append(
                    DropdownItem(
                        left_meta=item.left_meta,
                        main=item.main,
                        right_meta=item.right_meta,
                        search_string=search_string,
                        highlight_ranges=item.highlight_ranges,
                        highlight_style=highlight_style
                        if item.highlight_style is None
                        else item.highlight_style,
                    )
                )

        matches = sorted(
            matches,
            key=lambda match: not match.main.plain.lower().startswith(value.lower()),
        )

        return matches

    @property
    def option_list(self) -> AutoCompleteList:
        return self.query_one(AutoCompleteList)
