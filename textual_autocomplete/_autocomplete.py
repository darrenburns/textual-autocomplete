from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from typing import Iterable, ClassVar, Mapping, cast

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.style import Style
from rich.table import Table
from rich.text import Text, TextType
from textual import events
from textual._types import MessageTarget
from textual.app import ComposeResult
from textual.geometry import Size, Region
from textual.message import Message
from textual.reactive import watch
from textual.widget import Widget
from textual.widgets import Input


class DropdownRender:
    def __init__(
        self,
        filter: str,
        matches: list[DropdownItem],
        selected_index: int,
        component_styles: Mapping[str, Style],
    ) -> None:
        self.filter = filter
        self.matches = matches
        self.selection_cursor_index = selected_index
        self.component_styles = component_styles

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        get_style = self.component_styles.get
        table = Table.grid(expand=True)

        if self.matches:
            if self.matches[0].left_meta:
                table.add_column(
                    "left_meta", justify="left", style=get_style("left-column")
                )
            if self.matches[0].main:
                table.add_column("main", style=get_style("main-column"))
            if self.matches[0].right_meta:
                table.add_column(
                    "right_meta", justify="right", style=get_style("right-column")
                )

        add_row = table.add_row
        for index, match in enumerate(self.matches):
            main_text = cast(Text, match.main)
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

            # If the cursor is on this row, highlight it
            additional_row_style = Style.null()
            if index == self.selection_cursor_index:
                additional_row_style = self.component_styles["selection-cursor"]

            row_items = []
            if match.left_meta:
                row_items.append(match.left_meta)
            if match.main:
                row_items.append(match.main)
            if match.right_meta:
                row_items.append(match.right_meta)

            add_row(
                *row_items,
                style=additional_row_style,
            )

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
        highlight_ranges: Custom ranges to highlight. By default, the value is None,
            meaning textual-autocomplete will highlight substrings in the dropdown.
            That is, if the value you've typed into the Input is a substring of the candidates
            `main` attribute, then that substring will be highlighted. If you supply your own
            implementation of `items` which uses a more complex process to decide what to
            display in the dropdown, then you can customise the highlighting of the returned
            candidates by supplying index ranges to highlight.

    """

    main: TextType = ""
    left_meta: TextType = ""
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
        *,
        id: str | None = None,
        classes: str | None = None,
    ):
        """Coordinates between a Textual Input and a Dropdown widget,
        ensuring the Dropdown is fed with data from the Input and displayed
        in the correct location at the appropriate times.

        Args:
            input: The input widget that you want to power the dropdown.
            dropdown: The dropdown widget. This will be populated by AutoComplete.
        """
        super().__init__(id=id, classes=classes)
        self.input = input
        self.dropdown = dropdown
        self.dropdown.input_widget = self.input

    def compose(self) -> ComposeResult:
        yield self.input

    def on_mount(self, event: events.Mount) -> None:
        self.screen.mount(self.dropdown)

    def on_descendant_blur(self, event: events.DescendantBlur) -> None:
        self.dropdown.display = False

    def on_key(self, event: events.Key) -> None:
        key = event.key
        if key == "down":
            self.dropdown.cursor_down()
        elif key == "up":
            self.dropdown.cursor_up()
        elif key == "escape":
            self.dropdown.close()
        elif key == "tab":
            self._select_item()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._select_item()

    def _select_item(self):
        selected = self.dropdown.selected_item
        if self.dropdown.display and selected is not None:
            self.input.value = ""
            self.input.insert_text_at_cursor(selected.main.plain)
            self.dropdown.display = False
            self.emit_no_wait(self.Selected(self, item=self.dropdown.selected_item))

    class Selected(Message):
        def __init__(self, sender: MessageTarget, item: DropdownItem):
            super().__init__(sender)
            self.item = item


class Dropdown(Widget):
    DEFAULT_CSS = """\
Dropdown {
    layer: textual-autocomplete;
    /* to prevent parent `align` confusing things, we dock to remove from flow */
    dock: top;
    display: none;
    overflow: hidden auto;
    background: $panel-lighten-1;
    width: auto;
    height: auto;
    max-height: 12;
    max-width: 1fr;
    scrollbar-size-vertical: 1;
}

Dropdown .autocomplete--highlight-match {
    color: $accent-lighten-2;
    text-style: bold;
}

