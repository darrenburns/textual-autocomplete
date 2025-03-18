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

            path_prefix = directory if directory.endswith("/") else f"{directory}/"
            if directory == ".":
                path_prefix = ""

            results: list[DropdownItem] = []
            for entry in filtered_entries:
                completion = f"{path_prefix}{entry.name}"
                if entry.is_dir():
                    completion += "/"
                results.append(DropdownItem(completion))

            return results

    def post_completion(self) -> None:
        if not self.should_show_dropdown(self.target.value):
            self.action_hide()
