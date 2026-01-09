"""Resource panel widget for displaying emotion resources."""

from decimal import Decimal
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Label, ProgressBar, Static

if TYPE_CHECKING:
    from ..game.resources import EmotionTier
    from ..game.state import GameStateManager

# Import will be available at runtime
try:
    from ..game.resources import EMOTION_CONFIGS, EmotionTier
except ImportError:
    # Fallback for type checking
    EMOTION_CONFIGS = {}
    EmotionTier = None


class ResourceDisplay(Static):
    """Display a single resource with amount, storage bar, and rate."""

    amount: reactive[Decimal] = reactive(Decimal("0"))
    storage_percent: reactive[float] = reactive(0.0)
    production_rate: reactive[Decimal] = reactive(Decimal("0"))
    purity: reactive[float] = reactive(100.0)

    def __init__(self, tier: "EmotionTier", **kwargs):
        super().__init__(**kwargs)
        self.tier = tier
        self.config = EMOTION_CONFIGS[tier]

    def compose(self) -> ComposeResult:
        with Horizontal(classes="resource-row"):
            yield Label(f"{self.config.symbol} {self.config.name}", classes="resource-name")
            yield Label("0", id=f"amount-{self.tier.name}", classes="resource-amount")
            yield ProgressBar(total=100, show_eta=False, id=f"storage-{self.tier.name}")
            yield Label("+0/s", id=f"rate-{self.tier.name}", classes="resource-rate")

    def update_display(self, amount: Decimal, capacity: int, rate: Decimal, purity: float):
        """Update the resource display values."""
        self.amount = amount
        self.storage_percent = float(amount / capacity * 100) if capacity > 0 else 0
        self.production_rate = rate
        self.purity = purity

        # Update labels
        amount_label = self.query_one(f"#amount-{self.tier.name}", Label)
        amount_label.update(self._format_amount(amount))

        rate_label = self.query_one(f"#rate-{self.tier.name}", Label)
        rate_label.update(f"+{self._format_amount(rate)}/s")

        storage_bar = self.query_one(f"#storage-{self.tier.name}", ProgressBar)
        storage_bar.update(progress=self.storage_percent)

    def _format_amount(self, value: Decimal) -> str:
        """Format large numbers with K, M, B suffixes."""
        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"
        elif value >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.2f}K"
        else:
            return f"{value:.1f}"


class ResourcePanel(Static):
    """Panel showing all unlocked resources."""

    def __init__(self, state_manager: "GameStateManager", **kwargs):
        super().__init__(**kwargs)
        self.state_manager = state_manager
        self.resource_displays: dict["EmotionTier", ResourceDisplay] = {}

    def compose(self) -> ComposeResult:
        yield Label("Resources", classes="panel-title")
        with Vertical(id="resource-list"):
            for tier in EmotionTier:
                display = ResourceDisplay(tier, id=f"resource-{tier.name}")
                self.resource_displays[tier] = display
                yield display

    def on_mount(self):
        """Initialize visibility based on unlocked resources."""
        self._update_visibility()

    def _update_visibility(self):
        """Show/hide resources based on unlock status."""
        state = self.state_manager.state
        for tier, display in self.resource_displays.items():
            resource = state.resources[tier]
            display.display = resource.unlocked

    def refresh_all(self):
        """Refresh all resource displays."""
        state = self.state_manager.state
        self._update_visibility()

        for tier, display in self.resource_displays.items():
            resource = state.resources[tier]
            if resource.unlocked:
                # Get production rate from production engine (will be passed in)
                display.update_display(
                    amount=resource.amount,
                    capacity=resource.storage_capacity,
                    rate=Decimal("0"),  # Will be updated by production engine
                    purity=resource.purity,
                )
