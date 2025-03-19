# textual-autocomplete

A simple autocomplete dropdown library for [Textual](https://github.com/textualize/textual) `Input` widgets.

Compatible with **Textual 2.0 and above**.

## Installation

I recommend using [uv](https://docs.astral.sh/uv/) to manage your dependencies and install `textual-autocomplete`:

```bash
uv add textual-autocomplete
```

If you prefer `pip`, `poetry`, or something else, those will work too.

## Quick Start

Here's the simplest possible way to add autocomplete to your Textual app:

```python
from textual.app import App, ComposeResult
from textual.widgets import Input
from textual_autocomplete import AutoComplete, DropdownItem

class ColorFinder(App):
    def compose(self) -> ComposeResult:
        # Create a standard Textual input
        text_input = Input(placeholder="Type a color...")
        yield text_input
        
        # Add an autocomplete to the same screen, and pass in the input widget.
        yield AutoComplete(
            text_input,  # Target input widget
            candidates=["Red", "Green", "Blue", "Yellow", "Purple", "Orange"]
        )

if __name__ == "__main__":
    app = ColorFinder()
    app.run()
```

That's it! As you type in the input field, matching options will appear in a dropdown below.

## Core Features

- 🔍 **Fuzzy matching** - Find matches even with typos
- ⌨️ **Keyboard navigation** - Arrow keys, Tab, Enter, and Escape
- 🎨 **Rich styling options** - Customizable highlighting and appearance
- 📝 **Dynamic content** - Supply items as a list or from a callback function

## Examples

### With Left Metadata Column

Add a metadata column (like icons) to provide additional context.
These columns are display-only, and do not influence the search process.

```python
from textual.app import App, ComposeResult
from textual.widgets import Input
from textual_autocomplete import AutoComplete, DropdownItem

# Create dropdown items with a left metadata column.
ITEMS = [
    DropdownItem(main="Python", prefix="🐍"),
    DropdownItem(main="JavaScript", prefix="📜"),
    DropdownItem(main="TypeScript", prefix="🔷"),
    DropdownItem(main="Java", prefix="☕"),
]

class LanguageSearcher(App):
    def compose(self) -> ComposeResult:
        text_input = Input(placeholder="Programming language...")
        yield text_input
        yield AutoComplete(text_input, candidates=ITEMS)

if __name__ == "__main__":
    app = LanguageSearcher()
    app.run()
```

### Styled Two-Column Layout

Add rich styling to your metadata columns using [Textual markup](https://textual.textualize.io/guide/content/#markup).

```python
from textual.app import App, ComposeResult
from textual.content import Content
from textual.widgets import Input, Label
from textual_autocomplete import AutoComplete, DropdownItem

# Languages with their popularity rank
LANGUAGES_WITH_RANK = [
    (1, "Python"),
    (2, "JavaScript"),
    (3, "Java"),
    (4, "C++"),
    (5, "TypeScript"),
    (6, "Go"),
    (7, "Ruby"),
    (8, "Rust"),
]

# Create dropdown items with styled rank in prefix
CANDIDATES = [
    DropdownItem(
        language,  # Main text to be completed
        prefix=Content.from_markup(
            f"[$text-primary on $primary-muted] {rank:>2} "
        ),  # Prefix with styled rank
    )
    for rank, language in LANGUAGES_WITH_RANK
]

class LanguageSearcher(App):
    def compose(self) -> ComposeResult:
        yield Label("Start typing a programming language:")
        text_input = Input(placeholder="Type here...")
        yield text_input
        yield AutoComplete(target=text_input, candidates=CANDIDATES)

if __name__ == "__main__":
    app = LanguageSearcher()
    app.run()
```

## Keyboard Controls

- **↑/↓** - Navigate through options
- **↓** - Summon the dropdown
- **Enter/Tab** - Complete the selected option
- **Escape** - Hide dropdown

## Styling

The dropdown can be styled using Textual CSS:

```css
    AutoComplete {
        /* Customize the dropdown */
        & AutoCompleteList {
            max-height: 6;  /* The number of lines before scrollbars appear */
            color: $text-primary;  /* The color of the text */
            background: $primary-muted;  /* The background color of the dropdown */
            border-left: wide $success;  /* The color of the left border */
        }

        /* Customize the matching substring highlighting */
        & .autocomplete--highlight-match {
            color: $text-accent;
            text-style: bold;
        }

        /* Customize the text the cursor is over */
        & .option-list--option-highlighted {
            color: $text-success;
            background: $error 50%;  /* 50% opacity, blending into background */
            text-style: italic;  
        }
    }
```

Here's what that looks like when applied:

<img width="226" alt="image" src="https://github.com/user-attachments/assets/3fae3ecf-fdd3-4ff5-ac37-7ef3088c596e" />

By using Textual CSS like in the example above, you can ensure the shades of colors remain
consistent across different themes. Here's the same dropdown with the Textual app theme switched to `gruvbox`:

<img width="234" alt="image" src="https://github.com/user-attachments/assets/6bc4804d-7a4b-41ab-bba9-5745d87648b9" />

### Styling the prefix

You can style the prefix using Textual Content markup.

```python
DropdownItem(
    main="Python",
    prefix=Content.from_markup(
        "[$text-success on $success-muted] 🐍"
    ),
)
```

## Completing Paths

`textual-autocomplete` includes a `PathAutoComplete` widget that can be used to autocomplete filesystem paths.

```python
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Button, Input, Label

from textual_autocomplete import PathAutoComplete

class FileSystemPathCompletions(App[None]):
    def compose(self) -> ComposeResult:
        yield Label("Choose a file!", id="label")
        input_widget = Input(placeholder="Enter a path...")
        yield input_widget
        yield PathAutoComplete(target=input_widget, path="../textual")


if __name__ == "__main__":
    app = FileSystemPathCompletions()
    app.run()
```

Here's what that looks like in action:

https://github.com/user-attachments/assets/25b80e34-0a35-4962-9024-f2dab7666689

`PathAutoComplete` has a bunch of parameters that can be used to customize the behavior - check the docstring for more details. It'll also cache directory contents after reading them once - but you can clear the cache if you need to using the `clear_directory_cache` method.

## Dynamic Data with Callbacks

Instead of supplying a static list of candidates, you can supply a callback function which returns a list of `DropdownItem` (candidates) that will be searched against.

This callback function will be called anytime the text in the target input widget changes or the cursor position changes (and since the cursor position changes when the user inserts text, you can expect 2 calls to this function for most keystrokes - cache accordingly if this is a problem).

The app below displays the length of the text in the input widget in the prefix of the dropdown items.

```python
from textual.app import App, ComposeResult
from textual.widgets import Input

from textual_autocomplete import AutoComplete
from textual_autocomplete._autocomplete import DropdownItem, TargetState


class DynamicDataApp(App[None]):
    def compose(self) -> ComposeResult:
        input_widget = Input()
        yield input_widget
        yield AutoComplete(input_widget, candidates=self.candidates_callback)

    def candidates_callback(self, state: TargetState) -> list[DropdownItem]:
        left = len(state.text)
        return [
            DropdownItem(item, prefix=f"{left:>2} ")
            for item in [
                "Apple",
                "Banana",
                "Cherry",
                "Orange",
                "Pineapple",
                "Strawberry",
                "Watermelon",
            ]
        ]


if __name__ == "__main__":
    app = DynamicDataApp()
    app.run()
```

Notice the count displayed in the prefix increment and decrement based on the character count in the input.

![Screen Recording 2025-03-18 at 18 26 42](https://github.com/user-attachments/assets/ca0e039b-8ae0-48ac-ba96-9ec936720ded)

## Customizing Behavior

If you need custom behavior, `AutoComplete` is can be subclassed.

A good example of how to subclass and customize behavior is the `PathAutoComplete` widget, which is a subclass of `AutoComplete`.

Some methods you may want to be aware of which you can override:

- `get_candidates`: Return a list of `DropdownItem` objects - called each time the input changes or the cursor position changes. Note that if you're overriding this in a subclass, you'll need to make sure that the `get_candidates` parameter passed into the `AutoComplete` constructor is set to `None` - this tells `textual-autocomplete` to use the subclassed method instead of the default.
- `get_search_string`: The string that will be used to filter the candidates. You may wish to only use a portion of the input text to filter the candidates rather than the entire text.
- `apply_completion`: Apply the completion to the target input widget. Receives the value the user selected from the dropdown and updates the `Input` directly using it's API.
- `post_completion`: Called when a completion is selected. Called immediately after `apply_completion`. The default behaviour is just to hide the completion dropdown (after performing a completion, we want to immediately hide the dropdown in the default case).

## More Examples

Check out the [examples directory](./examples) for more runnable examples.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests on GitHub.
