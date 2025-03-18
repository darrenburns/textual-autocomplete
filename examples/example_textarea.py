from textual.app import App, ComposeResult
from textual.widgets import TextArea, Header, Footer
from textual_autocomplete import InputAutoComplete, DropdownItem


class TextAreaAutoCompleteExample(App[None]):
    """Example application demonstrating the AutoComplete widget with a TextArea."""

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
    ]

    CSS = """
    Screen {
        align: center middle;
    }

    TextArea {
        width: 80%;
        height: 70%;
        border: solid $accent;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield TextArea(
            "# TextArea with Autocomplete\n\nStart typing 'py' to see autocompletion.\n"
            "Try typing some of these words:\n- python\n- pypi\n- pytest\n- pydantic\n",
            id="code-editor",
        )

        # Example with a list of programming language keywords
        programming_terms = [
            DropdownItem(main="python", left_column="🐍"),
            DropdownItem(main="pypi", left_column="📦"),
            DropdownItem(main="pytest", left_column="🧪"),
            DropdownItem(main="pydantic", left_column="🔍"),
            DropdownItem(main="pygame", left_column="🎮"),
            DropdownItem(main="pylint", left_column="🔎"),
            DropdownItem(main="pyramid", left_column="🏔️"),
            DropdownItem(main="pyyaml", left_column="📄"),
        ]

        yield InputAutoComplete(
            target="#code-editor",
            candidates=programming_terms,
        )
        yield Footer()


if __name__ == "__main__":
    app = TextAreaAutoCompleteExample()
    app.run()
