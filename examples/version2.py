from textual.app import App, ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Input, TextArea

from textual_autocomplete import AutoComplete, DropdownItem


class Version2(App[None]):
    CSS = "Input {  } Vertical { height: 100; }"

    def compose(self) -> ComposeResult:
        # input = TextArea()
        with VerticalScroll():
            with Vertical():
                yield Input(id="my-input")
                yield Input()

    def on_mount(self) -> None:
        # If we mount it like this it ensures it's on the screen.
        # This might be easier to explain.
        # OR we could provide a utility function that does this for us.
        self.screen.mount(
            AutoComplete(
                target=self.query_one("#my-input", Input),
                items=[
                    DropdownItem("Content-Type"),
                    DropdownItem("User-Agent"),
                    DropdownItem("Accept"),
                    DropdownItem("Accept-Language"),
                    DropdownItem("Accept-Encoding"),
                    DropdownItem("Authorization"),
                    DropdownItem("Cookie"),
                    DropdownItem("Host"),
                    DropdownItem("Connection"),
                    DropdownItem("Referrer"),
                    DropdownItem("Referrer-Policy"),
                    DropdownItem("Sec-Fetch-Dest"),
                    DropdownItem("Sec-Fetch-Mode"),
                    DropdownItem("Origin"),
                    DropdownItem("Pragma"),
                    DropdownItem("Expect"),
                    DropdownItem("Upgrade-Insecure-Requests"),
                ],
                prevent_default_tab=False,
            )
        )


app = Version2()
app.run()
