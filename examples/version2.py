from textual.app import App, ComposeResult
from textual.widgets import Input, TextArea

from textual_autocomplete import AutoComplete, DropdownItem


class Version2(App[None]):
    def compose(self) -> ComposeResult:
        # input = TextArea()
        input = Input()
        yield input
        yield AutoComplete(
            target=input,
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


app = Version2()
app.run()
