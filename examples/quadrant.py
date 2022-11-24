from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Input, Footer

from examples.basic import ITEMS
from textual_autocomplete._autocomplete import AutoComplete, Dropdown


class Quadrant(App):
    def compose(self) -> ComposeResult:
        auto_completes = [
            AutoComplete(
                Input(classes="search-box", placeholder="Search for a UK city..."),
                Dropdown(items=ITEMS, classes=f"dropdown", id=f"dropdown-{i}"),
            )
            for i in range(1, 4)
        ]
        yield Container()
        yield Container(
            *auto_completes,
            id="grid",
        )
        yield Footer()

    def watch_scroll_y(self, event) -> None:
        print("SCROLLING DOWN")
        for dropdown in self.query(Dropdown):
            dropdown.reposition()




app = Quadrant(css_path="quadrant.css")
if __name__ == "__main__":
    app.run()
