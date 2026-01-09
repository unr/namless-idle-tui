"""Statistics display widget showing game progress and metrics."""

from decimal import Decimal
from typing import Dict, Optional

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static, ProgressBar, Label
from textual.containers import Container, Vertical, Horizontal, Grid


class StatItem(Static):
    """Individual statistic display item."""

    value: reactive[str] = reactive("0")

    def __init__(self, label: str, *args, **kwargs) -> None:
        """Initialize a stat item.

        Args:
            label: The label for this statistic
        """
        super().__init__(*args, **kwargs)
        self.label_text = label

    def compose(self) -> ComposeResult:
        """Compose the stat item layout."""
        with Horizontal(classes="stat-item"):
            yield Static(f"{self.label_text}:", classes="stat-label")
            yield Static(self.value, classes="stat-value")

    def watch_value(self, new_value: str) -> None:
        """Update display when value changes."""
        if not self.is_mounted:
            return
        try:
            value_widget = self.query_one(".stat-value", Static)
            value_widget.update(new_value)
        except Exception:
            pass


class ProductionRateDisplay(Static):
    """Display production rates for all emotions."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize production rate display."""
        super().__init__(*args, **kwargs)
        self.rates: Dict[str, Decimal] = {}

    def compose(self) -> ComposeResult:
        """Compose the production rate display."""
        with Container(classes="production-rates"):
            yield Static("Production Rates:", classes="subsection-header")
            with Vertical(id="rates-list"):
                yield Static("No production yet", id="rates-placeholder")

    def update_rate(self, resource: str, rate: Decimal) -> None:
        """Update the production rate for a resource.

        Args:
            resource: Name of the resource
            rate: Production rate per second
        """
        self.rates[resource] = rate
        self._refresh_display()

    def _refresh_display(self) -> None:
        """Refresh the production rates display."""
        rates_list = self.query_one("#rates-list", Vertical)

        # Clear placeholder if we have rates
        if self.rates:
            placeholder = rates_list.query_one("#rates-placeholder", Static)
            if placeholder:
                placeholder.remove()

        # Update or create rate displays
        for resource, rate in self.rates.items():
            if rate > 0:
                rate_text = self._format_rate(rate)
                # Try to find existing display
                try:
                    rate_display = rates_list.query_one(f"#{resource}-rate", Static)
                    rate_display.update(f"{resource}: {rate_text}")
                except:
                    # Create new display
                    rate_display = Static(
                        f"{resource}: {rate_text}",
                        id=f"{resource}-rate",
                        classes="rate-item"
                    )
                    rates_list.mount(rate_display)

    def _format_rate(self, rate: Decimal) -> str:
        """Format a production rate.

        Args:
            rate: Rate to format

        Returns:
            Formatted string
        """
        rate_float = float(rate)
        if rate_float >= 1_000_000:
            return f"+{rate_float / 1_000_000:.2f}M/s"
        elif rate_float >= 1_000:
            return f"+{rate_float / 1_000:.2f}K/s"
        else:
            return f"+{rate_float:.1f}/s"


