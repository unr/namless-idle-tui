"""Main gameplay screen for Emotion Merchant."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static, Label

from src.idle_game.widgets.resource_panel import ResourcePanel
from src.idle_game.widgets.action_buttons import ActionButtons, HarvestClicked, ProducerPurchased
from src.idle_game.widgets.stat_display import StatDisplay


class GameScreen(Screen):
    """Main game screen showing resources, actions, and stats."""

    BINDINGS = [
        ("escape", "app.toggle_pause", "Pause"),
        ("tab", "focus_next", "Next"),
        ("shift+tab", "focus_previous", "Previous"),
    ]

    def __init__(self, game_state, game_loop, **kwargs):
        """Initialize the game screen with game state.

        Args:
            game_state: The GameState instance
            game_loop: The GameLoop instance
        """
        super().__init__(**kwargs)
        self.game_state = game_state
        self.game_loop = game_loop

    def compose(self) -> ComposeResult:
        """Compose the game screen layout."""
        # Top header
        yield Header()

        # Main game container
        with Container(id="game-container"):
            # Title banner
            with Container(id="title-banner"):
                yield Static("EMOTION MERCHANT", id="game-title")
                yield Static("Trade emotions, serve customers, discover meaning", id="game-subtitle")

            # Main game area - horizontal split
            with Horizontal(id="main-area"):
                # Left panel - Resources
                with Vertical(id="left-panel"):
                    yield Static("Resources", classes="panel-header")
                    with ScrollableContainer(id="resource-scroll"):
                        yield ResourcePanel(game_state=self.game_state, game_loop=self.game_loop)

                # Center panel - Actions and interactions
                with Vertical(id="center-panel"):
                    yield Static("Actions", classes="panel-header")
                    with Container(id="action-container"):
                        yield ActionButtons(game_state=self.game_state)

                    # Space for customer or event display
                    with Container(id="event-container"):
                        yield Static("", id="event-display")

                # Right panel - Statistics and info
                with Vertical(id="right-panel"):
                    yield Static("Statistics", classes="panel-header")
                    with ScrollableContainer(id="stats-scroll"):
                        yield StatDisplay(game_state=self.game_state)

        # Bottom footer with keybindings
        yield Footer()

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Set focus to action buttons for keyboard interaction
        action_buttons = self.query_one(ActionButtons)
        if action_buttons:
            action_buttons.focus()

    def update_event_display(self, message: str) -> None:
        """Update the event display area with a message.

        Args:
            message: The message to display (customer arrival, unlock, etc.)
        """
        event_display = self.query_one("#event-display", Static)
        event_display.update(message)

    def on_harvest_clicked(self, message: HarvestClicked) -> None:
        """Handle harvest button clicks.

        Args:
            message: The HarvestClicked message
        """
        # Perform click in game state
        smiles_earned = self.game_state.perform_click()

        # Update resource panel
        self.refresh_resources()

        # Show feedback
        self.update_event_display(f"☺ Harvested {smiles_earned} Smiles!")

    def on_producer_purchased(self, message: ProducerPurchased) -> None:
        """Handle producer purchase attempts.

        Args:
            message: The ProducerPurchased message containing producer info
        """
        success = self.game_state.purchase_producer(message.emotion_type)

        if success:
            # Update displays
            self.refresh_resources()
            self.refresh_action_buttons()

            # Show feedback
            emotion_name = message.emotion_type.title()
            self.update_event_display(f"✓ Purchased {emotion_name} producer!")
        else:
            # Show error
            self.update_event_display(f"✗ Not enough resources!")

    def refresh_resources(self) -> None:
        """Refresh the resource panel display."""
        resource_panel = self.query_one(ResourcePanel)
        if resource_panel:
            resource_panel.update_from_game_state()

    def refresh_action_buttons(self) -> None:
        """Refresh the action buttons display."""
        action_buttons = self.query_one(ActionButtons)
        if action_buttons:
            action_buttons.update_from_game_state()

    def on_key(self, event) -> None:
        """Handle screen-specific key events."""
        # Additional key handling can be added here
        pass
