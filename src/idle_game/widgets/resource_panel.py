"""Resource panel widget displaying all emotions and their properties."""

from decimal import Decimal
from typing import Optional

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static, ProgressBar, Label
from textual.containers import Container, Vertical, Horizontal


class ResourceDisplay(Static):
    """Individual resource display showing amount, storage, and purity."""

    # Reactive attributes that auto-update the UI
    amount: reactive[Decimal] = reactive(Decimal(0))
    capacity: reactive[Decimal] = reactive(Decimal(100))
    purity: reactive[float] = reactive(100.0)
    production_rate: reactive[Decimal] = reactive(Decimal(0))
    is_locked: reactive[bool] = reactive(True)

    def __init__(
        self,
        name: str,
        symbol: str,
        tier: int,
        *args,
        **kwargs
    ) -> None:
        """Initialize a resource display.

        Args:
            name: Name of the emotion (e.g., "Smiles", "Joy")
            symbol: Unicode symbol for the emotion (e.g., "☺", "❤")
            tier: Tier level (0-9)
        """
        super().__init__(*args, **kwargs)
        self.emotion_name = name
        self.symbol = symbol
        self.tier = tier

    def compose(self) -> ComposeResult:
        """Compose the resource display layout."""
        with Container(classes="resource-item"):
            # Header line: symbol, name, amount
            with Horizontal(classes="resource-header"):
                yield Static(self.symbol, classes="resource-symbol")
                yield Static(self.emotion_name, classes="resource-name")
                yield Static(self._format_amount(self.amount), classes="resource-amount")

            # Storage bar and capacity
            with Horizontal(classes="resource-storage"):
                yield ProgressBar(
                    total=100,
                    show_percentage=False,
                    classes="storage-bar"
                )
                yield Static(
                    self._format_capacity(),
                    classes="capacity-text"
                )

            # Bottom line: purity and production rate
            with Horizontal(classes="resource-info"):
                yield Static(
                    self._format_purity(),
                    classes="purity-indicator"
                )
                yield Static(
                    self._format_production(),
                    classes="production-rate"
                )

    def watch_amount(self, new_amount: Decimal) -> None:
        """Update display when amount changes."""
        if not self.is_mounted:
            return
        try:
            amount_widget = self.query_one(".resource-amount", Static)
            amount_widget.update(self._format_amount(new_amount))

            # Update storage bar
            if self.capacity > 0:
                percentage = float(new_amount / self.capacity * 100)
                progress_bar = self.query_one(".storage-bar", ProgressBar)
                progress_bar.update(progress=min(percentage, 100))

                # Update capacity text
                capacity_widget = self.query_one(".capacity-text", Static)
                capacity_widget.update(self._format_capacity())
        except Exception:
            pass

    def watch_purity(self, new_purity: float) -> None:
        """Update display when purity changes."""
        if not self.is_mounted:
            return
        try:
            purity_widget = self.query_one(".purity-indicator", Static)
            purity_widget.update(self._format_purity())
        except Exception:
            pass

    def watch_production_rate(self, new_rate: Decimal) -> None:
        """Update display when production rate changes."""
        if not self.is_mounted:
            return
        try:
            production_widget = self.query_one(".production-rate", Static)
            production_widget.update(self._format_production())
        except Exception:
            pass

    def watch_is_locked(self, locked: bool) -> None:
        """Update display when lock state changes."""
        if locked:
            self.add_class("locked")
        else:
            self.remove_class("locked")

    def _format_amount(self, amount: Decimal) -> str:
        """Format large numbers with K, M, B, T notation.

        Args:
            amount: The amount to format

        Returns:
            Formatted string (e.g., "1.23K", "45.6M")
        """
        if self.is_locked:
            return "🔒 Locked"

        amount_float = float(amount)

        if amount_float >= 1_000_000_000_000:  # Trillion
            return f"{amount_float / 1_000_000_000_000:.2f}T"
        elif amount_float >= 1_000_000_000:  # Billion
            return f"{amount_float / 1_000_000_000:.2f}B"
        elif amount_float >= 1_000_000:  # Million
            return f"{amount_float / 1_000_000:.2f}M"
        elif amount_float >= 1_000:  # Thousand
            return f"{amount_float / 1_000:.2f}K"
        else:
            return f"{amount_float:.1f}"

    def _format_capacity(self) -> str:
        """Format the capacity display.

        Returns:
            Formatted string showing current/max
        """
        if self.is_locked:
            return ""

        return f"{self._format_amount(self.amount)}/{self._format_amount(self.capacity)}"

    def _format_purity(self) -> str:
        """Format the purity indicator.

        Returns:
            Purity percentage with diamond indicators
        """
        if self.is_locked:
            return ""

        diamonds = "◊" * (int(self.purity / 20) + 1)  # 1-5 diamonds
        return f"{diamonds} {self.purity:.0f}%"

    def _format_production(self) -> str:
        """Format the production rate display.

        Returns:
            Production rate per second
        """
        if self.is_locked or self.production_rate == 0:
            return ""

        rate_float = float(self.production_rate)
        if rate_float >= 1000:
            return f"↑ {rate_float / 1000:.1f}K/s"
        else:
            return f"↑ {rate_float:.1f}/s"


