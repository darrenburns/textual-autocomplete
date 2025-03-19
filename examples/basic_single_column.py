"""Basic dropdown autocomplete from a list of options."""

from textual.app import App, ComposeResult
from textual.widgets import Input

from textual_autocomplete import AutoComplete

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


class AutoCompleteExample(App[None]):
    def compose(self) -> ComposeResult:
        text_input = Input(placeholder="Search for a programming language...")
        yield text_input

        yield AutoComplete(
            target=text_input,  # The widget to attach autocomplete to
            candidates=LANGUAGES,  # The list of completion candidates
        )


if __name__ == "__main__":
    app = AutoCompleteExample()
    app.run()
