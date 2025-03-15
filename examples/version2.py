from __future__ import annotations
from functools import lru_cache

import os
import re
from typing import Callable

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Footer, Input, TextArea

from textual_autocomplete import (
    AutoComplete,
    DropdownItem,
    MatcherFactoryType,
    TargetState,
)

from rich.text import Text

from ._headers import REQUEST_HEADERS

_VARIABLES_PATTERN = re.compile(
    r"\$(?:([a-zA-Z_][a-zA-Z0-9_]*)|{([a-zA-Z_][a-zA-Z0-9_]*)})"
)


def get_variables() -> dict[str, str | None]:
    return {header["name"]: "" for header in REQUEST_HEADERS}


@lru_cache()
def find_variables(template_str: str) -> list[tuple[str, int, int]]:
    return [
        (m.group(1) or m.group(2), m.start(), m.end())
        for m in re.finditer(_VARIABLES_PATTERN, template_str)
    ]


@lru_cache()
def is_cursor_within_variable(cursor: int, text: str) -> bool:
    if not text or cursor < 0 or cursor > len(text):
        return False

    # Check for ${var} syntax
    start = text.rfind("${", 0, cursor)
    if start != -1:
        end = text.find("}", start)
        if end != -1 and start < cursor <= end:
            return True

    # Check for $ followed by { (cursor between $ and {)
    if (
        cursor > 0
        and text[cursor - 1] == "$"
        and cursor < len(text)
        and text[cursor] == "{"
    ):
        return True

    # Check for $var syntax
    last_dollar = text.rfind("$", 0, cursor)
    if last_dollar == -1:
        return False

    # Check if cursor is within a valid variable name
    for i in range(last_dollar + 1, len(text)):
        if i >= cursor:
            return True
        if not (text[i].isalnum() or text[i] == "_"):
            return False

    return True


@lru_cache()
def find_variable_start(cursor: int, text: str) -> int:
    if not text:
        return cursor

    # Check for ${var} syntax
    start = text.rfind("${", 0, cursor)
    if start != -1 and start < cursor <= text.find("}", start):
        return start

    # Check for $ followed by { (cursor between $ and {)
    if (
        cursor > 0
        and text[cursor - 1] == "$"
        and cursor < len(text)
        and text[cursor] == "{"
    ):
        return cursor - 1

    # Check for $var syntax
    for i in range(cursor - 1, -1, -1):
        if text[i] == "$":
            if i + 1 < len(text) and text[i + 1] == "{":
                return i
            if all(c.isalnum() or c == "_" for c in text[i + 1 : cursor]):
                return i

    return cursor  # No valid variable start found


@lru_cache()
def find_variable_end(cursor: int, text: str) -> int:
    if not text:
        return cursor

    # Check for ${var} syntax
    start = text.rfind("${", 0, cursor)
    if start != -1:
        end = text.find("}", start)
        if end != -1 and start < cursor <= end + 1:  # Include the closing brace
            return end + 1

    # Check for $ followed by { (cursor between $ and {)
    if (
        cursor > 0
        and text[cursor - 1] == "$"
        and cursor < len(text)
        and text[cursor] == "{"
    ):
        end = text.find("}", cursor)
        if end != -1:
            return end + 1

    # Check for $var syntax
    for i in range(cursor, len(text)):
        if not (text[i].isalnum() or text[i] == "_"):
            return i

    return len(text)


@lru_cache()
def get_variable_at_cursor(cursor_column: int, text: str) -> str | None:
    if not is_cursor_within_variable(cursor_column, text):
        return None

    start = find_variable_start(cursor_column, text)
    end = find_variable_end(cursor_column, text)

    return text[start:end]


def extract_variable_name(variable_text: str) -> str:
    """
    Extract the variable name from a variable reference.

    Args:
        variable_text: The text containing the variable reference.

    Returns:
        str: The extracted variable name.

    Examples:
        >>> extract_variable_name("$var")
        'var'
        >>> extract_variable_name("${MY_VAR}")
        'MY_VAR'
    """
    if variable_text.startswith("${") and variable_text.endswith("}"):
        return variable_text[2:-1]
    elif variable_text.startswith("$"):
        return variable_text[1:]
    return variable_text  # Return as-is if it doesn't match expected formats


