import os
from pathlib import Path
from typing import Callable, Sequence
from textual.widgets import Input

from textual_autocomplete import DropdownItem, InputAutoComplete, TargetState


class PathInputAutoComplete(InputAutoComplete):
    def __init__(
        self,
        target: Input | str,
        candidates: Sequence[DropdownItem | str]
        | Callable[[TargetState], list[DropdownItem]]
        | None = None,
        *,
        base_path: str | Path = ".",
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
            prevent_default_enter=prevent_default_enter,
            prevent_default_tab=prevent_default_tab,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        base_path = Path(base_path) if isinstance(base_path, str) else base_path
        self.base_path = base_path

    def get_candidates(self, target_state: TargetState) -> list[DropdownItem]:
        current_input = target_state.text[: target_state.cursor_position]

        if "/" in current_input:
            last_slash_index = current_input.rindex("/")
            directory = current_input[:last_slash_index] or "/"
            prefix = current_input[last_slash_index + 1 :]
        else:
            directory = "."
            prefix = current_input

        try:
            entries = list(os.scandir(directory))
        except OSError:
            return []
        else:
            filtered_entries = [
                entry for entry in entries if entry.name.startswith(prefix)
            ]

            results: list[DropdownItem] = []
            for entry in filtered_entries:
                # Only include the entry name, not the full path
                completion = entry.name
                if entry.is_dir():
                    completion += "/"
                results.append(DropdownItem(completion))

            return results

    def get_search_string(self, target_state: TargetState) -> str:
        """Return only the current path segment for searching in the dropdown."""
        current_input = target_state.text[: target_state.cursor_position]

        if "/" in current_input:
            last_slash_index = current_input.rindex("/")
            search_string = current_input[last_slash_index + 1 :]
            print(f"search_string: {search_string}")
            return search_string
        else:
            return current_input

    def apply_completion(self, value: str, state: TargetState) -> None:
        """Apply the completion by replacing only the current path segment."""
        target = self.target
        current_input = state.text
        cursor_position = state.cursor_position

        # There's a slash before the cursor, so we only want to replace
        # the text after the last slash with the selected value
        try:
            replace_start_index = current_input.rindex("/", 0, cursor_position)
        except ValueError:
            # No slashes, so we do a full replacement
            new_value = value
            new_cursor_position = len(value)
        else:
            # Keep everything before and including the slash before the cursor.
            path_prefix = current_input[: replace_start_index + 1]
            new_value = path_prefix + value
            new_cursor_position = len(path_prefix) + len(value)

        with self.prevent(Input.Changed):
            target.value = new_value
            target.cursor_position = new_cursor_position

    def post_completion(self) -> None:
        if not self.target.value.endswith("/"):
            self.action_hide()
