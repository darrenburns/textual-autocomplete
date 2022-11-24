from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Callable, ClassVar, Mapping, cast

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.style import Style
from rich.table import Table
from rich.text import Text
from textual import events
from textual.app import ComposeResult
from textual.reactive import watch
from textual.widget import Widget
from textual.widgets import Input


class AutoCompleteError(Exception):
    pass


class DropdownRender:
    def __init__(
        self,
        filter: str,
        matches: Iterable[Candidate],
        highlight_index: int,
        component_styles: Mapping[str, Style],
    ) -> None:
        self.filter = filter
        self.matches = matches
        self.highlight_index = highlight_index
        self.component_styles = component_styles

    @property
    def _table(self) -> Table:
        table = Table.grid(expand=True)
        table.add_column("left_meta", justify="left")
        table.add_column("main")
        table.add_column("right_meta", justify="right")

        for match in self.matches:
            if self.filter != "":
                match.main.highlight_words(
                    [self.filter],
                    style=self.component_styles["substring-match"],
                    case_sensitive=False,
                )

            table.add_row(match.left_meta, match.main, match.right_meta)

        return table

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield self._table


@dataclass
class Candidate:
    """A single option appearing in the autocompletion dropdown. Each option has up to 3 columns.
    Note that this is not a widget, it's simply a data structure for describing dropdown items.

    Args:
        left: The left column will often contain an icon/symbol, the main (middle)
            column contains the text that represents this option.
        main: The main text representing this option - this will be highlighted by default.
            In an IDE, the `main` (middle) column might contain the name of a function or method.
        right: The text appearing in the right column of the dropdown.
            The right column often contains some metadata relating to this option.
        highlight_ranges: Custom ranges to highlight. By default the value is None,
            meaning textual-autocomplete will highlight substrings in the dropdown.
            That is, if the value you've typed into the Input is a substring of the candidates
            `main` attribute, then that substring will be highlighted. If you supply your own
            implementation of get_results which uses a more complex process to decide what to
            display in the dropdown, then you can customise the highlighting of the returned
            candidates by supplying index ranges to highlight.

    """

    left_meta: Text = ""
    main: Text = ""
    right_meta: Text = ""
    highlight_ranges: Iterable[tuple[int, int]] | None = None


class AutoComplete(Widget):

    DEFAULT_CSS = """\
AutoComplete {
    height: auto;
    align-horizontal: center;
}
    """

    def __init__(
        self,
        input: Input,
        dropdown: Dropdown,
        id: str | None = None,
        classes: str | None = None,
    ):
        super().__init__(id=id, classes=classes)
        self.input = input
        self.dropdown = dropdown

    def compose(self) -> ComposeResult:
        yield self.input

    def on_mount(self, event: events.Mount) -> None:
        self.dropdown.input_widget = self.input
        self.screen.mount(self.dropdown)

    def on_key(self, event: events.Key) -> None:
        print(f"KEY === {event.key}")

class Dropdown(Widget):
    DEFAULT_CSS = """\
Dropdown {
    layer: textual-autocomplete;
    /* to prevent parent `align` confusing things, we dock to remove from flow */
    dock: top;
    display: none;
    overflow: hidden auto;
    background: $panel-lighten-1;
    height: auto;
    max-height: 12;
    width: auto;
    scrollbar-size-vertical: 1;
}
    """

    # TODO: Add component classes for each column.
    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "autocomplete--highlight",
        "autocomplete--substring-match",
    }

    def __init__(
        self,
        get_results: Callable[[str, int], list[Candidate]],
        track_cursor: bool = True,
        id: str | None = None,
        classes: str | None = None,
    ):
        """Construct an Autocomplete. Autocomplete only works if your Screen has a dedicated layer
        called `textual-autocomplete`.

        Args:
            linked_input: A reference to the Input Widget to add autocomplete to, or a selector/query string
                identifying the Input Widget that should power this autocomplete.
            get_results: Function to call to retrieve the list of completion results for the current input value.
                Function takes the current input value and cursor position as arguments, and returns a list of
                `AutoCompleteOption` which will be displayed as a dropdown list.
            track_cursor: If True, the autocomplete dropdown will follow the cursor position.
            id: The ID of the widget, allowing you to directly refer to it using CSS and queries.
            classes: The classes of this widget, a space separated string.
        """
        super().__init__(
            id=id,
            classes=classes,
        )
        self._get_results = get_results
        self._matches: list[Candidate] = []
        self.track_cursor = track_cursor

    def compose(self) -> ComposeResult:
        yield AutoCompleteChild(
            self.input_widget,
            self._get_results,
            self.track_cursor,
        )


