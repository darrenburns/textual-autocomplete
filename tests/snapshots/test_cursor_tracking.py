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
                yield (input := Input(placeholder="Type here..."))

        yield AutoComplete(
            target=input,
            candidates=["foo", "bar", "baz", "qux"],
        )


def test_dropdown_tracks_cursor_when_parent_scrolls(snap_compare):
    """We type, the dropdown appears, then we scroll, and the dropdown tracks the cursor."""

    async def run_before(pilot: Pilot[None]) -> None:
        await pilot.press("b")
        scrollable = pilot.app.query_one("#scrollable")
        scrollable.scroll_relative(x=5, y=5, animate=False, force=True)
        await pilot.pause()

    assert snap_compare(CursorTracking(), run_before=run_before)


# TODO: Test that dropdown tracks cursor when scrolling occurs
# TODO: Test the dropdown tracks cursor when cursor moves via other means
