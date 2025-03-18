"""By default, textual-autocomplete replaces the entire content of a widget
with a completion.

Sometimes, however, you may wish to insert the completion text, or otherwise use
custom logic to determine the end-state of the Input after the user selects a completion.

For example, if completing a path on a filesystem, you may wish to offer partial completions
of the path based on the current content of the Input. Then, when the user selects a completion,
you could offer a different set of completions based on the new path in the Input.
"""

import os
from textual.app import App, ComposeResult
from textual.widgets import Input

from textual_autocomplete import DropdownItem, InputAutoComplete, TargetState


class PartialCompletionApp(App[None]):
    def compose(self) -> ComposeResult:
        input_widget = Input(placeholder="Enter a path...")
        yield input_widget
        yield InputAutoComplete(target=input_widget, candidates=self.get_candidates)

    def get_candidates(self, state: TargetState) -> list[DropdownItem]:
        maybe_path = state.text
        print(f"maybe_path: {maybe_path}")
    
        # If the input is empty, offer completions for all files/directories in the current directory.
        if not maybe_path:
            cwd_items = [DropdownItem(item) for item in os.listdir(".")]
            print(f"cwd_items: {cwd_items}")
            return cwd_items
        
        # If the input ends with a slash, offer completions for all files/directories in the given path.
        if maybe_path.endswith("/") and os.path.exists(maybe_path):
            path_items = [DropdownItem(item) for item in os.listdir(maybe_path)]
            print(f"path_items: {path_items}")
            return path_items
        
        return []


if __name__ == "__main__":
    app = PartialCompletionApp()
    app.run()