class PrestigeInfo(Static):
    """Display prestige-related information."""

    prestige_count: reactive[int] = reactive(0)
    emotional_depth: reactive[Decimal] = reactive(Decimal(0))
    depth_multiplier: reactive[float] = reactive(1.0)
    is_unlocked: reactive[bool] = reactive(False)

    def compose(self) -> ComposeResult:
        """Compose the prestige info display."""
        with Container(classes="prestige-info"):
            yield Static("Prestige", classes="subsection-header")
            with Vertical(id="prestige-details"):
                if not self.is_unlocked:
                    yield Static(
                        "Prestige unlocks at Transcendence tier",
                        classes="prestige-locked"
                    )
                else:
                    yield StatItem("Prestige Count", id="prestige-count-item")
                    yield StatItem("Emotional Depth", id="emotional-depth-item")
                    yield StatItem("Production Bonus", id="depth-bonus-item")

    def watch_prestige_count(self, new_count: int) -> None:
        """Update prestige count display."""
        if not self.is_mounted or not self.is_unlocked:
            return
        try:
            count_item = self.query_one("#prestige-count-item", StatItem)
            count_item.value = str(new_count)
        except Exception:
            pass

    def watch_emotional_depth(self, new_depth: Decimal) -> None:
        """Update emotional depth display."""
        if not self.is_mounted or not self.is_unlocked:
            return
        try:
            depth_item = self.query_one("#emotional-depth-item", StatItem)
            depth_item.value = f"{float(new_depth):.1f}"
        except Exception:
            pass

    def watch_depth_multiplier(self, new_multiplier: float) -> None:
        """Update depth multiplier display."""
        if not self.is_mounted or not self.is_unlocked:
            return
        try:
            bonus_item = self.query_one("#depth-bonus-item", StatItem)
            bonus_item.value = f"+{(new_multiplier - 1.0) * 100:.0f}%"
        except Exception:
            pass

    def watch_is_unlocked(self, unlocked: bool) -> None:
        """Update display when prestige unlocks."""
        if unlocked:
            # Rebuild the display to show prestige stats
            details = self.query_one("#prestige-details", Vertical)
            details.remove_children()
            details.mount(StatItem("Prestige Count", id="prestige-count-item"))
            details.mount(StatItem("Emotional Depth", id="emotional-depth-item"))
            details.mount(StatItem("Production Bonus", id="depth-bonus-item"))

            # Initialize values
            self.watch_prestige_count(self.prestige_count)
            self.watch_emotional_depth(self.emotional_depth)
            self.watch_depth_multiplier(self.depth_multiplier)


