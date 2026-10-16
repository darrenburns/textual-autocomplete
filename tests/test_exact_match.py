from __future__ import annotations

import pytest
from textual.app import App, ComposeResult
from textual.content import Content
from textual.widgets import Input

from textual_autocomplete import AutoComplete, DropdownItem


@pytest.mark.parametrize("prefix", [None, "1 ", Content.from_markup("[bold]1 [/bold]")])
async def test_exact_match_with_display_only_prefix_stays_hidden(prefix):
    class Languages(App[None]):
        def compose(self) -> ComposeResult:
            target = Input()
            yield target
            yield AutoComplete(
                target,
                candidates=[DropdownItem("Python", prefix=prefix)],
            )

    app = Languages()
    async with app.run_test() as pilot:
        await pilot.press(*"Python")
        autocomplete = app.query_one(AutoComplete)
        assert not autocomplete.display

        await pilot.press("down")
        assert not autocomplete.display


@pytest.mark.parametrize("prefix", ["1 ", Content.from_markup("[bold]1 [/bold]")])
async def test_completed_value_with_prefix_cannot_be_resummoned(prefix):
    class Languages(App[None]):
        def compose(self) -> ComposeResult:
            target = Input()
            yield target
            yield AutoComplete(
                target,
                candidates=[DropdownItem("Python", prefix=prefix)],
            )

    app = Languages()
    async with app.run_test() as pilot:
        await pilot.press("p", "enter")
        assert app.query_one(Input).value == "Python"
        autocomplete = app.query_one(AutoComplete)
        assert not autocomplete.display

        await pilot.press("down")
        assert not autocomplete.display
