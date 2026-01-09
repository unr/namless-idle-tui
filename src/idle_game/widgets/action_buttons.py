"""Action buttons widget for click harvesting and production buildings."""

from decimal import Decimal
from typing import Optional

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Static, Label
from textual.containers import Container, Vertical, Horizontal, Grid
from textual.message import Message


class ProducerButton(Static):
    """Button for purchasing emotion producers/buildings."""

    # Reactive attributes
    cost: reactive[Decimal] = reactive(Decimal(10))
    owned_count: reactive[int] = reactive(0)
    production_rate: reactive[Decimal] = reactive(Decimal(0.5))
    can_afford: reactive[bool] = reactive(False)
    is_locked: reactive[bool] = reactive(True)

    def __init__(
        self,
        name: str,
        description: str,
        resource_type: str,
        *args,
        **kwargs
    ) -> None:
        """Initialize a producer button.

        Args:
            name: Name of the producer (e.g., "Joy Factory")
            description: Description text
            resource_type: Type of resource this produces (e.g., "Smiles")
        """
        super().__init__(*args, **kwargs)
        self.producer_name = name
        self.producer_description = description
        self.resource_type = resource_type

    def compose(self) -> ComposeResult:
        """Compose the producer button layout."""
        with Container(classes="producer-button"):
            # Producer name and count
            with Horizontal(classes="producer-header"):
                yield Static(self.producer_name, classes="producer-name")
                yield Static(f"Owned: {self.owned_count}", classes="producer-count")

            # Description and production
            yield Static(self.producer_description, classes="producer-description")
            yield Static(
                f"Produces: {self._format_production()}",
                classes="producer-production"
            )

            # Cost and buy button
            with Horizontal(classes="producer-footer"):
                yield Static(
                    f"Cost: {self._format_cost()}",
                    classes="producer-cost"
                )
                yield Button(
                    "Buy",
                    variant="primary" if self.can_afford else "default",
                    disabled=not self.can_afford or self.is_locked,
                    classes="buy-button"
                )

    def watch_owned_count(self, new_count: int) -> None:
        """Update display when owned count changes."""
        if not self.is_mounted:
            return
        try:
            count_widget = self.query_one(".producer-count", Static)
            count_widget.update(f"Owned: {new_count}")
        except Exception:
            pass

    def watch_cost(self, new_cost: Decimal) -> None:
        """Update display when cost changes."""
        if not self.is_mounted:
            return
        try:
            cost_widget = self.query_one(".producer-cost", Static)
            cost_widget.update(f"Cost: {self._format_cost()}")
        except Exception:
            pass

    def watch_production_rate(self, new_rate: Decimal) -> None:
        """Update display when production rate changes."""
        if not self.is_mounted:
            return
        try:
            production_widget = self.query_one(".producer-production", Static)
            production_widget.update(f"Produces: {self._format_production()}")
        except Exception:
            pass

    def watch_can_afford(self, affordable: bool) -> None:
        """Update button state when affordability changes."""
        if not self.is_mounted:
            return
        try:
            buy_button = self.query_one(".buy-button", Button)
            buy_button.variant = "primary" if affordable else "default"
            buy_button.disabled = not affordable or self.is_locked
        except Exception:
            pass

    def watch_is_locked(self, locked: bool) -> None:
        """Update display when lock state changes."""
        if locked:
            self.add_class("locked")
        else:
            self.remove_class("locked")

        if not self.is_mounted:
            return
        try:
            buy_button = self.query_one(".buy-button", Button)
            buy_button.disabled = locked or not self.can_afford
        except Exception:
            pass

    def _format_cost(self) -> str:
        """Format the cost display."""
        if self.is_locked:
            return "🔒 Locked"

        cost_float = float(self.cost)
        if cost_float >= 1_000_000:
            return f"{cost_float / 1_000_000:.2f}M"
        elif cost_float >= 1_000:
            return f"{cost_float / 1_000:.2f}K"
        else:
            return f"{cost_float:.0f}"

    def _format_production(self) -> str:
        """Format the production rate display."""
        if self.is_locked:
            return "Locked"

        rate_float = float(self.production_rate)
        return f"{rate_float:.1f} {self.resource_type}/sec each"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle buy button press."""
        if not self.is_locked and self.can_afford:
            # Post a custom message that the parent can handle
            self.post_message(self.ProducerPurchased(self.name))

    class ProducerPurchased(Message):
        """Message sent when a producer is purchased."""

        def __init__(self, producer_name: str) -> None:
            """Initialize the message.

            Args:
                producer_name: Name of the purchased producer
            """
            super().__init__()
            self.producer_name = producer_name


class ActionButtons(Widget):
    """Widget containing click button and producer purchase buttons."""

    # Reactive attributes for click power
    click_power: reactive[Decimal] = reactive(Decimal(5))
    click_multiplier: reactive[float] = reactive(1.0)
    total_clicks: reactive[int] = reactive(0)

    def __init__(self, game_state=None, *args, **kwargs) -> None:
        """Initialize the action buttons widget."""
        super().__init__(*args, **kwargs)
        self.game_state = game_state

        # Track producer buttons
        self.producer_buttons: dict[str, ProducerButton] = {}

    def compose(self) -> ComposeResult:
        """Compose the action buttons layout."""
        with Vertical(id="action-buttons"):
            # Click harvesting section
            with Container(id="click-section"):
                yield Static("Manual Harvesting", classes="section-header")

                # Click power display
                with Horizontal(classes="click-info"):
                    yield Static("Click Power:", classes="info-label")
                    yield Static(
                        self._format_click_power(),
                        id="click-power-display"
                    )

                # Main click button
                yield Button(
                    "☺ Harvest Smiles ☺",
                    variant="success",
                    id="harvest-button",
                    classes="action-button-large"
                )

                # Click counter
                yield Static(
                    f"Total Clicks: {self.total_clicks}",
                    id="click-counter"
                )

            # Producers section
            with Container(id="producers-section"):
                yield Static("Production Buildings", classes="section-header")

                with Vertical(id="producers-list"):
                    # Joy Factory (first producer, unlocks with first customer)
                    joy_factory = ProducerButton(
                        name="Joy Factory",
                        description="Converts Smiles into Joy",
                        resource_type="Smiles"
                    )
                    joy_factory.cost = Decimal(10)
                    joy_factory.production_rate = Decimal(0.5)
                    joy_factory.is_locked = True  # Unlocked by first customer
                    self.producer_buttons["Joy Factory"] = joy_factory
                    yield joy_factory

                    # More producers will be added as they unlock
                    yield Static(
                        "More producers unlock as you progress...",
                        classes="unlock-hint"
                    )

    def watch_click_power(self, new_power: Decimal) -> None:
        """Update display when click power changes."""
        if not self.is_mounted:
            return
        try:
            power_display = self.query_one("#click-power-display", Static)
            power_display.update(self._format_click_power())
        except Exception:
            pass

    def watch_click_multiplier(self, new_multiplier: float) -> None:
        """Update display when click multiplier changes."""
        if not self.is_mounted:
            return
        try:
            power_display = self.query_one("#click-power-display", Static)
            power_display.update(self._format_click_power())
        except Exception:
            pass

    def watch_total_clicks(self, new_count: int) -> None:
        """Update click counter display."""
        if not self.is_mounted:
            return
        try:
            counter = self.query_one("#click-counter", Static)
            counter.update(f"Total Clicks: {new_count}")
        except Exception:
            pass

    def _format_click_power(self) -> str:
        """Format the click power display."""
        base = float(self.click_power)
        multiplier = self.click_multiplier
        total = base * multiplier

        if multiplier > 1.0:
            return f"{total:.1f} ({base:.0f} × {multiplier:.1f}x)"
        else:
            return f"{total:.1f}"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "harvest-button":
            # Increment click counter
            self.total_clicks += 1

            # Post a custom message for the game logic to handle
            self.post_message(self.HarvestClicked(self.click_power * Decimal(self.click_multiplier)))

    def update_producer(
        self,
        name: str,
        cost: Optional[Decimal] = None,
        owned_count: Optional[int] = None,
        production_rate: Optional[Decimal] = None,
        can_afford: Optional[bool] = None,
        is_locked: Optional[bool] = None
    ) -> None:
        """Update a producer's values.

        Args:
            name: Name of the producer to update
            cost: New cost value
            owned_count: New owned count
            production_rate: New production rate
            can_afford: Whether player can afford it
            is_locked: Whether it's locked
        """
        producer = self.producer_buttons.get(name)
        if not producer:
            return

        if cost is not None:
            producer.cost = cost
        if owned_count is not None:
            producer.owned_count = owned_count
        if production_rate is not None:
            producer.production_rate = production_rate
        if can_afford is not None:
            producer.can_afford = can_afford
        if is_locked is not None:
            producer.is_locked = is_locked

    def add_producer(
        self,
        name: str,
        description: str,
        resource_type: str,
        cost: Decimal,
        production_rate: Decimal
    ) -> None:
        """Add a new producer button dynamically.

        Args:
            name: Name of the producer
            description: Description text
            resource_type: Type of resource produced
            cost: Initial cost
            production_rate: Production rate
        """
        if name in self.producer_buttons:
            return

        producer = ProducerButton(
            name=name,
            description=description,
            resource_type=resource_type
        )
        producer.cost = cost
        producer.production_rate = production_rate
        producer.is_locked = False

        self.producer_buttons[name] = producer

        # Mount the new producer to the list
        producers_list = self.query_one("#producers-list", Vertical)
        producers_list.mount(producer, before=producers_list.children[-1])

    class HarvestClicked(Message):
        """Message sent when harvest button is clicked."""

        def __init__(self, amount: Decimal) -> None:
            """Initialize the message.

            Args:
                amount: Amount to harvest
            """
            super().__init__()
            self.amount = amount
