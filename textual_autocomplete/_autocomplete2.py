from textual.widget import Widget
from textual.widgets import Input, TextArea


class AutoComplete(Widget):
    def __init__(
        self,
        target: Input | TextArea,
        dropdown: Dropdown,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )
