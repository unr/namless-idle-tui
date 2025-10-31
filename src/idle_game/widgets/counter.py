from textual.widgets import Static
from textual.reactive import reactive
from ..models import GameNumber


class CounterDisplay(Static):
    """Display current counter value with animations"""

    value: reactive[GameNumber] = reactive(GameNumber())
    increment_text: reactive[str] = reactive("")

    def render(self) -> str:
        lines = [
            "[bold cyan]Resources:[/bold cyan]",
            f"[bold yellow]{self.value.format()}[/bold yellow]",
        ]
        if self.increment_text:
            lines.append(f"[green]{self.increment_text}[/green]")
        return "\n".join(lines)

    def show_increment(self, amount: GameNumber):
        """Show floating increment text"""
        self.increment_text = f"+{amount.format()}"
        self.set_timer(1.0, self.clear_increment)

    def clear_increment(self):
        self.increment_text = ""
