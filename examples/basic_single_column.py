"""Basic dropdown autocomplete from a list of options."""

from textual.app import App, ComposeResult
from textual.widgets import Input, Label

from textual_autocomplete._autocomplete import AutoComplete, DropdownItem

LANGUAGES = [
    "Python",
    "JavaScript",
    "TypeScript",
    "Java",
    "C++",
    "Ruby",
    "Go",
    "Rust",
]

CANDIDATES = [DropdownItem(lang) for lang in LANGUAGES]


class AutoCompleteExample(App[None]):
    def compose(self) -> ComposeResult:
        yield Label("Start typing a programming language:")
        text_input = Input(placeholder="Type here...")
        yield text_input

        yield AutoComplete(
            target=text_input,  # The widget to attach autocomplete to
            candidates=CANDIDATES,  # The list of completion candidates
        )


if __name__ == "__main__":
    app = AutoCompleteExample()
    app.run()
