"""Customer panel widget for displaying and interacting with customers."""

from typing import TYPE_CHECKING, Callable, Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Label, Static

if TYPE_CHECKING:
    from ..game.customers import Customer, CustomerManager


class CustomerCard(Static):
    """Display a single customer in the queue."""

    def __init__(self, customer: "Customer", on_select: Callable[["Customer"], None], **kwargs):
        super().__init__(**kwargs)
        self.customer = customer
        self._on_select = on_select

    def compose(self) -> ComposeResult:
        with Horizontal(classes="customer-card"):
            yield Label(self.customer.avatar, classes="customer-avatar")
            with Vertical(classes="customer-info"):
                yield Label(self.customer.name, classes="customer-name")
                yield Label(
                    f"Needs: {self.customer.primary_need.name}",
                    classes="customer-need",
                )
                yield Label(
                    f"Patience: {'█' * self.customer.patience}{'░' * (5 - self.customer.patience)}",
                    classes="customer-patience",
                )
            yield Button("Serve", id=f"serve-{self.customer.id}", classes="serve-btn")

    @on(Button.Pressed)
    def handle_serve(self, event: Button.Pressed):
        """Handle serve button press."""
        self._on_select(self.customer)


class CustomerPanel(Static):
    """Panel showing customer queue and current customer."""

    def __init__(self, customer_manager: "CustomerManager", **kwargs):
        super().__init__(**kwargs)
        self.customer_manager = customer_manager
        self._on_serve: Optional[Callable[["Customer"], None]] = None
        self._current_tutorial: Optional["Customer"] = None

    def set_serve_callback(self, callback: Callable[["Customer"], None]):
        """Set the callback for when a customer is selected to serve."""
        self._on_serve = callback

    def compose(self) -> ComposeResult:
        yield Label("Customer Queue", classes="panel-title")
        yield Static("No customers waiting", id="empty-queue-msg")
        yield Vertical(id="customer-list")
        yield Static("", id="tutorial-customer", classes="tutorial-highlight")

    def refresh_queue(self):
        """Refresh the customer queue display."""
        queue_container = self.query_one("#customer-list", Vertical)
        queue_container.remove_children()

        empty_msg = self.query_one("#empty-queue-msg", Static)
        tutorial_display = self.query_one("#tutorial-customer", Static)

        # Check for tutorial customer
        tutorial_customer = self.customer_manager.check_tutorial_triggers()
        if tutorial_customer:
            tutorial_display.update(self._format_tutorial_customer(tutorial_customer))
            tutorial_display.display = True
            # Store reference for serving
            self._current_tutorial = tutorial_customer
        else:
            tutorial_display.display = False
            self._current_tutorial = None

        # Display queue
        if self.customer_manager.queue:
            empty_msg.display = False
            for customer in self.customer_manager.queue:
                card = CustomerCard(customer, self._handle_select)
                queue_container.mount(card)
        else:
            empty_msg.display = not (tutorial_customer is not None)

    def _format_tutorial_customer(self, customer: "Customer") -> str:
        """Format tutorial customer display."""
        config = customer.tutorial_config
        return f"""
╔══════════════════════════════════════╗
║  {customer.avatar} SPECIAL CUSTOMER: {customer.name}
║
║  "{customer.dialogue}"
║
║  Trade: {config.cost_amount} {config.cost_tier.name} → {config.reward_amount} {config.reward_tier.name}
║
║  [Press T to Trade]
╚══════════════════════════════════════╝
"""

    def _handle_select(self, customer: "Customer"):
        """Handle customer selection."""
        if self._on_serve:
            self._on_serve(customer)
