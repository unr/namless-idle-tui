"""Click harvesting widget for manual resource collection."""

from decimal import Decimal
from typing import TYPE_CHECKING, Callable

from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.reactive import reactive
from textual.widgets import Button, Label, Static

if TYPE_CHECKING:
    from ..game.state import GameStateManager


class ClickerWidget(Static):
    """Main click harvesting area."""

    DEFAULT_CSS = """
    ClickerWidget {
        height: auto;
        padding: 1;
        border: solid $primary;
    }

    .clicker-button {
        width: 100%;
        height: 5;
        margin: 1;
    }

    .click-info {
        text-align: center;
        margin: 1;
    }
    """

    total_clicks: reactive[int] = reactive(0)
    click_power: reactive[Decimal] = reactive(Decimal("5"))
    last_harvest: reactive[Decimal] = reactive(Decimal("0"))

    def __init__(
        self,
        state_manager: "GameStateManager",
        on_click: Callable[[], Decimal],
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.state_manager = state_manager
        self._on_click = on_click

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("☺ HARVEST SMILES ☺", classes="click-info", id="clicker-title")
            with Center():
                yield Button(
                    "CLICK!",
                    id="harvest-btn",
                    classes="clicker-button",
                    variant="success",
                )
            yield Label("Click Power: 5 ☺", id="click-power-label", classes="click-info")
            yield Label("Total Clicks: 0", id="total-clicks-label", classes="click-info")
            yield Label("", id="last-harvest-label", classes="click-info")

    @on(Button.Pressed, "#harvest-btn")
    def handle_click(self, event: Button.Pressed):
        """Handle harvest button click."""
        harvested = self._on_click()
        self.last_harvest = harvested
        self.total_clicks = self.state_manager.state.total_clicks
        self.click_power = self.state_manager.state.click_power

        # Update display
        self._update_display()

    def _update_display(self):
        """Update all display labels."""
        power_label = self.query_one("#click-power-label", Label)
        power_label.update(f"Click Power: {self.click_power} ☺")

        total_label = self.query_one("#total-clicks-label", Label)
        total_label.update(f"Total Clicks: {self.total_clicks:,}")

        harvest_label = self.query_one("#last-harvest-label", Label)
        if self.last_harvest > 0:
            harvest_label.update(f"+{self.last_harvest} ☺")
