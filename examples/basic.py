from __future__ import annotations

from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import Input

from textual_autocomplete._autocomplete import AutoComplete, Candidate

DATA = [
    ("London", "8,907,918"),
    ("Birmingham", "1,153,717"),
    ("Glasgow", "612,040"),
    ("Liverpool", "579,256"),
    ("Bristol", "571,922"),
    ("Manchester", "554,400"),
    ("Sheffield", "544,402"),
    ("Leeds", "503,388"),
    ("Edinburgh", "488,050"),
    ("Leicester", "470,965"),
    ("Coventry", "369,127"),
    ("Bradford", "361,046"),
    ("Cardiff", "350,558"),
    ("Belfast", "328,937"),
    ("Nottingham", "311,823"),
    ("Kingston upon Hull", "288,671"),
    ("Newcastle upon Tyne", "281,842"),
    ("Stoke-on-Trent", "277,051"),
    ("Southampton", "269,231"),
    ("Derby", "263,933"),
    ("Portsmouth", "248,479"),
    ("Brighton", "241,999"),
    ("Plymouth", "241,179"),
    ("Northampton", "229,815"),
    ("Reading", "229,274"),
    ("Luton", "222,907"),
    ("Wolverhampton", "218,255"),
    ("Bolton", "202,369"),
    ("Aberdeen", "200,680"),
    ("Bournemouth", "198,727"),
]


def get_results(value: str, cursor_position: int) -> list[Candidate]:
    candidates = [
        Candidate(Text(str(rank)), Text(city), Text(population))
        for rank, (city, population) in enumerate(DATA, start=1)
    ]
    return [c for c in candidates if value.lower() in c.main.plain.lower()]


class CompletionExample(App):
    CSS_PATH = "basic.css"

    def compose(self) -> ComposeResult:
        yield Input(id="search-box")
        yield AutoComplete(linked_input="#search-box", get_results=get_results)



app = CompletionExample()
if __name__ == "__main__":
    app.run()
