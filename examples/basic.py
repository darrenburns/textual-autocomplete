from __future__ import annotations

from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import Input

from textual_autocomplete._autocomplete import AutoComplete, Candidate


def get_results(value: str, cursor_position: int) -> list[Candidate]:
    candidates = [
        Candidate(Text("f"), Text("foo"), Text("abc")),
        Candidate(Text("p"), Text("bar"), Text("def")),
        Candidate(Text("f"), Text("baz"), Text("ghi")),
    ]
    for candidate in candidates:
        candidate.main.set_length(20)
    return [c for c in candidates if value in c.main]


class CompletionExample(App):
    CSS_PATH = "basic.css"

    def compose(self) -> ComposeResult:
        yield Input(id="search-box")
        yield AutoComplete(linked_input="#search-box", get_results=get_results)


app = CompletionExample()
if __name__ == '__main__':
    app.run()
