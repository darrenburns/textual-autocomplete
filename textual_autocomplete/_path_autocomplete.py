from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable
from os import DirEntry
from textual.content import Content
from textual.widgets import Input
from textual.cache import LRUCache

from textual_autocomplete import DropdownItem, AutoComplete, TargetState


class PathDropdownItem(DropdownItem):
    def __init__(self, completion: str, path: Path) -> None:
        super().__init__(completion)
        self.path = path


def default_path_input_sort_key(item: PathDropdownItem) -> tuple[bool, bool, str]:
    """Sort key function for results within the dropdown.

    Args:
        item: The PathDropdownItem to get a sort key for.

    Returns:
        A tuple of (is_dotfile, is_file, lowercase_name) for sorting.
    """
    name = item.path.name
    is_dotfile = name.startswith(".")
    return (not item.path.is_dir(), not is_dotfile, name.lower())


class PathAutoComplete(AutoComplete):
    def __init__(
        self,
        target: Input | str,
        path: str | Path = ".",
        *,
        show_dotfiles: bool = True,
        sort_key: Callable[[PathDropdownItem], Any] = default_path_input_sort_key,
        folder_prefix: Content = Content("📂"),
        file_prefix: Content = Content("📄"),
        prevent_default_enter: bool = True,
        prevent_default_tab: bool = True,
        cache_size: int = 100,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """An autocomplete widget for filesystem paths.

        Args:
            target: The target input widget to autocomplete.
            path: The base path to autocomplete from.
            show_dotfiles: Whether to show dotfiles (files/dirs starting with ".").
            sort_key: Function to sort the dropdown items.
            folder_prefix: The prefix for folder items (e.g. 📂).
            file_prefix: The prefix for file items (e.g. 📄).
            prevent_default_enter: Whether to prevent the default enter behavior.
            prevent_default_tab: Whether to prevent the default tab behavior.
            cache_size: The number of directories to cache.
            name: The name of the widget.
            id: The DOM node id of the widget.
            classes: The CSS classes of the widget.
            disabled: Whether the widget is disabled.
        """
        super().__init__(
            target,
            None,
            prevent_default_enter=prevent_default_enter,
            prevent_default_tab=prevent_default_tab,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.path = Path(path) if isinstance(path, str) else path
        self.show_dotfiles = show_dotfiles
        self.sort_key = sort_key
        self.folder_prefix = folder_prefix
        self.file_prefix = file_prefix
        self._directory_cache: LRUCache[str, list[DirEntry[str]]] = LRUCache(cache_size)

    def get_candidates(self, target_state: TargetState) -> list[DropdownItem]:
        """Get the candidates for the current path segment.

        This is called each time the input changes or the cursor position changes/
        """
        current_input = target_state.text[: target_state.cursor_position]

        if "/" in current_input:
            last_slash_index = current_input.rindex("/")
            path_segment = current_input[:last_slash_index] or "/"
            directory = self.path / path_segment if path_segment != "/" else self.path
        else:
            directory = self.path

        # Use the directory path as the cache key
        cache_key = str(directory)
        cached_entries = self._directory_cache.get(cache_key)

        if cached_entries is not None:
            entries = cached_entries
        else:
            try:
                entries = list(os.scandir(directory))
                self._directory_cache[cache_key] = entries
            except OSError:
                return []

        results: list[PathDropdownItem] = []
        for entry in entries:
            # Only include the entry name, not the full path
            completion = entry.name
            if not self.show_dotfiles and completion.startswith("."):
                continue
            if entry.is_dir():
                completion += "/"
            results.append(PathDropdownItem(completion, path=Path(entry.path)))

        results.sort(key=self.sort_key)
        folder_prefix = self.folder_prefix
        file_prefix = self.file_prefix
        return [
            DropdownItem(
                item.main,
                prefix=folder_prefix if item.path.is_dir() else file_prefix,
            )
            for item in results
        ]

    def get_search_string(self, target_state: TargetState) -> str:
        """Return only the current path segment for searching in the dropdown."""
        current_input = target_state.text[: target_state.cursor_position]

        if "/" in current_input:
            last_slash_index = current_input.rindex("/")
            search_string = current_input[last_slash_index + 1 :]
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

    def should_show_dropdown(self, search_string: str) -> bool:
        default_behavior = super().should_show_dropdown(search_string)
        return (
            default_behavior
            or (search_string == "" and self.target.value != "")
            and self.option_list.option_count > 1
        )

    def clear_directory_cache(self) -> None:
        """Clear the directory cache. If you know that the contents of the directory have changed,
        you can call this method to invalidate the cache.
        """
        self._directory_cache.clear()
        target_state = self._get_target_state()
        self._rebuild_options(target_state, self.get_search_string(target_state))