class AutoCompleteChild(Widget):
    """An autocompletion dropdown widget. This widget gets linked to an Input widget, and is automatically
    updated based on the state of that Input."""

    DEFAULT_CSS = """\
AutoCompleteChild {
    height: auto;
}
    """

    def __init__(
        self,
        linked_input: Input | str,
        get_results: Callable[[str, int], list[Candidate]],
        # TODO: Support awaitable and add debounce.
        track_cursor: bool = True,
    ):
        """Construct an Autocomplete. Autocomplete only works if your Screen has a dedicated layer
        called `textual-autocomplete`.

        Args:
            linked_input: A reference to the Input Widget to add autocomplete to, or a selector/query string
                identifying the Input Widget that should power this autocomplete.
            get_results: Function to call to retrieve the list of completion results for the current input value.
                Function takes the current input value and cursor position as arguments, and returns a list of
                `AutoCompleteOption` which will be displayed as a dropdown list.
            track_cursor: If True, the autocomplete dropdown will follow the cursor position.
        """
        super().__init__()
        self._get_results = get_results
        self._matches: list[Candidate] = []
        self._input_widget: Input | None = None
        self.linked_input = linked_input
        self.track_cursor = track_cursor

        # Rich style information - these are actually component classes
        # on the parent wrapper container to make things more convenient.
        self._substring_match_style: Style | None = None
        self._highlight_style: Style | None = None

    def on_mount(self, event: events.Mount) -> None:
        # Ensure we have a reference to the Input widget we're subscribing to
        if isinstance(self.linked_input, str):
            self._input_widget = self.app.query_one(self.linked_input, Input)
        else:
            self._input_widget = self.linked_input

        # A quick sanity check - make sure we have the appropriate layer available
        # TODO - think about whether it makes sense to enforce this.
        if "textual-autocomplete" not in self.screen.layers:
            raise AutoCompleteError(
                "Screen must have a layer called `textual-autocomplete`."
            )

        # Configure the watch methods - we want to subscribe to a couple of the
        # reactives inside the Input so that we can react accordingly.
        # TODO: Error cases - Handle case where reference to input widget no
        #  longer exists, for example
        watch(
            self._input_widget,
            attribute_name="value",
            callback=self._input_value_changed,
        )
        watch(
            self._input_widget,
            attribute_name="cursor_position",
            callback=self._input_cursor_position_changed,
        )

        self._sync_state(self._input_widget.value, self._input_widget.cursor_position)

    def render(self) -> RenderableType:
        assert self._input_widget is not None, "input_widget set in on_mount"
        parent_component = self.parent.get_component_rich_style
        return DropdownRender(
            filter=self._input_widget.value,
            matches=self._matches,
            highlight_index=0,
            component_styles={
                "highlight": parent_component("autocomplete--highlight"),
                "substring-match": parent_component("autocomplete--substring-match"),
            },
        )

    def _input_cursor_position_changed(self, cursor_position: int) -> None:
        assert self._input_widget is not None, "input_widget set in on_mount"
        print("cursor changed")
        self._sync_state(self._input_widget.value, cursor_position)

    def _input_value_changed(self, value: str) -> None:
        assert self._input_widget is not None, "input_widget set in on_mount"
        print("value changed")
        self._sync_state(value, self._input_widget.cursor_position)

    def _sync_state(self, value: str, cursor_position: int) -> None:
        print("syncing state!!")
        self._matches = self._get_results(value, cursor_position)
        self.parent.display = len(self._matches) > 0 and value != ""

        top, right, bottom, left = self.parent.styles.margin
        x, y, width, height = self._input_widget.content_region
        line_below_cursor = y + 1

        cursor_screen_position = x + (
            cursor_position - self._input_widget.view_position
        )
        self.parent.styles.margin = (
            line_below_cursor,
            right,
            bottom,
            cursor_screen_position,
        )

        self.refresh()
