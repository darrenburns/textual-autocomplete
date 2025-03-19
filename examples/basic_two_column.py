"""Two column dropdown example with simple styling on the prefix."""

from textual.app import App, ComposeResult
from textual.content import Content
from textual.widgets import Input, Label

from textual_autocomplete import AutoComplete, DropdownItem

# Languages with their popularity rank
LANGUAGES_WITH_RANK = [
    (1, "Python"),
    (2, "JavaScript"),
    (3, "Java"),
    (4, "C++"),
    (5, "TypeScript"),
    (6, "Go"),
    (7, "Ruby"),
    (8, "Rust"),
]

# Create dropdown items with two columns: rank and language name
CANDIDATES = [
    DropdownItem(
        language,  # Main text to be completed
        prefix=Content.from_markup(
            f"[$text-primary on $primary-muted] {rank} "
        ),  # Prefix showing rank, styled with Textual markup!
    )
    for rank, language in LANGUAGES_WITH_RANK
]


class TwoColumnAutoCompleteExample(App[None]):
    def compose(self) -> ComposeResult:
        yield Label("Start typing a programming language:")
        text_input = Input(placeholder="Type here...")
        yield text_input

        yield AutoComplete(
            target=text_input,  # The widget to attach autocomplete to
            candidates=CANDIDATES,  # The list of completion candidates
        )


if __name__ == "__main__":
    app = TwoColumnAutoCompleteExample()
    app.run()
