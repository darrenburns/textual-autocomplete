textual-autocomplete is a Python library for creating dropdown autocompletion menus in
Textual applications, allowing users to quickly select from a list of suggestions as
they type.

<img width="554" alt="image" src="https://user-images.githubusercontent.com/5740731/205718538-5599a9db-48a2-49dd-99c3-34d43459b81a.png">

<details>
<summary>Video example</summary>

https://user-images.githubusercontent.com/5740731/205718330-a9364894-9133-40ca-8249-6e3dcc13f456.mov

</details>



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
