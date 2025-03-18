# textual-autocomplete

A simple autocomplete dropdown library for [Textual](https://github.com/textualize/textual) `Input` widgets.

Compatible with **Textual 2.0 and above**.

## Installation

I recommend installing via [uv](https://docs.astral.sh/uv/):

```bash
uv add textual-autocomplete
```

If you prefer `pip`, `poetry`, or something else, those will work too.

## Quick Start

Here's the simplest possible way to add autocomplete to your Textual app:

```python
from textual.app import App, ComposeResult
from textual.widgets import Input
from textual_autocomplete import InputAutoComplete, DropdownItem

class ColorFinder(App):
    def compose(self) -> ComposeResult:
        # Create a standard Textual input
        text_input = Input(placeholder="Type a color...")
        yield text_input
        
        # Add an autocomplete to the same screen, and pass in the input widget.
        yield InputAutoComplete(
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
from textual_autocomplete import InputAutoComplete, DropdownItem

# Create dropdown items with a left metadata column.
ITEMS = [
    DropdownItem(main="Python", left_column="🐍"),
    DropdownItem(main="JavaScript", left_column="📜"),
    DropdownItem(main="TypeScript", left_column="🔷"),
    DropdownItem(main="Java", left_column="☕"),
]

class LanguageSearcher(App):
    def compose(self) -> ComposeResult:
        text_input = Input(placeholder="Programming language...")
        yield text_input
        yield InputAutoComplete(text_input, candidates=ITEMS)

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
from textual_autocomplete import InputAutoComplete, DropdownItem

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

# Create dropdown items with styled rank in left column
CANDIDATES = [
    DropdownItem(
        language,  # Main text to be completed
        left_column=Content.from_markup(
            f"[$text-primary on $primary-muted] {rank} "
        ),  # Left column with styled rank
    )
    for rank, language in LANGUAGES_WITH_RANK
]

class LanguageSearcher(App):
    def compose(self) -> ComposeResult:
        yield Label("Start typing a programming language:")
        text_input = Input(placeholder="Type here...")
        yield text_input
        yield InputAutoComplete(target=text_input, candidates=CANDIDATES)

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
    InputAutoComplete {
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

## Dynamic Data with Callbacks

Instead of supplying a static list of candidates, you can supply a callback function which returns a list of `DropdownItem` (candidates) that will be searched against.

This callback function will be called anytime the text in the target input widget changes.

The app below displays the length of the text in the input widget in the left column of the dropdown items.

```python
from textual.app import App, ComposeResult
from textual.widgets import Input

from textual_autocomplete import InputAutoComplete
from textual_autocomplete._autocomplete import DropdownItem, TargetState


class DynamicDataApp(App[None]):
    def compose(self) -> ComposeResult:
        input_widget = Input()
        yield input_widget
        yield InputAutoComplete(input_widget, candidates=self.get_candidates)

    def get_candidates(self, state: TargetState) -> list[DropdownItem]:
        left = len(state.text)
        return [
            DropdownItem(item, left_column=f"{left:>2} ")
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

Notice the count displayed in the left column increment and decrement based on the character count in the input.

![Screen Recording 2025-03-18 at 18 26 42](https://github.com/user-attachments/assets/ca0e039b-8ae0-48ac-ba96-9ec936720ded)

## Events

Listen for selection events:

```python
from textual.app import App, ComposeResult
from textual.widgets import Input, Label
from textual_autocomplete import InputAutoComplete

class EventApp(App):
    def compose(self) -> ComposeResult:
        self.result = Label("Nothing selected yet")
        yield self.result
        input_widget = Input()
        yield input_widget
        yield InputAutoComplete(input_widget, candidates=["Apple", "Banana", "Cherry"])
    
    def on_input_auto_complete_selected(self, event):
        """Called when an item is selected from the dropdown"""
        self.result.update(f"Selected: {event.value}")
```

## More Examples

Check out the [examples directory](./examples) for more advanced usage patterns, including:

- Color-coded categories
- Dynamic data sources
- Complex filtering logic
- Custom matching algorithms

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests on GitHub.
