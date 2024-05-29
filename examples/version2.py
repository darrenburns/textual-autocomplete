from textual.app import App, ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Input, TextArea

from textual_autocomplete import AutoComplete, DropdownItem


class Version2(App[None]):
    CSS = "Input { margin-top: 20; } Vertical { height: 100; }"

    def compose(self) -> ComposeResult:
        # input = TextArea()
        with VerticalScroll():
            with Vertical():
                yield Input()

    def on_mount(self) -> None:
        # If we mount it like this it ensures it's on the screen.
        # This might be easier to explain.
        self.screen.mount(
            AutoComplete(
                target=self.query_one(Input),
                items=[
                    DropdownItem("Content-Type"),
                    DropdownItem("User-Agent"),
                    DropdownItem("Accept"),
                    DropdownItem("Accept-Language"),
                    DropdownItem("Accept-Encoding"),
                    DropdownItem("Authorization"),
                    DropdownItem("Cookie"),
                    DropdownItem("Host"),
                ],
            )
        )


app = Version2()
app.run()
