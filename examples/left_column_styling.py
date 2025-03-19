from textual.app import App, ComposeResult
from textual.content import Content
from textual.widgets import Input

from textual_autocomplete import AutoComplete, DropdownItem


LANGUAGES = [
    DropdownItem(
        "Python",
        prefix=Content.from_markup("[$text-success on $success-muted] 🐍 "),
    ),
    DropdownItem(
        "Golang",
        prefix=Content.from_markup("[$text-primary on $primary-muted] 🔷 "),
    ),
    DropdownItem("Java", prefix=Content.from_markup("[#6a2db5 on magenta 20%] ☕ ")),
    DropdownItem(
        "Rust", prefix=Content.from_markup("[$text-accent on $accent-muted] 🦀 ")
    ),
]


class LanguagesSearchApp(App[None]):
    CSS = """
    Input {
        margin: 2 4;
    }
    """

    def compose(self) -> ComposeResult:
        input_widget = Input(placeholder="Search for a programming language...")
        yield input_widget
        yield AutoComplete(target=input_widget, candidates=LANGUAGES)


if __name__ == "__main__":
    app = LanguagesSearchApp()
    app.run()