class StatDisplay(Widget):
    """Main statistics display widget."""

    # Core game statistics
    total_clicks: reactive[int] = reactive(0)
    customers_served: reactive[int] = reactive(0)
    recipes_discovered: reactive[int] = reactive(0)
    total_playtime: reactive[float] = reactive(0.0)  # in seconds
    mood_rating: reactive[float] = reactive(0.0)  # 0-5 stars
    ethical_score: reactive[int] = reactive(50)  # 0-100

    def __init__(self, game_state=None, *args, **kwargs) -> None:
        """Initialize the statistics display."""
        super().__init__(*args, **kwargs)
        self.game_state = game_state

        # Sub-widgets
        self.production_display: Optional[ProductionRateDisplay] = None
        self.prestige_display: Optional[PrestigeInfo] = None

    def compose(self) -> ComposeResult:
        """Compose the statistics display layout."""
        with Vertical(id="stat-display"):
            # Core statistics section
            with Container(id="core-stats"):
                yield Static("Progress", classes="section-header")

                with Grid(id="stats-grid"):
                    yield StatItem("Total Clicks", id="total-clicks-item")
                    yield StatItem("Customers Served", id="customers-served-item")
                    yield StatItem("Recipes Discovered", id="recipes-discovered-item")
                    yield StatItem("Playtime", id="playtime-item")

            # Reputation section
            with Container(id="reputation-stats"):
                yield Static("Reputation", classes="section-header")

                with Vertical():
                    # Mood rating with stars
                    with Horizontal(classes="stat-item"):
                        yield Static("Mood Rating:", classes="stat-label")
                        yield Static(self._format_mood_rating(), id="mood-rating-display")

                    # Ethical score with bar
                    with Horizontal(classes="stat-item"):
                        yield Static("Ethical Score:", classes="stat-label")
                        yield ProgressBar(
                            total=100,
                            show_percentage=True,
                            id="ethical-score-bar"
                        )

            # Production rates section
            self.production_display = ProductionRateDisplay()
            yield self.production_display

            # Prestige section
            self.prestige_display = PrestigeInfo()
            yield self.prestige_display

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        # Initialize stat values
        self._update_all_stats()

    def watch_total_clicks(self, new_clicks: int) -> None:
        """Update total clicks display."""
        if not self.is_mounted:
            return
        try:
            clicks_item = self.query_one("#total-clicks-item", StatItem)
            clicks_item.value = f"{new_clicks:,}"
        except Exception:
            pass

    def watch_customers_served(self, new_count: int) -> None:
        """Update customers served display."""
        if not self.is_mounted:
            return
        try:
            customers_item = self.query_one("#customers-served-item", StatItem)
            customers_item.value = str(new_count)
        except Exception:
            pass

    def watch_recipes_discovered(self, new_count: int) -> None:
        """Update recipes discovered display."""
        if not self.is_mounted:
            return
        try:
            recipes_item = self.query_one("#recipes-discovered-item", StatItem)
            recipes_item.value = str(new_count)
        except Exception:
            pass

    def watch_total_playtime(self, new_time: float) -> None:
        """Update playtime display."""
        if not self.is_mounted:
            return
        try:
            playtime_item = self.query_one("#playtime-item", StatItem)
            playtime_item.value = self._format_playtime(new_time)
        except Exception:
            pass

    def watch_mood_rating(self, new_rating: float) -> None:
        """Update mood rating display."""
        if not self.is_mounted:
            return
        try:
            mood_display = self.query_one("#mood-rating-display", Static)
            mood_display.update(self._format_mood_rating())
        except Exception:
            pass

    def watch_ethical_score(self, new_score: int) -> None:
        """Update ethical score display."""
        if not self.is_mounted:
            return
        try:
            ethical_bar = self.query_one("#ethical-score-bar", ProgressBar)
            ethical_bar.update(progress=new_score)
        except Exception:
            pass

    def _format_mood_rating(self) -> str:
        """Format the mood rating as stars.

        Returns:
            String with star representation
        """
        full_stars = int(self.mood_rating)
        half_star = (self.mood_rating % 1) >= 0.5
        empty_stars = 5 - full_stars - (1 if half_star else 0)

        stars = "★" * full_stars
        if half_star:
            stars += "⯪"
        stars += "☆" * empty_stars

        return f"{stars} ({self.mood_rating:.1f}/5.0)"

    def _format_playtime(self, seconds: float) -> str:
        """Format playtime in a readable format.

        Args:
            seconds: Total playtime in seconds

        Returns:
            Formatted string (e.g., "1h 23m", "45m 12s")
        """
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"

    def _update_all_stats(self) -> None:
        """Update all stat displays."""
        self.watch_total_clicks(self.total_clicks)
        self.watch_customers_served(self.customers_served)
        self.watch_recipes_discovered(self.recipes_discovered)
        self.watch_total_playtime(self.total_playtime)
        self.watch_mood_rating(self.mood_rating)
        self.watch_ethical_score(self.ethical_score)

    def update_production_rate(self, resource: str, rate: Decimal) -> None:
        """Update a production rate.

        Args:
            resource: Name of the resource
            rate: Production rate per second
        """
        if self.production_display:
            self.production_display.update_rate(resource, rate)

    def update_prestige_info(
        self,
        count: Optional[int] = None,
        emotional_depth: Optional[Decimal] = None,
        multiplier: Optional[float] = None,
        unlocked: Optional[bool] = None
    ) -> None:
        """Update prestige information.

        Args:
            count: Prestige count
            emotional_depth: Emotional depth currency
            multiplier: Production multiplier from depth
            unlocked: Whether prestige is unlocked
        """
        if not self.prestige_display:
            return

        if count is not None:
            self.prestige_display.prestige_count = count
        if emotional_depth is not None:
            self.prestige_display.emotional_depth = emotional_depth
        if multiplier is not None:
            self.prestige_display.depth_multiplier = multiplier
        if unlocked is not None:
            self.prestige_display.is_unlocked = unlocked
