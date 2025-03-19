"""Let's ensure the `prevent_default_tab` and `prevent_default_enter` options work as expected."""

from __future__ import annotations

from typing import Any
from textual.app import App, ComposeResult
from textual.widgets import Button, Input
from textual_autocomplete import AutoComplete


class PreventDefaultTab(App[None]):
    """Test that the default tab key is permitted if `prevent_default_tab` is `False`."""

    def __init__(
        self, prevent_default_tab: bool = False, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.prevent_default_tab = prevent_default_tab

    def compose(self) -> ComposeResult:
        input = Input(placeholder="Type something...")
        yield input
        yield AutoComplete(
            input,
            candidates=["foo", "bar"],
            prevent_default_tab=self.prevent_default_tab,
        )
        yield Button("I'm here to test focus.")


async def test_switch_focus_on_completion_via_tab_key__prevent_default_tab_is_false():
    """The default tab key should not be prevented if `prevent_default_tab` is `False`."""
    app = PreventDefaultTab(prevent_default_tab=False)
    async with app.run_test() as pilot:
        await pilot.press("f", "tab")
        assert app.query_one(Input).value == "foo"
        assert app.query_one(Button).has_focus


async def test_no_focus_switch_via_tab_key__prevent_default_tab_is_true():
    """`prevent_default_tab` is `True`, so focus should switch on completion with tab."""
    app = PreventDefaultTab(prevent_default_tab=True)
    async with app.run_test() as pilot:
        await pilot.press("f", "tab")
        input_widget = app.query_one(Input)
        assert input_widget.value == "foo"
        assert input_widget.has_focus
        assert not app.query_one(Button).has_focus
