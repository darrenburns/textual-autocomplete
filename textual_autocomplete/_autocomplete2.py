from __future__ import annotations

from dataclasses import dataclass
from functools import partial
import functools
from operator import itemgetter
import types
from typing import (
    Callable,
    ClassVar,
    Iterator,
    NamedTuple,
    Optional,
    TypeVar,
    Union,
    cast,
)
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
from textual.widgets.text_area import Location, Selection


@dataclass
class TargetState:
    text: str
    """The content in the target widget."""

    selection: Selection
    """The selection of the target widget."""


class SearchString(NamedTuple):
    start_location: int
    value: str


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

TargetType = TypeVar("TargetType", bound=Union[Input, TextArea])


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
        candidates: list[DropdownItem] | Callable[[TargetState], list[DropdownItem]],
        matcher_factory: MatcherFactoryType | None = None,
        completion_strategy: (
            Callable[[str, TargetState], TargetState | None] | None
        ) = None,
        search_string: Callable[[TargetState], str] | None = None,
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
        """A function which modifies the state of the target widget 
        to perform the completion.
        If None, the default behavior will be used.
        """

        self.candidates = candidates
        """The candidates to match on, or a function which returns the candidates to match on."""

        self.matcher_factory = Matcher if matcher_factory is None else matcher_factory
        """A factory function that returns the Matcher to use for matching and highlighting."""

        self.search_string = search_string
        """A function that returns the search string to match on.
        
        This is the string that will be passed into the matcher.

        If None, the default the default behavior will be used.

        For Input widgets, the default behavior is to use the entire value 
        as the search string.

        For TextArea widgets, the default behavior is to use the text before the cursor 
        as the search string, up until the last whitespace.
        """

        self.prevent_default_enter = prevent_default_enter
        """Prevent the default enter behavior."""

        self.prevent_default_tab = prevent_default_tab
        """Prevent the default tab behavior."""

        self.last_action_was_completion = False
        """Used to filter duplicate performing an action twice on a character insertion.
        An insertion/deletion moves the cursor and creates a "changed" event, so we end up
        with two events for the same action.
        """

        self._target_state = TargetState("", Selection.cursor((0, 0)))
        """Cached state of the target Input/TextArea."""

        self._patch_on_event()

    def compose(self) -> ComposeResult:
        option_list = AutoCompleteList(wrap=False)
        option_list.can_focus = False
        yield option_list

    def on_mount(self) -> None:
        # Subscribe to the target widget's reactive attributes.
        self.target.message_signal.subscribe(self, self._listen_to_messages)  # type: ignore
        self.screen.screen_layout_refresh_signal.subscribe(  # type: ignore
            self,
            lambda _event: self._align_to_target(),  # type: ignore
        )
        self._subscribe_to_target()
        self._handle_target_update()

    def _patch_on_event(self) -> None:
        target = self.target
        if isinstance(target, TextArea):
            original_on_event = target.on_event

            @functools.wraps(original_on_event)
            async def on_event(text_area: TextArea, event: events.Event) -> None:
                if (
                    isinstance(event, events.Key)
                    and event.key in {"tab", "enter"}
                    and self.styles.display != "none"
                ):
                    self._complete(self.option_list.highlighted or 0)
                    return
                return await original_on_event(event)

            bound_on_event = types.MethodType(on_event, target)
            setattr(target, "on_event", bound_on_event)

    def _listen_to_messages(self, event: events.Event) -> None:
        """Listen to some events of the target widget."""

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
                # Check if there's only one item and it matches the search string
                if option_list.option_count == 1:
                    search_string = self.get_search_string(self._get_target_state())
                    first_option = option_list.get_option_at_index(0).prompt
                    text_from_option = (
                        first_option.plain
                        if isinstance(first_option, Text)
                        else first_option
                    )
                    if text_from_option == search_string:
                        # Don't prevent default behavior in this case
                        return

                event.stop()
                event.prevent_default()
                # If you press `down` while in an Input and the autocomplete is currently
                # hidden, then we should show the dropdown.
                if isinstance(self.target, Input):
                    if not displayed:
                        self.display = True
                        highlighted = 0
                    else:
                        highlighted = (highlighted + 1) % option_list.option_count
                else:
                    if displayed:
                        highlighted = (highlighted + 1) % option_list.option_count

                option_list.highlighted = highlighted

            elif event.key == "up":
                if displayed:
                    event.stop()
                    event.prevent_default()
                    highlighted = (highlighted - 1) % option_list.option_count
                    option_list.highlighted = highlighted
            elif event.key == "enter":
                if self.prevent_default_enter and displayed:
                    event.stop()
                    event.prevent_default()
                self._complete(option_index=highlighted)
            elif event.key == "tab":
                if self.prevent_default_tab and displayed:
                    event.stop()
                    event.prevent_default()
                self._complete(option_index=highlighted)
            elif event.key == "escape":
                self.action_hide()

        if isinstance(event, (Input.Changed, TextArea.Changed)):
            self._handle_target_update()

    def action_hide(self) -> None:
        self.styles.display = "none"

    def action_show(self) -> None:
        self.styles.display = "block"

    def _complete(self, option_index: int) -> None:
        """Do the completion (i.e. insert the selected item into the target input/textarea).

        This is when the user highlights an option in the dropdown and presses tab or enter.
        """
        if not self.display or self.option_list.option_count == 0:
            return

        target = self.target
        completion_strategy = self.completion_strategy
        option_list = self.option_list
        highlighted = option_index
        option = cast(DropdownItem, option_list.get_option_at_index(highlighted))
        highlighted_value = option.main.plain
        if isinstance(target, Input):
            if completion_strategy is None:
                target.value = ""
                target.insert_text_at_cursor(highlighted_value)
            elif callable(completion_strategy):
                completion_strategy(
                    highlighted_value,
                    self._get_target_state(),
                )
        else:  # elif isinstance(target, TextArea):
            if completion_strategy is None:
                replacement_range = self.get_text_area_word_bounds_before_cursor(target)
                target.replace(highlighted_value, *replacement_range)
            elif callable(completion_strategy):
                completion_strategy(
                    highlighted_value,
                    self._get_target_state(),
                )

        # Set a flag indicating that the last action that was performed
        # was a completion. This is so that when the target posts a Changed message
        # as a result of this completion, we can opt to ignore it in `handle_target_updated`
        self.last_action_was_completion = True
        self.action_hide()

    def yield_characters_before_cursor(
        self, target: TextArea
    ) -> Iterator[tuple[str, Location]]:
        cursor_location = target.cursor_location

        cursor_row, column = cursor_location
        start = (cursor_row, 0)
        text = target.get_text_range(start=start, end=cursor_location)
        for char in reversed(text):
            column -= 1
            yield char, (cursor_row, column)

    def get_text_area_word_bounds_before_cursor(
        self, target: TextArea
    ) -> tuple[Location, Location]:
        """Get the bounds of the word before the cursor in a TextArea.

        A word is defined as a sequence of alphanumeric characters or underscores,
        bounded by the start of the line, a space, or a non-alphanumeric character.

        Returns:
            A tuple containing the start and end positions of the word as (row, column) tuples.
        """
        cursor_location = target.cursor_location
        for char, (row, column) in self.yield_characters_before_cursor(target):
            if not char.isalnum() and char not in "$_-":
                return (row, column + 1), cursor_location
            elif column == 0:
                return (row, column), cursor_location

        return cursor_location, cursor_location

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
        self.watch(target, "has_focus", self._handle_focus_change)
        if isinstance(target, Input):
            self.watch(target, "cursor_position", self._align_to_target)
        else:
            self.watch(target, "selection", self._align_to_target)

    def _handle_target_message(self, message: events.Event) -> None:
        if isinstance(message, (Input.Changed, TextArea.Changed)):
            self._handle_target_update()

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
            search_string = self.get_search_string(self._target_state)
            self._rebuild_options(self._target_state, search_string)

    def _handle_target_update(self) -> None:
        """Called when the state (text or selection) of the target is updated.

        Here we align the dropdown to the target, determine if it should be visible,
        and rebuild the options in it.
        """
        self._target_state = self._get_target_state()
        search_string = self.get_search_string(self._target_state)

        # Determine visibility after the user makes a change in the
        # target widget (e.g. typing in a character in the Input).
        should_show = self.should_show_dropdown(search_string)
        if should_show and not self.last_action_was_completion:
            self.action_show()
            self._rebuild_options(self._target_state, search_string)
            self._align_to_target()
        else:
            self.action_hide()

        # We've rebuilt the options based on the latest change,
        # however, if the user made that change via selecting a completion
        # from the dropdown, then we always want to hide the dropdown.
        if self.last_action_was_completion:
            self.last_action_was_completion = False
            self.action_hide()
            return

    def should_show_dropdown(self, search_string: str) -> bool:
        """
        Determine whether to show or hide the dropdown based on the current state.

        This method can be overridden to customize the visibility behavior.

        Args:
            search_string: The current search string.

        Returns:
            bool: True if the dropdown should be shown, False otherwise.
        """
        option_list = self.option_list
        option_count = option_list.option_count

        if len(search_string) == 0 or option_count == 0:
            return False
        elif option_count == 1:
            first_option = option_list.get_option_at_index(0).prompt
            text_from_option = (
                first_option.plain if isinstance(first_option, Text) else first_option
            )
            return text_from_option.lower() != search_string.lower()
        else:
            return True

    def _rebuild_options(self, target_state: TargetState, search_string: str) -> None:
        """Rebuild the options in the dropdown.

        Args:
            target_state: The state of the target widget.
        """
        option_list = self.option_list
        option_list.clear_options()
        if self.target.has_focus:
            matches = self._compute_matches(target_state, search_string)
            if matches:
                option_list.add_options(matches)
                option_list.highlighted = 0

    def get_search_string(self, target_state: TargetState) -> str:
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
        if self.search_string is not None:
            search_string = self.search_string(target_state)
            return search_string

        if isinstance(self.target, Input):
            return target_state.text
        else:
            start, end = self.get_text_area_word_bounds_before_cursor(self.target)
            search_string = self.target.get_text_range(start, end)
            return search_string

    def _compute_matches(
        self, target_state: TargetState, search_string: str
    ) -> list[DropdownItem]:
        """Compute the matches based on the target state.

        Args:
            target_state: The state of the target widget.

        Returns:
            The matches to display in the dropdown.
        """

        # If items is a callable, then it's a factory function that returns the candidates.
        # Otherwise, it's a list of candidates.
        candidates = self.get_candidates(target_state)
        return self.get_matches(target_state, candidates, search_string)

    def get_candidates(self, target_state: TargetState) -> list[DropdownItem]:
        """Get the candidates to match against."""
        candidates = self.candidates
        return candidates(target_state) if callable(candidates) else candidates

    def get_matches(
        self,
        target_state: TargetState,
        candidates: list[DropdownItem],
        search_string: str,
    ) -> list[DropdownItem]:
        """Given the state of the target widget, return the DropdownItems
        which match the query string and should be appear in the dropdown.

        Args:
            target_state: The state of the target widget.
            candidates: The candidates to match against.

        Returns:
            The matches to display in the dropdown.
        """
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
