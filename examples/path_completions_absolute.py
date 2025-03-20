"""By default, textual-autocomplete replaces the entire content of a widget
with a completion.

Sometimes, however, you may wish to insert the completion text, or otherwise use
custom logic to determine the end-state of the Input after the user selects a completion.

For example, if completing a path on a filesystem, you may wish to offer partial completions
of the path based on the current content of the Input. Then, when the user selects a completion,
you could offer a different set of completions based on the new path in the Input.
"""

from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Input, Label

from textual_autocomplete import PathAutoComplete


class FileSystemPathCompletions(App[None]):
    CSS = """
    #container {
        padding: 2 4;
    }
    #label {
        margin-left: 3;
    }
    Input {
        width: 80%;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="container"):
            yield Label("Choose a file!", id="label")
            input_widget = Input(placeholder="Enter a path...")
            yield input_widget
            yield PathAutoComplete(target=input_widget, path=Path.cwd())


if __name__ == "__main__":
    app = FileSystemPathCompletions()
    app.run()
