from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Callable, ClassVar, Mapping

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.style import Style
from rich.table import Table
from rich.text import Text, TextType
from textual import events
from textual.app import ComposeResult
from textual.reactive import watch
from textual.widget import Widget
from textual.widgets import Input


class DropdownRender:
    def __init__(
        self,
        filter: str,
        matches: Iterable[DropdownItem],
        cursor_index: int,
        component_styles: Mapping[str, Style],
    ) -> None:
        self.filter = filter
        self.matches = matches
        self.cursor_index = cursor_index
        self.component_styles = component_styles

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        get_style = self.component_styles.get
        table = Table.grid(expand=True)
        table.add_column("left_meta", justify="left", style=get_style("left-column"))
        table.add_column("main", style=get_style("main-column"))
        table.add_column("right_meta", justify="right", style=get_style("right-column"))

        add_row = table.add_row
        for match in self.matches:
            main_text = match.main
            if self.filter != "":
                highlight_style = self.component_styles["highlight-match"]
                if match.highlight_ranges is not None:
                    # If the user has supplied their own ranges to highlight
                    for start, end in match.highlight_ranges:
                        main_text.stylize(highlight_style, start, end)
                else:
                    # Otherwise, by default, we highlight case-insensitive substrings
                    main_text.highlight_words(
                        [self.filter],
                        highlight_style,
                        case_sensitive=False,
                    )

            add_row(match.left_meta, match.main, match.right_meta)

        yield table


@dataclass
class DropdownItem:
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

    left_meta: TextType = ""
    main: TextType = ""
    right_meta: TextType = ""
    highlight_ranges: Iterable[tuple[int, int]] | None = None

    def __post_init__(self):
        if isinstance(self.left_meta, str):
            self.left_meta = Text(self.left_meta)
        if isinstance(self.main, str):
            self.main = Text(self.main)
        if isinstance(self.right_meta, str):
            self.right_meta = Text(self.right_meta)


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
    max-width: 1fr;
    scrollbar-size-vertical: 1;
}

Dropdown .autocomplete--highlight-match {
    color: $accent-lighten-2;
    text-style: bold;
}
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "autocomplete--cursor",
        "autocomplete--highlight-match",
        "autocomplete--left-column",
        "autocomplete--main-column",
        "autocomplete--right-column",
    }

    def __init__(
        self,
        results: list[DropdownItem] | Callable[[str, int], list[DropdownItem]],
        id: str | None = None,
        classes: str | None = None,
    ):
        """Construct an Autocomplete. Autocomplete only works if your Screen has a dedicated layer
        called `textual-autocomplete`.

        Args:
            results: A list of dropdown items, or a function to call to retrieve the list
                of dropdown items for the current input value and cursor position.
                Function takes the current input value and cursor position as arguments, and returns a list of
                `DropdownItem` which will be displayed in the dropdown list.
            id: The ID of the widget, allowing you to directly refer to it using CSS and queries.
            classes: The classes of this widget, a space separated string.
        """
        super().__init__(
            id=id,
            classes=classes,
        )
        self._results = results
        self._matches: list[DropdownItem] = []

    def compose(self) -> ComposeResult:
        yield AutoCompleteChild(
            self.input_widget,
            self._results,
        )

    def on_mount(self, event: events.Mount) -> None:
        screen_layers = list(self.screen.styles.layers)
        if not "textual-autocomplete" in screen_layers:
            screen_layers.append("textual-autocomplete")
        self.screen.styles.layers = tuple(screen_layers)


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
        linked_input: Input,
        items: list[DropdownItem] | Callable[[str, int], list[DropdownItem]],
        # TODO: Support awaitable and add debounce.
    ):
        """Construct an Autocomplete. Autocomplete only works if your Screen has a dedicated layer
        called `textual-autocomplete`.

        Args:
            linked_input: A reference to the Input Widget to add autocomplete to, or a selector/query string
                identifying the Input Widget that should power this autocomplete.
            items: Function to call to retrieve the list of completion results for the current input value.
                Function takes the current input value and cursor position as arguments, and returns a list of
                `AutoCompleteOption` which will be displayed as a dropdown list.
        """
        super().__init__()
        self.items = items
        self._matches: list[DropdownItem] = []
        self.linked_input = linked_input

    def on_mount(self, event: events.Mount) -> None:
        # Configure the watch methods - we want to subscribe to a couple of the
        # reactives inside the Input so that we can react accordingly.
        # TODO: Error cases - Handle case where reference to input widget no
        #  longer exists, for example
        watch(
            self.linked_input,
            attribute_name="value",
            callback=self._input_value_changed,
        )

        # TODO - this watcher wasn't firing, potential Textual issue.
        # watch(
        #     self.linked_input,
        #     attribute_name="cursor_position",
        #     callback=self._input_cursor_position_changed,
        # )

        self._sync_state(self.linked_input.value, self.linked_input.cursor_position)

    def render(self) -> RenderableType:
        assert self.linked_input is not None, "input_widget set in on_mount"
        parent_component = self.parent.get_component_rich_style
        component_styles = {
            "cursor": parent_component("autocomplete--cursor"),
            "highlight-match": parent_component("autocomplete--highlight-match"),
            "left-column": parent_component("autocomplete--left-column"),
            "main-column": parent_component("autocomplete--main-column"),
            "right-column": parent_component("autocomplete--right-column"),
        }
        return DropdownRender(
            filter=self.linked_input.value,
            matches=self._matches,
            cursor_index=0,
            component_styles=component_styles,
        )

    def _input_cursor_position_changed(self, cursor_position: int) -> None:
        assert self.linked_input is not None, "input_widget set in on_mount"
        self._sync_state(self.linked_input.value, cursor_position)

    def _input_value_changed(self, value: str) -> None:
        assert self.linked_input is not None, "input_widget set in on_mount"
        self._sync_state(value, self.linked_input.cursor_position)

    def _sync_state(self, value: str, cursor_position: int) -> None:
        if callable(self.items):
            self._matches = self.items(value, cursor_position)
        else:
            self._matches = [
                DropdownItem(
                    left_meta=item.left_meta.copy(),
                    main=item.main.copy(),
                    right_meta=item.right_meta.copy(),
                )
                for item in self.items
                if value.lower() in item.main.plain.lower()
            ]
        self.parent.display = len(self._matches) > 0 and value != ""

        top, right, bottom, left = self.parent.styles.margin
        x, y, width, height = self.linked_input.content_region
        line_below_cursor = y + 1

        cursor_screen_position = x + (
            cursor_position - self.linked_input.view_position
        )
        self.parent.styles.margin = (
            line_below_cursor,
            right,
            bottom,
            cursor_screen_position,
        )

        self.refresh()
