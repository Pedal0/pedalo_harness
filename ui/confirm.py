import json

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class ConfirmScreen(ModalScreen[str]):

    CSS = """
    ConfirmScreen { align: center middle; }
    #box { width: 80; max-height: 16; border: round yellow; padding: 1 2; background: $surface; }
    #cmd { color: $text; margin-bottom: 1; }
    Horizontal { align-horizontal: center; height: auto; }
    Button { margin: 0 1; }
    """

    def __init__(self, name: str, arguments: dict):
        super().__init__()
        self.tool_name = name
        self.arguments = arguments

    def compose(self) -> ComposeResult:
        args = json.dumps(self.arguments, ensure_ascii=False)
        if len(args) > 300:
            args = args[:300] + "…"
        with Vertical(id="box"):
            yield Static(f"[b]{self.tool_name}[/b] requests execution:")
            yield Static(args, id="cmd")
            with Horizontal():
                yield Button("Yes", id="y", variant="success")
                yield Button("No", id="n", variant="error")
                yield Button("Always", id="a", variant="warning")

    def on_button_pressed(self, event: Button.Pressed):
        self.dismiss(event.button.id)