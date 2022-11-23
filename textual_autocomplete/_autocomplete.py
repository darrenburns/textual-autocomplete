from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from typing import Iterable, Callable

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.measure import Measurement
from rich.text import Text
from textual import events
from textual.app import ComposeResult
from textual.css.styles import RenderStyles
from textual.reactive import watch
from textual.widget import Widget
from textual.widgets import Input


class AutoCompleteError(Exception):
    pass


class DropdownItem:
    def __init__(
        self,
        left_meta: Text,
        main: Text,
        right_meta: Text,
        filter: str = "",
    ):
        self.left_meta = left_meta
        self.main = main
        self.right_meta = right_meta
        self.filter = filter

    @property
    def renderable(self):
        if self.filter != "":
            self.main.highlight_words([self.filter], style="on red")

        columns = []
        if self.left_meta:
            columns.append(self.left_meta)
        if self.main:
            columns.append(self.main)
        if self.right_meta:
            columns.append(self.right_meta)

        return Text(" ").join(columns)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield self.renderable

    def __rich_measure__(
        self, console: Console, options: ConsoleOptions
    ) -> Measurement:
        measurement = Measurement.get(console, options, self.renderable)
        print(measurement)
        return measurement


class DropdownRender:
    def __init__(
        self,
        filter: str,
        matches: Iterable[Candidate],
        highlight_index: int,
        component_styles: dict[str, RenderStyles],
    ) -> None:
        self.filter = filter
        self.matches = matches
        self.highlight_index = highlight_index

    @property
    def item_renderables(self) -> list[DropdownItem]:
        return [
            DropdownItem(
                match.left_meta, match.main, match.right_meta, filter=self.filter
            )
            for match in self.matches
        ]

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield from self.item_renderables

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        get = partial(Measurement.get, console, options)
        minimum = 0
        maximum = 0
        for item in self.item_renderables:
            item_min, item_max = get(item)
            minimum = max(item_min, minimum)
            maximum = max(item_max, maximum)

        return Measurement(minimum, maximum)


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
    overflow: hidden auto;
    height: 1;
    width: auto;
}
    """

    def __init__(
        self,
        linked_input: Input | str,
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
        self._input_widget: Input | None = None
        self.linked_input = linked_input
        self.track_cursor = track_cursor

    def compose(self) -> ComposeResult:
        yield AutoCompleteChild(
            self.linked_input,
            self._get_results,
            self.track_cursor,
        )


class AutoCompleteChild(Widget):
    """An autocompletion dropdown widget. This widget gets linked to an Input widget, and is automatically
    updated based on the state of that Input."""

    DEFAULT_CSS = """\
AutoCompleteChild {
    layer: textual-autocomplete;
    display: none;
    margin-top: 3;
    background: $panel;
    width: auto;
    height: auto;
}
    """

    def __init__(
        self,
        linked_input: Input | str,
        get_results: Callable[[str, int], list[Candidate]],
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
            attribute_name="cursor_position",
            callback=self._input_cursor_position_changed,
        )
        watch(
            self._input_widget,
            attribute_name="value",
            callback=self._input_value_changed,
        )

        self._sync_state(self._input_widget.value, self._input_widget.cursor_position)

    def render(self) -> RenderableType:
        assert self._input_widget is not None, "input_widget set in on_mount"
        return DropdownRender(
            filter=self._input_widget.value,
            matches=self._matches,
            highlight_index=0,
            component_styles={},
        )

    def _input_cursor_position_changed(self, cursor_position: int) -> None:
        assert self._input_widget is not None, "input_widget set in on_mount"
        self._sync_state(self._input_widget.value, cursor_position)

    def _input_value_changed(self, value: str) -> None:
        assert self._input_widget is not None, "input_widget set in on_mount"
        self._sync_state(value, self._input_widget.cursor_position)

    def _sync_state(self, value: str, cursor_position: int) -> None:
        self._matches = self._get_results(value, cursor_position)
        self.display = len(self._matches) > 0 and value != ""
        self.refresh()
