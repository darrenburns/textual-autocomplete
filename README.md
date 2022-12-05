textual-autocomplete is a Python library for creating dropdown autocompletion menus in
Textual applications, allowing users to quickly select from a list of suggestions as
they type.

[//]: # (TODO: Add video or gif demo)

## Quickstart

Simply wrap a Textual `Input` widget as follows:

```python
from textual.app import ComposeResult
from textual.widgets import Input
from textual_autocomplete import AutoComplete, Dropdown, DropdownItem

def compose(self) -> ComposeResult:
    yield AutoComplete(
        Input(placeholder="Type to search..."),
        Dropdown(items=[
            DropdownItem("Glasgow"),
            DropdownItem("Edinburgh"),
            DropdownItem("Aberdeen"),
            DropdownItem("Dundee"),
        ]),
    )
```

There are more examples [here](./examples).

## Installation

`textual-autocomplete` can be installed from PyPI using your favourite dependency
manager.

## Controls

- Press the Up or Down arrow keys to force the dropdown to appear.
- Press Esc to hide the dropdown.
- 
