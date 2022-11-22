from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Callable

from rich import Console
from rich.console import ConsoleOptions, RenderableType
from rich.text import Text
from textual import events
from textual.app import ComposeResult
from textual.css.styles import RenderStyles
from textual.reactive import watch
from textual.widget import Widget
from textual.widgets import Input


class AutocompleteError(Exception):
    pass


class DropdownRender:
    def __init__(
        self,
        filter: str,
        matches: Iterable[CompletionCandidate],
        highlight_index: int,
        component_styles: dict[str, RenderStyles],
    ) -> None:
        self.filter = filter
        self.matches = matches
        self.highlight_index = highlight_index
        self.component_styles = component_styles
        self._highlight_item_style = self.component_styles.get(
            "search-completion--selected-item"
        ).rich_style

    def __rich_console__(self, console: Console, options: ConsoleOptions):
        matches = []
        for index, match in enumerate(self.matches):
            if not match.secondary:
                secondary_text = self._find_secondary_text(match.original_object)
            else:
                secondary_text = match.secondary
            match = Text.from_markup(
                f"{match.primary:<{options.max_width - 3}}[dim]{secondary_text}"
            )
            matches.append(match)
            if self.highlight_index == index:
                match.stylize(self._highlight_item_style)
            match.highlight_regex(self.filter, style="black on #4EBF71")

        return Text("\n").join(matches)


@dataclass
class AutocompleteOption:
    """A single option appearing in the autocompletion dropdown. Each option has up to 3 columns.

    Args:
        left: The left column will often contain an icon/symbol, the main (middle)
            column contains the text that represents this option.
        main: The main text representing this option - this will be highlighted by default.
            In an IDE, the `main` (middle) column might contain the name of a function or method.
        right: The text appearing in the right column of the dropdown.
            The right column often contains some metadata relating to this option.

    """
    left: str = ""
    main: str = ""
    right: str = ""


class Autocomplete(Widget):
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
        get_results: Callable[[str, int], list[AutocompleteOption]],
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

        if isinstance(linked_input, str):
            # If the user supplied a selector, find the Input to subscribe to
            self._input_widget = self.app.query_one(linked_input)
        else:
            self._input_widget = linked_input

        super().__init__(
            linked_input,
            id=id,
            classes=classes,
        )
        self._get_results = get_results

        # Configure the watch methods - we want to subscribe to a couple of the reactives inside the Input
        # so that we can react accordingly.
        # TODO: Error cases - Handle case where reference to input widget no longer exists for example
        watch(self._input_widget, attribute_name="cursor_position", callback=self._input_cursor_position_changed)
        watch(self._input_widget, attribute_name="value", callback=self._input_value_changed)

    def on_mount(self, event: events.Mount) -> None:
        # A quick sanity check - make sure we have the appropriate layer available
        # TODO - think about whether it makes sense to enforce this.
        if "textual-autocomplete" not in self.screen.layers:
            raise AutocompleteError(
                "Screen must have a layer called `textual-autocomplete`."
            )

    def _input_cursor_position_changed(self) -> None:
        return

    def _input_value_changed(self) -> None:
        return