class SubstitutionError(Exception):
    """Raised when the user refers to a variable that doesn't exist."""


class VariableAutoComplete(AutoComplete):
    def __init__(
        self,
        target: Input | TextArea | str,
        candidates: list[DropdownItem] | Callable[[TargetState], list[DropdownItem]],
        variable_candidates: list[DropdownItem]
        | Callable[[TargetState], list[DropdownItem]]
        | None = None,
        matcher_factory: MatcherFactoryType | None = None,
        prevent_default_enter: bool = True,
        prevent_default_tab: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            target,
            candidates,
            matcher_factory,
            None,
            self._search_string,
            prevent_default_enter,
            prevent_default_tab,
            name,
            id,
            classes,
            disabled,
        )
        if variable_candidates is None:
            variable_candidates = [
                DropdownItem(main=f"${variable}") for variable in get_variables()
            ]
        self.variable_candidates = variable_candidates

    def get_candidates(self, target_state: TargetState) -> list[DropdownItem]:
        cursor = target_state.selection.end[1]
        text = target_state.text
        if is_cursor_within_variable(cursor, text):
            return self.get_variable_candidates(target_state)
        else:
            return super().get_candidates(target_state)

    def _search_string(self, target_state: TargetState) -> str:
        cursor_row, cursor_column = target_state.selection.end
        text = target_state.text
        target = self.target

        if isinstance(target, TextArea):
            text = target.document.get_line(cursor_row)

        if is_cursor_within_variable(cursor_column, text):
            variable_at_cursor = get_variable_at_cursor(cursor_column, text)
            return variable_at_cursor or ""
        else:
            if isinstance(target, TextArea):
                # Use the word behind the cursor as a search string
                start, end = self.get_text_area_word_bounds_before_cursor(self.target)
                search_string = target.get_text_range(start, end)
                print("DEFAULT search_string", search_string)
                return search_string
            else:
                # Use the entire Input as a search string
                return target.value

    def get_variable_candidates(self, target_state: TargetState) -> list[DropdownItem]:
        candidates = self.variable_candidates
        return candidates(target_state) if callable(candidates) else candidates


class Version2(App[None]):
    CSS = "Vertical { height: 100; } TextArea { height: 1fr; }"

    BINDINGS = [
        Binding("ctrl+n", "insert_matching_text", "Insert matching text"),
    ]

    def compose(self) -> ComposeResult:
        # input = TextArea()
        with VerticalScroll():
            with Vertical():
                input_one = Input(id="my-input")
                input_one.focus()
                yield input_one
                yield Input()
                yield TextArea.code_editor()
        yield Footer()

    def on_mount(self) -> None:
        # If we mount it like this it ensures it's on the screen.
        # This might be easier to explain.
        # OR we could provide a utility function that does this for us.

        items: list[DropdownItem] = []
        for header in REQUEST_HEADERS:
            style = "yellow" if header["experimental"] else ""
            items.append(DropdownItem(Text(header["name"], style=style)))

        self.screen.mount(
            VariableAutoComplete(
                target=self.query_one("#my-input", Input),
                candidates=[
                    DropdownItem(main=header) for header in request_header_names
                ],
                variable_candidates=[
                    DropdownItem(main=f"${var}") for var in os.environ.keys()
                ],
            )
        )

        self.screen.mount(
            VariableAutoComplete(
                target=self.query_one(TextArea),
                candidates=[
                    DropdownItem(main=header) for header in request_header_names
                ],
                variable_candidates=[
                    DropdownItem(main=f"${var}") for var in os.environ.keys()
                ],
            )
        )

    def action_insert_matching_text(self) -> None:
        self.query_one("#my-input", Input).value = "Authorization"


if __name__ == "__main__":
    app = Version2()
    app.run()
