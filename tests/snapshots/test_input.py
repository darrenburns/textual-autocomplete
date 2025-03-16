"""Snapshot tests for the Input widget with autocomplete."""

from textual.app import App, ComposeResult
from textual.pilot import Pilot
from textual.widgets import Input
from textual.widgets.input import Selection

from textual_autocomplete import AutoComplete, AutoCompleteList, DropdownItem

LANGUAGES = [
    "Python",
    "JavaScript",
    "TypeScript",
    "Java",
    "C++",
    "Ruby",
    "Go",
    "Rust",
    "C#",
    "Swift",
    "Kotlin",
    "PHP",
]


class BasicInputAutocomplete(App[None]):
    def compose(self) -> ComposeResult:
        input = Input(placeholder="Type here...")
        yield input
        yield AutoComplete(
            target=input,
            candidates=[DropdownItem(lang) for lang in LANGUAGES],
        )
        yield Input(placeholder="Another input which can be focused")


def test_single_matching_candidate(snap_compare):
    """Typing should make the dropdown appear and show filtered results."""

    async def run_before(pilot: Pilot) -> None:
        await pilot.press(*"py")

    assert snap_compare(BasicInputAutocomplete(), run_before=run_before)


def test_many_matching_candidates(snap_compare):
    """Typing should make the dropdown appear and show filtered results."""

    async def run_before(pilot: Pilot) -> None:
        await pilot.press(*"ja")

    assert snap_compare(BasicInputAutocomplete(), run_before=run_before)


def test_selecting_candidate_should_complete_input__enter_key(snap_compare):
    """Selecting a candidate using the enter key should complete the input."""

    async def run_before(pilot: Pilot) -> None:
        await pilot.press(*"ja")
        await pilot.press("down")
        await pilot.press("enter")

    assert snap_compare(BasicInputAutocomplete(), run_before=run_before)


def test_selecting_candidate_should_complete_input__tab_key(snap_compare):
    """Selecting a candidate using the tab key should complete the input."""

    async def run_before(pilot: Pilot) -> None:
        await pilot.press(*"ja")
        await pilot.press("down")
        await pilot.press("tab")

    assert snap_compare(BasicInputAutocomplete(), run_before=run_before)


def test_tab_still_works_after_completion(snap_compare):
    """Tabbing after completing an input should still work (the autocomplete should not consume the tab key).

    The second input should become focused in this example."""

    async def run_before(pilot: Pilot) -> None:
        await pilot.press(*"ja")
        await pilot.press("down")
        await pilot.press("tab")
        await pilot.press("tab")

    assert snap_compare(BasicInputAutocomplete(), run_before=run_before)


def test_summon_by_pressing_down(snap_compare):
    """We can summon the autocomplete dropdown by pressing the down arrow key."""

    async def run_before(pilot: Pilot) -> None:
        await pilot.press("down")

    assert snap_compare(BasicInputAutocomplete(), run_before=run_before)


def test_hide_after_summoning_by_pressing_escape(snap_compare):
    """Dropdown summoned via down, then escape was pressed to hide it."""

    async def run_before(pilot: Pilot) -> None:
        await pilot.press("down")
        await pilot.press("escape")

    assert snap_compare(BasicInputAutocomplete(), run_before=run_before)


def test_summon_when_only_one_full_match_does_not_show_dropdown(snap_compare):
    """If the dropdown contains only one item, and that item is an exact match for the dropdown
    content, then the dropdown should not be shown."""

    async def run_before(pilot: Pilot) -> None:
        await pilot.press(*"py")
        await pilot.press("enter")
        await pilot.press("down")

    assert snap_compare(BasicInputAutocomplete(), run_before=run_before)


def test_hide_after_typing_by_pressing_escape(snap_compare):
    """Dropdown summoned via typing a matching query, then escape was pressed to hide it."""

    async def run_before(pilot: Pilot) -> None:
        await pilot.press(*"py")
        await pilot.press("escape")

    assert snap_compare(BasicInputAutocomplete(), run_before=run_before)


def test_candidate_can_be_selected_via_click(snap_compare):
    """A candidate can be selected by clicking on it.

    In this example, we click on "Java", which is the second result in the dropdown.
    """

    async def run_before(pilot: Pilot) -> None:
        await pilot.press(*"ja")
        await pilot.click(AutoCompleteList, offset=(1, 1))  # Click second result

    assert snap_compare(BasicInputAutocomplete(), run_before=run_before)


def test_text_selection_works_while_autocomplete_is_open(snap_compare):
    """If the dropdown is open, the text selection should still work."""

    async def run_before(pilot: Pilot) -> None:
        await pilot.press(*"ja")
        input = pilot.app.query_one(Input)
        input.selection = Selection(0, 2)

    assert snap_compare(BasicInputAutocomplete(), run_before=run_before)


def test_completion_still_works_if_chosen_while_input_widget_has_selection(
    snap_compare,
):
    """If the dropdown is open, and a candidate is chosen, the completion should still
    work, and the selection should move to the end of the input."""

    async def run_before(pilot: Pilot) -> None:
        await pilot.press(*"ja")
        input = pilot.app.query_one(Input)
        input.selection = Selection(0, 2)
        await pilot.press("down")
        await pilot.press("enter")

    assert snap_compare(BasicInputAutocomplete(), run_before=run_before)


def test_dropdown_tracks_cursor_position(snap_compare):
    """The dropdown should track the cursor position of the target widget."""

    async def run_before(pilot: Pilot) -> None:
        await pilot.press(*"ja")
        await pilot.press("down")


# TODO: Test that dropdown tracks cursor when scrolling occurs
# TODO: Test the dropdown tracks cursor when cursor moves via other means
