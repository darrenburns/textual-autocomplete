"""A two-column autocomplete example with heavy styling."""

from textual.app import App, ComposeResult
from textual.content import Content
from textual.widgets import Input, Label

from textual_autocomplete import AutoComplete, DropdownItem
from examples._headers import headers

# Define a mapping of sections to colors
SECTION_COLORS: dict[str, str] = {
    "Authentication": "$text-success",
    "Caching": "$text-primary",
    "Conditionals": "$text-warning",
    "Connection management": "$text-error",
    "Content negotiation": "$text-success",
    "Controls": "$text-accent",
    "Cookies": "$text-warning",
    "CORS": "$text-error",
    # Add fallback color for any other sections
    "default": "$foreground",
}

# Create dropdown items with two columns: rank and language name
CANDIDATES = [
    DropdownItem(
        Content.styled(
            str(header["name"]),
            style=SECTION_COLORS.get(
                str(header.get("section", "default")), SECTION_COLORS["default"]
            ),
        ),  # Main text to be completed with color based on section
        prefix=Content.from_markup(
            "[$text-primary on $primary-muted] $number", number=f"{i:<3}"
        ),  # Prefix showing rank, styled with Textual markup!
    )
    for i, header in enumerate(headers)
]


class TwoColumnAutoCompleteExample(App[None]):
    def compose(self) -> ComposeResult:
        yield Label("Start typing an HTTP header name:")
        text_input = Input(placeholder="Type here...")
        yield text_input

        yield AutoComplete(
            target=text_input,  # The widget to attach autocomplete to
            candidates=CANDIDATES,  # The list of completion candidates
        )


if __name__ == "__main__":
    app = TwoColumnAutoCompleteExample()
    app.run()
