from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Center, VerticalScroll
from textual.pilot import Pilot
from textual.widgets import Input
from textual_autocomplete import AutoComplete


class CursorTracking(App[None]):
    CSS = """
    #scrollable {
        overflow: scroll scroll;
        scrollbar-color: red;
        Center {
            background: $accent;
            height: 100;
            width: 100;
            align-vertical: middle;
        }
        Input {
            width: 24;
        }
    }
    """

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="scrollable", can_focus=False):
            with Center():
                input = Input(placeholder="Type here...")
                input.cursor_blink = False
                yield input

        yield AutoComplete(
            target=input,
            candidates=["foo", "bar", "baz", "qux", "boop"],
        )


def test_dropdown_tracks_input_cursor_and_cursor_prefix_as_search_string(snap_compare):
    """The completions should be based on the text between the start of the input and the cursor location.

    In this example, we type "ba", then move the cursor back one cell so that the search string is "b",
    meaning the completions should be "bar", "baz", and "boop".
    """

    async def run_before(pilot: Pilot[None]) -> None:
        await pilot.press(*"ba")  # Type "ba"
        await pilot.press("left")  # Move the cursor back one cell

    assert snap_compare(CursorTracking(), run_before=run_before)


def test_dropdown_tracks_input_cursor_on_click_and_cursor_prefix_search_string(
    snap_compare,
):
    """The completions should be based on the text between the start of the input and the cursor location.

    In this example, we type "ba", then move the cursor back one cell by clicking, so that the search string is "b",
    meaning the completions should be "bar", "baz", and "boop".
    """

    async def run_before(pilot: Pilot[None]) -> None:
        await pilot.press(*"ba")  # Type "ba"
        input_widget = pilot.app.query_one(Input)
        await pilot.click(input_widget, offset=(4, 1))  # Click on the "a"

    assert snap_compare(CursorTracking(), run_before=run_before)
