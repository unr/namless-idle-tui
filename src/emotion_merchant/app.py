"""Main application for Emotion Merchant TUI game."""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Vertical, Container
from textual.binding import Binding
from textual import work
from decimal import Decimal
import asyncio
from pathlib import Path

from .game.state import GameStateManager
from .game.production import ProductionEngine
from .game.customers import CustomerManager
from .game.resources import EmotionTier
from .widgets.resource_panel import ResourcePanel
from .widgets.clicker import ClickerWidget
from .widgets.customer_panel import CustomerPanel


class EmotionMerchantApp(App):
    """Emotion Merchant - An idle game about harvesting and trading emotions."""

    TITLE = "Emotion Merchant"
    SUB_TITLE = "Trade in the currency of feelings"
    CSS_PATH = Path(__file__).parent / "styles" / "main.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("space", "click", "Harvest"),
        Binding("t", "trade", "Trade"),
        Binding("s", "save", "Save"),
        Binding("p", "pause", "Pause"),
    ]

    def __init__(self):
        """Initialize the application."""
        super().__init__()
        self.state_manager = GameStateManager()
        self.production_engine = ProductionEngine(self.state_manager)
        self.customer_manager = CustomerManager(self.state_manager)
        self.paused = False
        self._tick_rate = 0.1  # 10 ticks per second

    def compose(self) -> ComposeResult:
        """Compose the application UI."""
        yield Header()

        with Container(id="main-container"):
            # Left panel - Resources
            with Vertical(id="left-panel"):
                yield ResourcePanel(self.state_manager, id="resource-panel")

            # Center panel - Main game area
            with Vertical(id="center-panel"):
                yield ClickerWidget(
                    self.state_manager,
                    on_click=self._handle_click,
                    id="clicker"
                )
                yield Static(id="game-info")

            # Right panel - Customers
            with Vertical(id="right-panel"):
                yield CustomerPanel(self.customer_manager, id="customer-panel")

        yield Footer()

    def on_mount(self):
        """Initialize game on mount."""
        self._start_game_loop()
        self._refresh_display()

        # Subscribe to state changes
        self.state_manager.subscribe(self._on_state_change)

    @work(exclusive=True)
    async def _start_game_loop(self):
        """Main game loop running in background."""
        while True:
            if not self.paused:
                self.production_engine.tick(self._tick_rate)
                self._check_customer_events()
                self._refresh_display()
            await asyncio.sleep(self._tick_rate)

    def _handle_click(self) -> Decimal:
        """Handle harvest click.

        Returns:
            Amount of Smiles harvested
        """
        return self.state_manager.click_harvest()

    def _on_state_change(self, event: str, data: any):
        """Handle state change events.

        Args:
            event: Name of the event that occurred
            data: Event data
        """
        if event == "resource_unlocked":
            self.notify(f"Unlocked: {data['tier'].name}!")
        elif event == "emotion_unlocked":
            self.notify(f"Discovered: {data['emotion'].name}!")

    def _check_customer_events(self):
        """Check for tutorial and queue events."""
        customer_panel = self.query_one("#customer-panel", CustomerPanel)
        customer_panel.refresh_queue()

    def _refresh_display(self):
        """Refresh all UI components."""
        # Update resource panel
        resource_panel = self.query_one("#resource-panel", ResourcePanel)
        resource_panel.refresh_all()

        # Update production rates in resource displays
        state = self.state_manager.state
        for tier in EmotionTier:
            resource = state.resources[tier]
            if resource.unlocked:
                rate = self.production_engine.get_total_production_rate(tier)
                display = resource_panel.resource_displays.get(tier)
                if display:
                    display.update_display(
                        amount=resource.amount,
                        capacity=resource.storage_capacity,
                        rate=rate,
                        purity=resource.purity
                    )

        # Update game info
        info = self.query_one("#game-info", Static)
        info.update(self._format_game_info())

    def _format_game_info(self) -> str:
        """Format game info display.

        Returns:
            Formatted string with game statistics
        """
        state = self.state_manager.state
        return f"""
╔═══════════════════════════════════════╗
║  Customers Served: {state.customers_served}
║  Reputation: {'★' * int(state.reputation)}{'☆' * (5 - int(state.reputation))}
║  Ethical Score: {state.ethical_score:.1f}%
║  Play Time: {state.play_time_seconds / 60:.1f} min
╚═══════════════════════════════════════╝
"""

    def action_click(self):
        """Handle space bar click action."""
        clicker = self.query_one("#clicker", ClickerWidget)
        clicker.handle_click(None)

    def action_trade(self):
        """Handle trade action for tutorial customers."""
        customer_panel = self.query_one("#customer-panel", CustomerPanel)
        if hasattr(customer_panel, '_current_tutorial') and customer_panel._current_tutorial:
            success = self.customer_manager.serve_tutorial_customer(
                customer_panel._current_tutorial
            )
            if success:
                self.notify("Trade complete!")
                customer_panel.refresh_queue()
            else:
                self.notify("Not enough resources!", severity="warning")

    def action_save(self):
        """Save game state."""
        # Implement save logic
        save_path = Path.home() / ".emotion_merchant" / "save.json"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.state_manager.save_to_file(str(save_path))
            self.notify("Game saved!")
        except Exception as e:
            self.notify(f"Save failed: {e}", severity="error")

    def action_pause(self):
        """Toggle pause state."""
        self.paused = not self.paused
        status = "PAUSED" if self.paused else "RESUMED"
        self.notify(f"Game {status}")


def main():
    """Entry point for the application."""
    app = EmotionMerchantApp()
    app.run()


if __name__ == "__main__":
    main()
