# textual-autocomplete

textual-autocomplete is a Python library for creating dropdown autocompletion menus in
Textual applications, allowing users to quickly select from a list of suggestions as
they type.

> **Warning**
> 
> Not quite ready for use yet - I'm aiming for the week beginning December 5th 2022.

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

There are more complete examples [here](./examples).

## Installation

`textual-autocomplete` can be installed from PyPI using your favourite dependency
manager.

## Usage

### Wrapping your `Input`

As shown in the quickstart, you can wrap the Textual builtin `Input` widget with
`AutoComplete`, and supply a `Dropdown`. 
The `AutoComplete` manages communication between the `Input` and the `Dropdown`.
The `Dropdown` is the widget you see on screen, as you type into the input.

### Supplying data to `Dropdown`

You can supply the data for the dropdown via a list or a callback function.

#### Using a list

The easiest way to use textual-autocomplete is to pass in a list of `DropdownItem`s, 
as shown in the quickstart.

#### Using a callable

Instead of passing a list of `DropdownItems`, you can supply a callback function
which will be called with the current value and cursor position in the input.

See [here](./examples/custom_meta.py) for a usage example.

### Keyboard control

- Press the Up/Down arrow keys to navigate.
- Press Enter to select the item in the dropdown and fill it in.
- Press Tab to fill in the selected item, and move focus.
- Press Esc to hide the dropdown.
- Press the Up/Down arrow keys to force the dropdown to appear.

### Styling

The `Dropdown` itself can be styled using Textual CSS.

For more fine-grained control over styling, you can target the following CSS classes:

- `.autocomplete--highlight-match`: the highlighted portion of a matching item
- `.autocomplete--selection-cursor`: the item the selection cursor is on
- `.autocomplete--left-column`: the left metadata column, if it exists
- `.autocomplete--right-column`: the right metadata column, if it exists

The [examples directory](./examples) contains multiple examples of custom styling.

### Messages

When you select an item in the dropdown, a `Dropdown.Selected` event is emitted.

You can declare a handler for this event `on_dropdown_selected(self, event)` to respond
to an item being selected.

An item is selected when it's highlighted in the dropdown, and you press Enter or Tab.
