from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Callable

from rich.console import Console, ConsoleOptions, RenderableType
from rich.text import Text
from textual import events
from textual.css.styles import RenderStyles
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
        component_styles: dict[str, RenderStyles],
    ) -> None:
        self.filter = filter
        self.matches = matches
        self.highlight_index = highlight_index

    def __rich_console__(self, console: Console, options: ConsoleOptions):
        matches = []
        for match in self.matches:
            candidate_text = Text(match.main)
            candidate_text.highlight_words([self.filter], style="on yellow")
            matches.append(candidate_text)
        return Text("\n").join(matches)


@dataclass
class Candidate:
    """A single option appearing in the autocompletion dropdown. Each option has up to 3 columns.

    Args:
        left: The left column will often contain an icon/symbol, the main (middle)
            column contains the text that represents this option.
        main: The main text representing this option - this will be highlighted by default.
            In an IDE, the `main` (middle) column might contain the name of a function or method.
        right: The text appearing in the right column of the dropdown.
            The right column often contains some metadata relating to this option.

    """
    main: str = ""
    left_meta: str = ""
    right_meta: str = ""


class AutoComplete(Widget):
    """An autocompletion dropdown widget. This widget gets linked to an Input widget, and is automatically
    updated based on the state of that Input."""

    DEFAULT_CSS = """\
Autocomplete {
    layer: textual-autocomplete; 
}
    """

    def __init__(
        self,
        linked_input: Input | str,
        get_results: Callable[[str, int], Iterable[Candidate]],
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
            id: The ID of the widget, allowing you to directly refer to it using CSS and queries.
            classes: The classes of this widget, a space separated string.
        """

        super().__init__(
            id=id,
            classes=classes,
        )
        self._get_results = get_results
        self._linked_input = linked_input
        self._candidates = []

    def on_mount(self, event: events.Mount) -> None:
        # Ensure we have a reference to the Input widget we're subscribing to
        if isinstance(self._linked_input, str):
            self._input_widget: Input = self.app.query_one(self._linked_input, Input)
        else:
            self._input_widget: Input = self._linked_input

        # A quick sanity check - make sure we have the appropriate layer available
        # TODO - think about whether it makes sense to enforce this.
        if "textual-autocomplete" not in self.screen.layers:
            raise AutoCompleteError(
                "Screen must have a layer called `textual-autocomplete`."
            )

        # Configure the watch methods - we want to subscribe to a couple of the reactives inside the Input
        # so that we can react accordingly.
        # TODO: Error cases - Handle case where reference to input widget no longer exists for example
        watch(self._input_widget, attribute_name="cursor_position", callback=self._input_cursor_position_changed)
        watch(self._input_widget, attribute_name="value", callback=self._input_value_changed)

    def render(self) -> RenderableType:
        matches = [match for match in self._candidates]
        return DropdownRender(
            filter=self._input_widget.value,
            matches=matches,
            highlight_index=0,
            component_styles={},
        )

    def _input_cursor_position_changed(self, cursor_position: int) -> None:
        self._candidates = self._get_results(self._input_widget.value, cursor_position)
        self.refresh()

    def _input_value_changed(self, value: str) -> None:
        self._candidates = self._get_results(value, self._input_widget.cursor_position)
        self.refresh()
