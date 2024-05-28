from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.geometry import Region
from textual.widget import Widget
from textual.widgets import Input, TextArea, OptionList
from textual.widgets.option_list import Option
from textual.widgets.text_area import Selection

from textual_autocomplete import CompletionStrategy, DropdownItem


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
        self, left: str, id: str | None = None, disabled: bool = False
    ) -> None:
        super().__init__(prompt, id, disabled)


class AutoComplete(Widget):
    BINDINGS = [
        Binding("escape", "hide", "Hide dropdown", show=False),
    ]

    DEFAULT_CSS = """\
    AutoComplete {
        layer: textual-autocomplete;
        height: auto;
        width: auto;
        max-height: 12;
        scrollbar-size-vertical: 1;
        padding: 0;
        margin: 0;
        border: none;

        & .autocomplete--highlight-match {
            color: $accent-lighten-2;
            text-style: bold;
        }

        & .autocomplete--selection-cursor {
            background: $boost;
        }

        & OptionList {
            width: auto;
            height: auto;
            border: none;
            padding: 0;
            margin: 0;
            &:focus {
               border: none;
                padding: 0;
                margin: 0;
            }
        }
    }
    """

    def __init__(
        self,
        target: Input | TextArea | str,
        items: list[DropdownItem] | Callable[[TargetState], list[DropdownItem]],
        on_tab: Callable[[TargetState], None] | None = None,
        on_enter: Callable[[TargetState], None] | None = None,
        completion_strategy: CompletionStrategy = "replace",
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
        self.on_tab = on_tab
        self.on_enter = on_enter
        self.completion_strategy = completion_strategy
        self.items = items

    def compose(self) -> ComposeResult:
        option_list = OptionList(*["one", "two", "three"])
        option_list.can_focus = False
        yield option_list

    async def on_mount(self) -> None:
        # Subscribe to the target widget's reactive attributes.

        await self.target._mounted_event.wait()  # TODO - timeout this wait
        self.target.message_signal.subscribe(self, self._hijack_keypress)
        self._subscribe_to_target()
        self._align_to_target()

        # TODO - we probably need a means of checking if the screen offset
        # of the target widget has changed at all.
        # self.watch(
        #     self.screen,
        #     attribute_name="scroll_target_x",
        #     callback=lambda: 1,
        # )
        # self.watch(
        #     self.screen,
        #     attribute_name="scroll_target_y",
        #     callback=lambda: 1,
        # )

    def _hijack_keypress(self, event) -> None:
        """Hijack some keypress events of the target widget."""
        if isinstance(event, events.Key):
            if event.key == "down":
                # TODO - only hijack this if there are results.
                self.option_list.can_focus = True
                self.option_list.focus(scroll_visible=False)
            elif event.key == "escape":
                self.styles.display = "none"
                self.action_hide()

    def action_hide(self) -> None:
        self.styles.display = "none"
        if not self.target.has_focus:
            self.target.focus(scroll_visible=False)

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
        print("aligning to target...")
        cursor_x, cursor_y = self.target.cursor_screen_offset
        if (cursor_x, cursor_y) == (0, 0):
            cursor_x, cursor_y = self.target.content_region.offset

        dropdown = self.query_one(OptionList)
        width, height = dropdown.size
        x, y, _width, _height = Region(
            cursor_x,
            cursor_y + 1,
            width,
            height,
        ).translate_inside(self.screen.region)

        self.styles.offset = x, y
        print(self.target.size)

    def _unify_target_state(self) -> TargetState:
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
        state = self._unify_target_state()
        self._align_to_target()
        print(state)

    @property
    def option_list(self) -> OptionList:
        return self.query_one(OptionList)
