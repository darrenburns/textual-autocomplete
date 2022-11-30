from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Input, Footer

from examples.basic import ITEMS, get_items
from textual_autocomplete._autocomplete import AutoComplete, Dropdown


class Quadrant(App):
    def compose(self) -> ComposeResult:
        auto_completes = [
            AutoComplete(
                Input(classes="search-box", placeholder="Search for a UK city...", id=f"input-{i}"),
                Dropdown(classes=f"dropdown", id=f"dropdown-{i}"),
                items=ITEMS,
            )
            for i in range(1, 4)
        ]
        yield Container(
            *auto_completes,
            AutoComplete(
                Input(placeholder="Search for a UK city...", id="input-4"),
                Dropdown(
                    classes="dropdown",
                    id="dropdown-4",
                ),
                items=get_items,  # Using a callback to dynamically generate items
            ),
            id="grid",
        )
        yield Footer()


app = Quadrant(css_path="quadrant.css")
if __name__ == "__main__":
    app.run()
