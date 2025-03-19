from textual.app import App, ComposeResult
from textual.widgets import Input

from textual_autocomplete import AutoComplete
from textual_autocomplete._autocomplete import DropdownItem, TargetState


class DynamicDataApp(App[None]):
    CSS = """
Input {
    margin: 2 4;
}
"""

    def compose(self) -> ComposeResult:
        input_widget = Input()
        yield input_widget
        yield AutoComplete(input_widget, candidates=self.get_candidates)

    def get_candidates(self, state: TargetState) -> list[DropdownItem]:
        left = len(state.text)
        return [
            DropdownItem(item, prefix=f"{left:>2} ")
            for item in [
                "Apple",
                "Banana",
                "Cherry",
                "Orange",
                "Pineapple",
                "Strawberry",
                "Watermelon",
            ]
        ]


if __name__ == "__main__":
    app = DynamicDataApp()
    app.run()
