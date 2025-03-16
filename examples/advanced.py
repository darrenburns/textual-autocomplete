"""Advanced autocomplete example with TextArea and custom completion strategies."""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import TextArea, Label, Button, Header, Footer

from textual_autocomplete._autocomplete import AutoComplete, Hit, TargetState


class AdvancedAutoCompleteExample(App[None]):
    """An advanced app demonstrating the AutoComplete widget with TextArea."""

    CSS = """
    Container {
        width: 100%;
        height: 100%;
    }

    #main-container {
        width: 100%;
        height: 100%;
        padding: 1;
    }

    #editor-container {
        width: 100%;
        height: 1fr;
        border: solid $primary;
        padding: 1;
    }

    Label {
        width: 100%;
        text-align: center;
        margin-bottom: 1;
    }

    TextArea {
        width: 100%;
        height: 100%;
        border: none;
        padding: 0;
    }

    #controls {
        width: 100%;
        height: auto;
        margin-top: 1;
    }

    Button {
        margin-right: 1;
    }
    """

    BINDINGS = [
        ("ctrl+space", "trigger_autocomplete", "Trigger Autocomplete"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        with Container(id="main-container"):
            yield Label("Python Code Editor with Autocomplete")
            with Container(id="editor-container"):
                editor = TextArea(language="python")
                editor.text = "# Start typing Python code here\n\n"
                yield editor

                # Create a list of Python keywords, functions, and methods as dropdown items
                python_items = [
                    # Keywords
                    Hit("def", left_meta="kw"),
                    Hit("class", left_meta="kw"),
                    Hit("import", left_meta="kw"),
                    Hit("from", left_meta="kw"),
                    Hit("if", left_meta="kw"),
                    Hit("elif", left_meta="kw"),
                    Hit("else", left_meta="kw"),
                    Hit("for", left_meta="kw"),
                    Hit("while", left_meta="kw"),
                    Hit("try", left_meta="kw"),
                    Hit("except", left_meta="kw"),
                    Hit("finally", left_meta="kw"),
                    Hit("with", left_meta="kw"),
                    Hit("as", left_meta="kw"),
                    Hit("return", left_meta="kw"),
                    # Built-in functions
                    Hit("print", left_meta="fn"),
                    Hit("len", left_meta="fn"),
                    Hit("range", left_meta="fn"),
                    Hit("str", left_meta="fn"),
                    Hit("int", left_meta="fn"),
                    Hit("float", left_meta="fn"),
                    Hit("list", left_meta="fn"),
                    Hit("dict", left_meta="fn"),
                    Hit("set", left_meta="fn"),
                    Hit("tuple", left_meta="fn"),
                    # Common snippets
                    Hit("def __init__(self):", left_meta="snip"),
                    Hit('if __name__ == "__main__":', left_meta="snip"),
                    Hit("for i in range(10):", left_meta="snip"),
                    Hit(
                        "try:\n    pass\nexcept Exception as e:\n    print(e)",
                        left_meta="snip",
                    ),
                ]

                # Custom completion strategy for snippets
                def custom_completion(value: str, state: TargetState) -> None:
                    """Custom completion strategy that handles snippets differently."""
                    target = self.query_one(TextArea)
                    if "\n" in value:
                        # For multi-line snippets, replace the current line
                        cursor_location = target.cursor_location
                        row, _ = cursor_location
                        # Get the current line's indentation
                        line_text = target.get_line(row)
                        indentation = ""
                        for char in str(line_text):
                            if char in " \t":
                                indentation += char
                            else:
                                break

                        # Replace the current line with the snippet, preserving indentation
                        lines = value.split("\n")
                        indented_lines = [indentation + line for line in lines]
                        indented_snippet = "\n".join(indented_lines)

                        # Replace the current line with the snippet
                        # Get the start and end positions of the current line
                        start_pos = (row, 0)
                        end_pos = (row, len(line_text))
                        target.replace(indented_snippet, start_pos, end_pos)
                    else:
                        # For single-line completions, just insert at cursor
                        target.replace(value, *target.selection)

                # Create the AutoComplete widget with custom completion strategy
                self.autocomplete = AutoComplete(
                    target=editor,
                    candidates=python_items,
                    completion_strategy=custom_completion,
                )
                yield self.autocomplete

            with Horizontal(id="controls"):
                yield Button("Trigger Autocomplete", id="trigger-btn")

        yield Footer()

    def action_trigger_autocomplete(self) -> None:
        """Manually trigger the autocomplete dropdown."""
        if self.autocomplete.styles.display == "none":
            self.autocomplete.action_show()
        else:
            self.autocomplete.action_hide()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "trigger-btn":
            self.action_trigger_autocomplete()


if __name__ == "__main__":
    app = AdvancedAutoCompleteExample()
    app.run()