class ResourcePanel(Widget):
    """Panel displaying all emotion resources."""

    def __init__(self, game_state=None, game_loop=None, *args, **kwargs) -> None:
        """Initialize the resource panel."""
        super().__init__(*args, **kwargs)
        self.game_state = game_state
        self.game_loop = game_loop

        # Define all emotion tiers (based on resources.md)
        self.emotions = [
            {"name": "Smiles", "symbol": "☺", "tier": 0},
            {"name": "Joy", "symbol": "❤", "tier": 1},
            {"name": "Love", "symbol": "💕", "tier": 2},
            {"name": "Nostalgia", "symbol": "❖", "tier": 3},
            {"name": "Serenity", "symbol": "◉", "tier": 4},
            {"name": "Euphoria", "symbol": "✧", "tier": 5},
            {"name": "Compassion", "symbol": "❀", "tier": 6},
            {"name": "Wisdom", "symbol": "◈", "tier": 7},
            {"name": "Transcendence", "symbol": "✵", "tier": 8},
            {"name": "Singularity", "symbol": "∞", "tier": 9},
        ]

        self.resource_displays: dict[str, ResourceDisplay] = {}

    def compose(self) -> ComposeResult:
        """Compose the resource panel layout."""
        with Vertical(id="resource-panel"):
            # Create a display for each emotion
            for emotion in self.emotions:
                resource_display = ResourceDisplay(
                    name=emotion["name"],
                    symbol=emotion["symbol"],
                    tier=emotion["tier"]
                )
                self.resource_displays[emotion["name"]] = resource_display
                yield resource_display

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        # Initialize with Smiles unlocked, others locked
        smiles = self.resource_displays.get("Smiles")
        if smiles:
            smiles.is_locked = False
            smiles.amount = Decimal(0)
            smiles.capacity = Decimal(100)
            smiles.purity = 100.0

    def update_resource(
        self,
        name: str,
        amount: Optional[Decimal] = None,
        capacity: Optional[Decimal] = None,
        purity: Optional[float] = None,
        production_rate: Optional[Decimal] = None,
        is_locked: Optional[bool] = None
    ) -> None:
        """Update a specific resource's values.

        Args:
            name: Name of the emotion to update
            amount: New amount value
            capacity: New capacity value
            purity: New purity percentage
            production_rate: New production rate
            is_locked: New lock state
        """
        resource = self.resource_displays.get(name)
        if not resource:
            return

        if amount is not None:
            resource.amount = amount
        if capacity is not None:
            resource.capacity = capacity
        if purity is not None:
            resource.purity = purity
        if production_rate is not None:
            resource.production_rate = production_rate
        if is_locked is not None:
            resource.is_locked = is_locked

    def unlock_resource(self, name: str) -> None:
        """Unlock a resource for the first time.

        Args:
            name: Name of the emotion to unlock
        """
        self.update_resource(name, is_locked=False, amount=Decimal(0))

    def update_from_game_state(self) -> None:
        """Update all resource displays from game state."""
        if not self.game_state:
            return

        # Update each resource from game_state.resources
        for emotion_name, emotion_resource in self.game_state.resources.items():
            # Calculate production rate using game loop
            production_rate = Decimal(0)
            if self.game_loop:
                production_rate = self.game_loop.get_production_rate(emotion_name)

            self.update_resource(
                name=emotion_name,
                amount=emotion_resource.amount,
                capacity=emotion_resource.capacity,
                purity=emotion_resource.purity,
                production_rate=production_rate,
                is_locked=(emotion_name not in self.game_state.unlocked_emotions)
            )
