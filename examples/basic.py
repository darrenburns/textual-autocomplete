from __future__ import annotations

from rich.color import Color
from rich.style import Style
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.renderables._blend_colors import blend_colors
from textual.widgets import Input, Footer, Label

from textual_autocomplete._autocomplete import AutoComplete, DropdownItem, Dropdown

INFO_TEXT = """\
Cities are ranked by population.
The left column shows the rank of the city.
The right column of the dropdown is coloured based on that population."""

DATA = [
    # ("London", "8,907,918"),
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

ITEMS = [
    DropdownItem(Text(str(rank)), Text(city), Text(population))
    for rank, (city, population) in enumerate(DATA, start=2)
]


def get_items(value: str, cursor_position: int) -> list[DropdownItem]:
    maximum_population = int(DATA[0][1].replace(",", ""))

    items = []
    for rank, (city, population) in enumerate(DATA, start=2):
        ratio = float(population.replace(",", "")) / maximum_population
        color = blend_colors(Color.parse("#e86c4a"), Color.parse("#4ed43f"), ratio)
        items.append(
            DropdownItem(
                Text(str(rank), style="#a1a1a1"),
                Text(city),
                Text(population, style=Style.from_color(color)),
            )
        )
    return [c for c in items if value.lower() in c.main.plain.lower()]


class CompletionExample(App):
    CSS_PATH = "basic.css"

    BINDINGS = [Binding("ctrl+d", "toggle_dark", "Day/Night")]

    def compose(self) -> ComposeResult:
        yield Container(
            Label("Textual Autocomplete", id="lead-text"),
            AutoComplete(
                Input(id="search-box", placeholder="Search for a UK city..."),
                Dropdown(
                    results=ITEMS,  # Using a list
                    # results=get_items,  # Using a callback to dynamically generate items
                    id="my-dropdown",
                ),
            ),
            Label(INFO_TEXT, id="info-text"),
            id="search-container",
        )
        yield Footer()


app = CompletionExample()
if __name__ == "__main__":
    app.run()
