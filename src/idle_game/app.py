from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, Label, Button
from textual.reactive import reactive
from textual.timer import Timer
from textual.screen import ModalScreen
from datetime import datetime
from decimal import Decimal
from typing import Optional

from .models import GameState
from .database import GameDatabase
from .widgets.counter import CounterDisplay
from .widgets.clicker import ClickButton


class IdleGame(App):
    """Main idle game application"""

    CSS_PATH = "styles/main.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "save", "Save Game"),
        ("r", "reset", "Reset Game"),
        ("p", "toggle_updates", "Pause/Resume"),
    ]

    game_state: reactive[GameState] = reactive(GameState())
    updates_enabled: reactive[bool] = reactive(False)

    def __init__(self):
        super().__init__()
        self.db = GameDatabase()
        self.update_timer: Optional[Timer] = None
        self.save_timer: Optional[Timer] = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main-container"):
            with Vertical(id="game-area"):
                yield CounterDisplay(id="counter")
                yield ClickButton()
                yield Label("[dim]Auto: +1/sec[/dim]", id="rate-display")
                yield Button("▶️ Enable Updates", id="toggle-updates", variant="success")
        yield Footer()

    async def on_mount(self):
        """Initialize game on mount"""
        await self.db.initialize()

        # Load saved state
        saved_state = await self.db.load_state()
        if saved_state:
            # Calculate offline earnings
            now = datetime.now()
            seconds_offline = (now - saved_state.last_save).total_seconds()
            if seconds_offline > 0:
                offline_earnings = saved_state.calculate_offline_earnings(seconds_offline)
                saved_state.counter = saved_state.counter.add(offline_earnings.value)
                self.notify(
                    f"Welcome back! You earned {offline_earnings.format()} while away!",
                    severity="information",
                )
            saved_state.last_update = now
            self.game_state = saved_state

        # Start timers
        self.update_timer = self.set_interval(0.1, self.game_tick)
        self.save_timer = self.set_interval(10.0, self.auto_save)

    def game_tick(self):
        """Main game loop tick"""
        if not self.updates_enabled:
            return

        now = datetime.now()
        increment = self.game_state.update(now)

        # Update display
        counter_widget = self.query_one("#counter", CounterDisplay)
        counter_widget.value = self.game_state.counter

        # Show increment if significant
        if increment.value >= Decimal("0.1"):
            counter_widget.show_increment(increment)

    async def auto_save(self):
        """Auto-save every 10 seconds"""
        await self.db.save_state(self.game_state)

    async def on_click_button_clicked(self, event: ClickButton.Clicked):
        """Handle manual clicks"""
        increment = self.game_state.click()

        # Update and show increment
        counter_widget = self.query_one("#counter", CounterDisplay)
        counter_widget.value = self.game_state.counter
        counter_widget.show_increment(increment)

    def on_button_pressed(self, event: Button.Pressed):
        """Handle button presses"""
        if event.button.id == "toggle-updates":
            self.action_toggle_updates()

    async def action_save(self):
        """Manual save action"""
        await self.db.save_state(self.game_state)
        self.notify("Game saved!", severity="information")

    def action_toggle_updates(self):
        """Toggle game updates on/off"""
        self.updates_enabled = not self.updates_enabled
        button = self.query_one("#toggle-updates", Button)
        if self.updates_enabled:
            button.label = "⏸️ Disable Updates"
            button.variant = "error"
            self.notify("Game updates enabled", severity="information")
        else:
            button.label = "▶️ Enable Updates"
            button.variant = "success"
            self.notify("Game updates disabled", severity="warning")

    async def action_reset(self):
        """Reset game with confirmation"""

        class ConfirmReset(ModalScreen):
            """Modal dialog for reset confirmation"""

            def compose(self):
                yield Container(
                    Static("⚠️ Reset Game?", id="reset-title"),
                    Static(
                        "This will delete all progress and cannot be undone!", id="reset-warning"
                    ),
                    Horizontal(
                        Button("Cancel", variant="default", id="cancel"),
                        Button("Reset", variant="error", id="confirm"),
                        id="reset-buttons",
                    ),
                    id="reset-dialog",
                )

            def on_button_pressed(self, event):
                if event.button.id == "confirm":
                    self.dismiss(True)
                else:
                    self.dismiss(False)

        # Show confirmation dialog
        if await self.push_screen_wait(ConfirmReset()):
            # Reset the game state
            self.game_state = GameState()
            await self.db.save_state(self.game_state)

            # Update UI
            counter_widget = self.query_one("#counter", CounterDisplay)
            counter_widget.value = self.game_state.counter

            self.notify("Game reset! Starting fresh.", severity="warning")

    async def on_unmount(self):
        """Clean up on exit"""
        if self.update_timer:
            self.update_timer.stop()
        if self.save_timer:
            self.save_timer.stop()
        await self.db.save_state(self.game_state)


def main():
    """Entry point"""
    app = IdleGame()
    app.run()


if __name__ == "__main__":
    main()
