from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Input

from examples.basic import ITEMS
from textual_autocomplete._autocomplete import AutoComplete, Dropdown


class Quadrant(App):
    def compose(self) -> ComposeResult:
        auto_completes = [
            AutoComplete(
                Input(classes="search-box", placeholder="Search for a UK city..."),
                Dropdown(results=ITEMS, classes=f"dropdown", id=f"dropdown-{i}"),
            )
            for i in range(1, 4)
        ]

        yield Container(
            *auto_completes,
            id="grid",
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        for input in list(self.query(Input))[1:]:
            input.cursor_position = event.input.cursor_position
            input.value = event.value


app = Quadrant(css_path="quadrant.css")
if __name__ == "__main__":
    app.run()
