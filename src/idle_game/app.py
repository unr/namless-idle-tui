"""Main Textual application for Emotion Merchant idle game."""

import time
from typing import Optional
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.timer import Timer

from src.idle_game.engine.save_manager import SaveManager
from src.idle_game.engine.game_loop import GameLoop
from src.idle_game.models.game_state import GameState
from src.idle_game.screens.game_screen import GameScreen
from src.idle_game.screens.alchemy_screen import AlchemyScreen
from src.idle_game.screens.customer_screen import CustomerScreen


class IdleGameApp(App[None]):
    """Emotion Merchant - An idle game about trading emotions."""

    # App Configuration
    TITLE = "Emotion Merchant"
    SUB_TITLE = "Trade emotions, serve customers, discover meaning"
    CSS_PATH = "game.tcss"

    # Key Bindings
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("s", "save_game", "Save", priority=True),
        Binding("p", "toggle_pause", "Pause"),
        Binding("a", "show_alchemy", "Alchemy"),
        Binding("c", "show_customers", "Customers"),
        Binding("m", "show_market", "Market"),
        Binding("?", "help", "Help"),
    ]

    def __init__(self) -> None:
        """Initialize the application."""
        super().__init__()

        # Game state management
        self.game_state: GameState = GameState()
        self.save_manager: SaveManager = SaveManager()
        self.game_loop: GameLoop = GameLoop(self.game_state)

        # Timing for delta calculations
        self.last_tick_time: float = time.time()

        # Timers
        self.autosave_timer: Optional[Timer] = None
        self.game_loop_timer: Optional[Timer] = None

        # State flags
        self.is_paused: bool = False

    def on_mount(self) -> None:
        """Called when app is mounted. Set up timers and load save."""
        # Load saved game
        self._load_game()

        # Start autosave timer (every 10 seconds)
        self.autosave_timer = self.set_interval(10.0, self._autosave)

        # Start game loop timer (10 FPS = 0.1 seconds per tick)
        self.game_loop_timer = self.set_interval(0.1, self._game_tick)

        # Push the main game screen with game state
        self.push_screen(GameScreen(self.game_state, self.game_loop))

        self.notify("Welcome to Emotion Merchant!", severity="information")

    def on_unmount(self) -> None:
        """Called when app is unmounted. Save game before exit."""
        self._save_game()

    def _load_game(self) -> None:
        """Load the saved game state."""
        try:
            if self.save_manager.load_game(self.game_state):
                self.notify("Game loaded!", severity="information")
            else:
                self.notify("Starting new game", severity="information")
        except Exception as e:
            self.notify(f"Failed to load game: {e}", severity="error")

    def _save_game(self) -> None:
        """Save the current game state."""
        try:
            if self.save_manager.save_game(self.game_state):
                pass  # Silent save, don't spam notifications
        except Exception as e:
            self.notify(f"Failed to save game: {e}", severity="error")

    def _autosave(self) -> None:
        """Periodic autosave callback."""
        if not self.is_paused:
            self._save_game()

    def _game_tick(self) -> None:
        """Main game loop tick - updates game state."""
        if not self.is_paused:
            # Calculate delta time
            current_time = time.time()
            delta_time = current_time - self.last_tick_time
            self.last_tick_time = current_time

            # Update game logic
            self.game_loop.update(delta_time)

    # Action handlers

    def action_quit(self) -> None:
        """Quit the application."""
        self._save_game()
        self.exit()

    def action_save_game(self) -> None:
        """Manually save the game."""
        self._save_game()
        self.notify("Game saved!", severity="information")

    def action_toggle_pause(self) -> None:
        """Toggle game pause state."""
        self.is_paused = not self.is_paused
        self.game_state.game_paused = self.is_paused
        status = "Paused" if self.is_paused else "Resumed"
        self.notify(f"Game {status}", severity="information")

    def action_show_alchemy(self) -> None:
        """Show the alchemy screen."""
        try:
            self.push_screen(AlchemyScreen(self.game_state))
        except Exception as e:
            self.notify(f"Error loading alchemy screen: {e}", severity="error")

    def action_show_customers(self) -> None:
        """Show the customer queue screen."""
        try:
            self.push_screen(CustomerScreen(self.game_state))
        except Exception as e:
            self.notify(f"Error loading customer screen: {e}", severity="error")

    def action_show_market(self) -> None:
        """Show the market/shop screen."""
        # TODO: Implement shop screen
        self.notify("Market system coming soon!", severity="warning")

    def action_help(self) -> None:
        """Show help information."""
        help_text = """
        EMOTION MERCHANT - HELP

        Controls:
        q - Quit game
        s - Save game
        p - Pause/Resume
        a - Alchemy screen
        c - Customer queue
        m - Market
        ? - This help

        How to Play:
        1. Click to harvest Smiles
        2. Serve customers to unlock emotions
        3. Mix recipes in the alchemy lab
        4. Manage storage and purity
        5. Build your emotion empire!
        """
        self.notify(help_text, severity="information", timeout=10)


def main() -> None:
    """Entry point for the application."""
    app = IdleGameApp()
    app.run()


if __name__ == "__main__":
    main()
