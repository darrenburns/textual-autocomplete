from __future__ import annotations

from textual.app import App, ComposeResult
from textual.pilot import Pilot
from textual.widgets import Input
from textual_autocomplete import AutoComplete


class StyledAutocomplete(App[None]):
    def compose(self) -> ComposeResult:
        input = Input(placeholder="Search...")
        yield input
        yield AutoComplete(target=input, candidates=["foo", "bar", "baz", "qux"])


def test_foreground_color_and_text_style(snap_compare):
    """Background color should not be impacted by the text foreground and style."""
    StyledAutocomplete.CSS = """
    AutoComplete {
        & .autocomplete--highlight-match {
            color: $text-accent;
            text-style: bold italic underline;
        }
    }
    """

    async def run_before(pilot: Pilot) -> None:
        await pilot.press(*"ba")

    assert snap_compare(StyledAutocomplete(), run_before=run_before)


def test_background_color_and_removed_style(snap_compare):
    StyledAutocomplete.CSS = """
    AutoComplete {
        & .autocomplete--highlight-match {
            color: $text-accent;
            background: $success-muted;
            text-style: not bold;
        }
    }
    """

    async def run_before(pilot: Pilot) -> None:
        await pilot.press(*"ba")

    assert snap_compare(StyledAutocomplete(), run_before=run_before)


def test_max_height_and_scrolling(snap_compare):
    """We should be scrolled to qux, and the red scrollbar should reflect that."""
    StyledAutocomplete.CSS = """
    AutoComplete {
        & AutoCompleteList {
            scrollbar-color: red;
            max-height: 2;
        }
    }
    """

    async def run_before(pilot: Pilot) -> None:
        await pilot.press("down", "down", "down", "down")

    assert snap_compare(StyledAutocomplete(), run_before=run_before)


def test_dropdown_styles_match_textual_theme(snap_compare):
    """Dropdown styles should match the textual theme. In this test, we've swapped the theme to nord."""
    StyledAutocomplete.CSS = """
    AutoComplete {
        & .autocomplete--highlight-match {
            color: $text-accent;
        }
    }
    """

    async def run_before(pilot: Pilot) -> None:
        pilot.app.theme = "nord"
        await pilot.press(*"ba")

    assert snap_compare(StyledAutocomplete(), run_before=run_before)


def test_cursor_color_change_and_dropdown_background_change(snap_compare):
    """Checking various interactions between styles. See the test's CSS for info."""
    StyledAutocomplete.CSS = """
    AutoComplete {

        & AutoCompleteList {
            color: red;
            background: $error-muted;
            & > .option-list--option-highlighted {
                color: $text-primary;
                background: magenta;
                text-style: italic;
            }
        }

        & .autocomplete--highlight-match {
            color: $text-success;
            background: $success-muted;
            text-style: underline;
        }

    }
    """

    async def run_before(pilot: Pilot) -> None:
        await pilot.press(*"ba")

    assert snap_compare(StyledAutocomplete(), run_before=run_before)
