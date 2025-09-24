from textual_autocomplete._autocomplete import AutoComplete
from textual.app import App, ComposeResult
from textual.containers import Center, VerticalScroll
from textual.widgets import Input


class CursorTracking(App[None]):
    CSS = """
    #scrollable {
        overflow: scroll scroll;
        scrollbar-color: red;
        Center {
            background: $accent;
            height: 100;
            width: 100;
            align-vertical: middle;
        }
        Input {
            width: 24;
        }
    }
    """

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="scrollable", can_focus=False):
            with Center():
                input = Input(placeholder="Type here...")
                input.cursor_blink = False
                yield input

        yield AutoComplete(
            target=input,
            candidates=["foo", "bar", "baz", "qux", "boop"],
        )


if __name__ == "__main__":
    app = CursorTracking()
    app.run()