Dropdown .autocomplete--selection-cursor {
    background: $boost 8%;
}
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "autocomplete--selection-cursor",
        "autocomplete--highlight-match",
        "autocomplete--left-column",
        "autocomplete--main-column",
        "autocomplete--right-column",
    }

    def __init__(
        self,
        items: list[DropdownItem] | Callable[[str, int], list[DropdownItem]],
        # edge: Whether the dropdown should appear above or below.
        # edge: str = "bottom",  # Literal["top", "bottom"]
        # tracking: Whether the dropdown should follow the cursor or remain static.
        # tracking: str = "follow_cursor",  # Literal["follow_cursor", "static"]
        id: str | None = None,
        classes: str | None = None,
    ):
        """Construct an Autocomplete. Autocomplete only works if your Screen has a dedicated layer
        called `textual-autocomplete`.

        Args:
            items: A list of dropdown items, or a function to call to retrieve the list
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
        # self._edge = edge
        # self._tracking = tracking
        self.items = items
        self.input_widget: Input

    def compose(self) -> ComposeResult:
        self.child = DropdownChild(self.input_widget)
        yield self.child

    def on_mount(self, event: events.Mount) -> None:
        screen_layers = list(self.screen.styles.layers)
        if not "textual-autocomplete" in screen_layers:
            screen_layers.append("textual-autocomplete")

        # TODO: Ignoring type below because Textual is typed incorrectly here.
        #  Style property setter for layers has incorrect type.
        self.screen.styles.layers = tuple(screen_layers)  # type: ignore

        # TODO: Error cases - Handle case where reference to input widget no
        #  longer exists, for example

        watch(
            self.input_widget,
            attribute_name="value",
            callback=self._input_value_changed,
        )

        # TODO - this watcher wasn't firing, potential Textual issue.
        # watch(
        #     self.input_widget,
        #     attribute_name="cursor_position",
        #     callback=self._input_cursor_position_changed,
        # )

        # TODO: Having to use scroll_target here because scroll_y doesn't fire.
        #  Will also probably need separate callbacks for x and y.
        watch(
            self.screen,
            attribute_name="scroll_target_y",
            callback=self.handle_screen_scroll,
        )

        if self.input_widget is not None:
            self.sync_state(self.input_widget.value, self.input_widget.cursor_position)

    def cursor_up(self) -> None:
        if not self.display:
            self.display = True
        else:
            self.child.selected_index -= 1

    def cursor_down(self) -> None:
        if not self.display:
            self.display = True
        else:
            self.child.selected_index += 1

    def cursor_home(self) -> None:
        self.child.selected_index = 0

    def close(self) -> None:
        if self.display:
            self.display = False

    @property
    def selected_item(self) -> DropdownItem | None:
        return self.child.selected_item

    def _input_cursor_position_changed(self, cursor_position: int) -> None:
        if self.input_widget is not None:
            self.sync_state(self.input_widget.value, cursor_position)

    def _input_value_changed(self, value: str) -> None:
        if self.input_widget is not None:
            self.sync_state(value, self.input_widget.cursor_position)

    def sync_state(self, value: str, input_cursor_position: int) -> None:
        if callable(self.items):
            matches = self.items(value, input_cursor_position)
        else:
            matches = []
            for item in self.items:
                # Casting to Text, since we convert to Text object in
                # the __post_init__ of DropdownItem.
                text = cast(Text, item.main)
                if value.lower() in text.plain.lower():
                    matches.append(
                        DropdownItem(
                            left_meta=cast(Text, item.left_meta).copy(),
                            main=cast(Text, item.main).copy(),
                            right_meta=cast(Text, item.right_meta).copy(),
                        )
                    )

            matches = sorted(
                matches,
                key=lambda match: not cast(Text, match.main)
                .plain.lower()
                .startswith(value.lower()),
            )

        self.child.matches = matches
        self.display = len(matches) > 0 and value != ""
        self.cursor_home()
        self.reposition(input_cursor_position)
        self.child.refresh()

    def handle_screen_scroll(self, old: float, new: float) -> None:
        self.reposition(scroll_target_adjust_y=int(old) - int(new))

    def reposition(
        self,
        input_cursor_position: int | None = None,
        scroll_target_adjust_y: int = 0,
    ) -> None:
        if self.input_widget is None:
            return

        if input_cursor_position is None:
            input_cursor_position = self.input_widget.cursor_position

        top, right, bottom, left = self.styles.margin
        x, y, width, height = self.input_widget.content_region
        line_below_cursor = y + 1 + scroll_target_adjust_y

        cursor_screen_position = x + (
            input_cursor_position - self.input_widget.view_position
        )
        self.styles.margin = (
            line_below_cursor,
            right,
            bottom,
            cursor_screen_position,
        )


class DropdownChild(Widget):
    """An autocompletion dropdown widget. This widget gets linked to an Input widget, and is automatically
    updated based on the state of that Input."""

    DEFAULT_CSS = """\
DropdownChild {
    height: auto;
}
    """

    # TODO: Support awaitable and add debounce.
    def __init__(self, linked_input: Input):
        """Construct an Autocomplete. Autocomplete only works if your Screen has a dedicated layer
        called `textual-autocomplete`.

        Args:
            linked_input: A reference to the Input Widget to add autocomplete to, or a selector/query string
                identifying the Input Widget that should power this autocomplete.
        """
        super().__init__()
        self.matches: list[DropdownItem] = []
        self.linked_input = linked_input
        self._selected_index: int = 0

    @property
    def parent(self) -> Dropdown:
        assert isinstance(self._parent, Dropdown)
        return self._parent

    def render(self) -> RenderableType:
        assert self.linked_input is not None, "input_widget set in on_mount"
        parent_component = self.parent.get_component_rich_style
        component_styles = {
            "selection-cursor": parent_component("autocomplete--selection-cursor"),
            "highlight-match": parent_component("autocomplete--highlight-match"),
            "left-column": parent_component("autocomplete--left-column"),
            "main-column": parent_component("autocomplete--main-column"),
            "right-column": parent_component("autocomplete--right-column"),
        }
        return DropdownRender(
            filter=self.linked_input.value,
            matches=self.matches,
            selected_index=self.selected_index,
            component_styles=component_styles,
        )

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        return len(self.matches)

    @property
    def selected_item(self) -> DropdownItem | None:
        selected_index = self._selected_index
        if not self.matches or not 0 <= selected_index < len(self.matches):
            return None
        return self.matches[selected_index]

    @property
    def selected_index(self) -> int:
        return self._selected_index

    @selected_index.setter
    def selected_index(self, value: int) -> None:
        self._selected_index = value % max(len(self.matches), 1)
        # It's easier to just ask our parent to scroll here rather
        # than having to make sure we do it in the parent each time we
        # update the index. We always appear under the same parent anyway.
        region = Region(
            x=self.virtual_region.x,
            y=self.virtual_region.y + self._selected_index,
            height=1,
            width=1,
        )
        self.parent.scroll_to_region(region=region, animate=False)
        self.refresh()
