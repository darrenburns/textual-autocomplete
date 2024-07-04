from __future__ import annotations

from dataclasses import dataclass
from operator import itemgetter
from typing import Callable, ClassVar, Literal, Optional, cast
from rich.measure import Measurement
from rich.style import Style
from rich.text import Text, TextType
from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.command import on
from textual.css.query import NoMatches
from textual_autocomplete.matcher import Matcher
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
        # popup: TextType | None = None,
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
            search_string: The string that is being used for matching.
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
            Text(left_meta, no_wrap=True, style="dim")
            if isinstance(left_meta, str)
            else left_meta
        )
        # self.popup = (
        #     Text(popup, no_wrap=True, style="dim") if isinstance(popup, str) else popup
        # )
        left = self.left_meta
        prompt = self.main
        if left:
            prompt = Text.assemble(left, " ", self.main)

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
            default=1,
        )
        max_width += self.scrollbar_size_vertical
        return max_width


MatcherFactoryType = Callable[[str, Optional[Style], bool], Matcher]


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
            &:focus {
                border: none;
                padding: 0;
                margin: 0;
            }
            & > .option-list--option-highlighted, & > .option-list--option-hover-highlighted {
                color: $text;
                background: $surface-lighten-3 60%;
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
    }

    def __init__(
        self,
        target: Input | TextArea | str,
        items: list[DropdownItem] | Callable[[TargetState], list[DropdownItem]],
        matcher_factory: MatcherFactoryType | None = None,
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
        
        Must be on the same screen as the dropdown instance."""

        self.completion_strategy = completion_strategy
        """The strategy that should be use to do the completion.
        
        You can pass a string literal to use one of the built-in strategies, or a function
        which takes the highlighted value in the dropdown and the current state of the target widget 
        and returns what the new state of the target widget should be after the completion has been applied.
        """

        self.items = items
        """The items to match on, or a function which returns the items to match on."""

        self.matcher_factory = Matcher if matcher_factory is None else matcher_factory
        """A factory function that returns the Matcher to use for matching and highlighting."""

        self.prevent_default_enter = prevent_default_enter
        """Prevent the default enter behaviour."""

        self.prevent_default_tab = prevent_default_tab
        """Prevent the default tab behaviour."""

        self._last_search_string = ""

        self._target_state = TargetState("", Selection.cursor((0, 0)))

    def compose(self) -> ComposeResult:
        option_list = AutoCompleteList(wrap=False)
        option_list.can_focus = False
        yield option_list

    def on_mount(self) -> None:
        # Subscribe to the target widget's reactive attributes.
        self.target.message_signal.subscribe(self, self._hijack_keypress)  # type: ignore
        self.screen.screen_layout_refresh_signal.subscribe(  # type: ignore
            self,
            lambda _event: self._align_to_target(),  # type: ignore
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
                if displayed:
                    event.prevent_default()
                    highlighted = (highlighted - 1) % option_list.option_count
                    option_list.highlighted = highlighted
            elif event.key == "enter":
                if self.prevent_default_enter and displayed:
                    event.prevent_default()
                self._complete(option_index=highlighted)
            elif event.key == "tab":
                if self.prevent_default_tab and displayed:
                    event.prevent_default()
                self._complete(option_index=highlighted)
            elif event.key == "escape":
                self.action_hide()

    def action_hide(self) -> None:
        self.styles.display = "none"

    def _complete(self, option_index: int) -> None:
        """Do the completion (i.e. insert the selected item into the target input/textarea).

        This is when the user highlights an option in the dropdown and presses tab or enter.
        """
        if not self.display:
            return

        target = self.target
        completion_strategy = self.completion_strategy
        option_list = self.option_list
        highlighted = option_index
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
                        self._get_target_state(),
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

        self.watch(target, "has_focus", self._handle_focus_change)

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
        """Get the state of the target widget."""
        target = self.target
        if isinstance(target, Input):
            return TargetState(
                text=target.value,
                selection=Selection.cursor((0, target.cursor_position)),  # type: ignore
            )
        else:
            return TargetState(
                text=target.text,
                selection=target.selection,
            )

    def _handle_focus_change(self, has_focus: bool) -> None:
        """Called when the focus of the target widget changes."""
        if not has_focus:
            self.action_hide()
        else:
            self._rebuild_options(self._target_state)

    def _handle_target_update(self) -> None:
        """Called when the state (text or selection) of the target is updated."""
        search_string = self.get_search_string()
        self._target_state = self._get_target_state()
        self._rebuild_options(self._target_state)
        self._align_to_target()

        if len(search_string) == 0:
            self.styles.display = "none"
        elif len(search_string) > len(self._last_search_string):
            self.styles.display = "block" if self.option_list.option_count else "none"

        self._last_search_string = search_string

    def _rebuild_options(self, target_state: TargetState) -> None:
        """Rebuild the options in the dropdown.

        Args:
            target_state: The state of the target widget.
        """
        option_list = self.option_list
        option_list.clear_options()
        if self.target.has_focus:
            matches = self._compute_matches(target_state)
            if matches:
                option_list.add_options(matches)
                option_list.highlighted = 0

    def get_search_string(self) -> str:
        """This value will be passed to the matcher.

        This could be, for example, the text in the target widget, or a substring of that text.

        For Input widgets the default is to use the text in the input, and for TextArea widgets
        the default is to use the text in the TextArea before the cursor up to the most recent
        non-alphanumeric character.

        Subclassing AutoComplete to create a custom `get_search_string` method is a way to
        customise the behaviour of the autocomplete dropdown.

        Returns:
            The search string that will be used to filter the dropdown options.
        """
        target = self.target
        if isinstance(target, Input):
            return target.value
        else:
            row, col = target.cursor_location
            line = target.document.get_line(row)

            for index in range(col, 0, -1):
                if not line[index].isalnum():
                    query_string = line[index + 1 : col + 1]
                    return query_string

            return ""

    def _compute_matches(self, target_state: TargetState) -> list[DropdownItem]:
        """Compute the matches based on the target state.

        Args:
            target_state: The state of the target widget.

        Returns:
            The matches to display in the dropdown.
        """

        # If items is a callable, then it's a factory function that returns the candidates.
        # Otherwise, it's a list of candidates.
        items = self.items
        candidates = items(target_state) if callable(items) else items
        return self.get_matches(target_state, candidates)

    def get_matches(
        self, target_state: TargetState, candidates: list[DropdownItem]
    ) -> list[DropdownItem]:
        """Given the state of the target widget, return the DropdownItems
        which match the query string and should be appear in the dropdown.

        Args:
            target_state: The state of the target widget.
            candidates: The candidates to match against.

        Returns:
            The matches to display in the dropdown.
        """
        search_string = self.get_search_string()
        if not search_string:
            return candidates

        match_style = self.get_component_rich_style("autocomplete--highlight-match")
        matcher = self.matcher_factory(search_string, match_style, False)

        matches_and_scores: list[tuple[DropdownItem, float]] = []
        append_score = matches_and_scores.append
        get_score = matcher.match
        get_highlighted = matcher.highlight

        for candidate in candidates:
            candidate_string = candidate.main.plain
            if (score := get_score(candidate_string)) > 0:
                highlighted_text = get_highlighted(candidate_string)
                highlighted_item = DropdownItem(
                    main=highlighted_text,
                    left_meta=candidate.left_meta,
                    id=candidate.id,
                    disabled=candidate.disabled,
                )
                append_score((highlighted_item, score))

        matches_and_scores.sort(key=itemgetter(1), reverse=True)
        matches = [match for match, _ in matches_and_scores]
        return matches

    @property
    def option_list(self) -> AutoCompleteList:
        return self.query_one(AutoCompleteList)

    @on(OptionList.OptionSelected, "AutoCompleteList")
    def _apply_completion(self, event: OptionList.OptionSelected) -> None:
        self._complete(event.option_index)
