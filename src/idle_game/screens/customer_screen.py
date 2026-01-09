"""Customer screen for managing customer queue and service."""

from decimal import Decimal
from typing import List, Optional

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, Button, Label
from textual.message import Message
from textual.reactive import reactive

from ..models.customer import Customer, TutorialCustomer, SatisfactionResult
from ..widgets.customer_queue import CustomerQueue
from ..widgets.customer_service import CustomerService


class CustomerScreen(Screen):
    """Screen for customer queue management and service."""

    CSS = """
    CustomerScreen {
        layout: vertical;
    }

    #customer_header {
        dock: top;
        height: 3;
        background: $primary;
        color: $text;
        content-align: center middle;
        text-style: bold;
    }

    #main_container {
        layout: horizontal;
        height: 1fr;
    }

    #queue_container {
        width: 40%;
        border: solid $primary;
        padding: 1;
    }

    #service_container {
        width: 60%;
        border: solid $accent;
        padding: 1;
    }

    #stats_bar {
        dock: bottom;
        height: 3;
        background: $surface;
        layout: horizontal;
        padding: 0 2;
    }

    .stat_item {
        width: 1fr;
        content-align: center middle;
    }

    #action_bar {
        dock: bottom;
        height: 3;
        layout: horizontal;
        background: $panel;
        padding: 0 2;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("escape", "back", "Back"),
        ("1,2,3,4,5", "select_customer", "Select Customer"),
        ("s", "serve", "Serve Customer"),
        ("r", "refuse", "Refuse Service"),
        ("n", "next_customer", "Next Customer"),
    ]

    # Reactive state
    queue: reactive[List[Customer]] = reactive(list, init=False)
    selected_customer: reactive[Optional[Customer]] = reactive(None, init=False)
    current_reputation: reactive[float] = reactive(3.0)
    total_customers_served: reactive[int] = reactive(0)
    total_revenue: reactive[Decimal] = reactive(Decimal("0"))

    class CustomerServed(Message):
        """Message sent when a customer is served."""
        def __init__(self, customer: Customer, result: SatisfactionResult, emotion_sold: str, amount: int):
            super().__init__()
            self.customer = customer
            self.result = result
            self.emotion_sold = emotion_sold
            self.amount = amount

    class CustomerRefused(Message):
        """Message sent when service is refused."""
        def __init__(self, customer: Customer, reason: str = ""):
            super().__init__()
            self.customer = customer
            self.reason = reason

    class TutorialTradeAccepted(Message):
        """Message sent when tutorial trade is accepted."""
        def __init__(self, customer: TutorialCustomer):
            super().__init__()
            self.customer = customer

    def __init__(self, name: str = "Customer Management"):
        super().__init__()
        self.title = name
        self._queue_widget: Optional[CustomerQueue] = None
        self._service_widget: Optional[CustomerService] = None

    def compose(self) -> ComposeResult:
        """Compose the customer screen UI."""
        yield Header()

        # Title
        yield Static("🏪 CUSTOMER MANAGEMENT", id="customer_header")

        # Main content
        with Container(id="main_container"):
            # Queue panel
            with Vertical(id="queue_container"):
                yield Label("Customer Queue", classes="panel_title")
                self._queue_widget = CustomerQueue()
                yield self._queue_widget

            # Service panel
            with Vertical(id="service_container"):
                yield Label("Customer Service", classes="panel_title")
                self._service_widget = CustomerService()
                yield self._service_widget

        # Stats bar
        with Horizontal(id="stats_bar"):
            yield Static("Reputation: ⭐⭐⭐", id="reputation_stat", classes="stat_item")
            yield Static("Served: 0", id="served_stat", classes="stat_item")
            yield Static("Revenue: 0◊", id="revenue_stat", classes="stat_item")

        # Action bar
        with Horizontal(id="action_bar"):
            yield Button("Serve [S]", id="serve_btn", variant="success")
            yield Button("Refuse [R]", id="refuse_btn", variant="error")
            yield Button("Next [N]", id="next_btn", variant="primary")
            yield Button("Back [ESC]", id="back_btn")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize screen on mount."""
        self._update_stats()

    def watch_queue(self, new_queue: List[Customer]) -> None:
        """React to queue changes."""
        if self._queue_widget:
            self._queue_widget.customers = new_queue

        # Auto-select first customer if none selected
        if new_queue and not self.selected_customer:
            self.selected_customer = new_queue[0]

    def watch_selected_customer(self, customer: Optional[Customer]) -> None:
        """React to customer selection changes."""
        if self._service_widget:
            self._service_widget.customer = customer

        if self._queue_widget:
            self._queue_widget.selected_customer_id = customer.id if customer else None

    def watch_current_reputation(self, reputation: float) -> None:
        """Update reputation display."""
        self._update_stats()

    def watch_total_customers_served(self, count: int) -> None:
        """Update served count display."""
        self._update_stats()

    def watch_total_revenue(self, revenue: Decimal) -> None:
        """Update revenue display."""
        self._update_stats()

    def _update_stats(self) -> None:
        """Update statistics bar."""
        # Reputation stars
        stars = "⭐" * int(self.current_reputation)
        half_star = "☆" if (self.current_reputation % 1) >= 0.5 else ""
        empty_stars = "☆" * (5 - int(self.current_reputation) - (1 if half_star else 0))
        reputation_display = f"Reputation: {stars}{half_star}{empty_stars}"

        # Update stats
        if rep_widget := self.query_one("#reputation_stat", Static):
            rep_widget.update(reputation_display)

        if served_widget := self.query_one("#served_stat", Static):
            served_widget.update(f"Served: {self.total_customers_served}")

        if revenue_widget := self.query_one("#revenue_stat", Static):
            revenue_widget.update(f"Revenue: {self.total_revenue:,.0f}◊")

    def add_customer_to_queue(self, customer: Customer) -> None:
        """Add a customer to the queue."""
        new_queue = self.queue.copy()
        new_queue.append(customer)
        self.queue = new_queue

    def remove_customer_from_queue(self, customer: Customer) -> None:
        """Remove a customer from the queue."""
        new_queue = [c for c in self.queue if c.id != customer.id]
        self.queue = new_queue

        # Select next customer if current was removed
        if self.selected_customer and self.selected_customer.id == customer.id:
            self.selected_customer = new_queue[0] if new_queue else None

    def action_select_customer(self, key: str) -> None:
        """Select customer by number key."""
        try:
            index = int(key) - 1
            if 0 <= index < len(self.queue):
                self.selected_customer = self.queue[index]
        except (ValueError, IndexError):
            pass

    def action_serve(self) -> None:
        """Serve the selected customer."""
        if not self.selected_customer:
            self.notify("No customer selected", severity="warning")
            return

        # Trigger service widget to show options
        if self._service_widget:
            self._service_widget.show_service_options()

    def action_refuse(self) -> None:
        """Refuse service to selected customer."""
        if not self.selected_customer:
            self.notify("No customer selected", severity="warning")
            return

        customer = self.selected_customer
        self.remove_customer_from_queue(customer)
        self.post_message(self.CustomerRefused(customer, "Service refused by merchant"))
        self.notify(f"Refused service to {customer.name}", severity="warning")

    def action_next_customer(self) -> None:
        """Select next customer in queue."""
        if not self.queue:
            return

        if self.selected_customer:
            current_index = next(
                (i for i, c in enumerate(self.queue) if c.id == self.selected_customer.id),
                -1
            )
            next_index = (current_index + 1) % len(self.queue)
            self.selected_customer = self.queue[next_index]
        else:
            self.selected_customer = self.queue[0]

    def action_back(self) -> None:
        """Return to previous screen."""
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "serve_btn":
            self.action_serve()
        elif button_id == "refuse_btn":
            self.action_refuse()
        elif button_id == "next_btn":
            self.action_next_customer()
        elif button_id == "back_btn":
            self.action_back()

    def on_customer_service_complete(
        self,
        emotion: str,
        amount: int,
        purity: float,
        price: Decimal
    ) -> None:
        """
        Handle completed customer service.

        This would be called by the CustomerService widget.
        """
        if not self.selected_customer:
            return

        customer = self.selected_customer

        # Calculate satisfaction
        result = customer.calculate_satisfaction(
            emotion_sold=emotion,
            purity=purity,
            price_charged=price,
            wait_time=customer.max_patience - customer.patience
        )

        # Update tracking
        self.total_customers_served += 1
        self.total_revenue += price

        # Update reputation (rolling average)
        reputation_delta = result.reputation_change * 0.1  # Smooth the changes
        self.current_reputation = max(0.0, min(5.0, self.current_reputation + reputation_delta))

        # Remove from queue
        self.remove_customer_from_queue(customer)

        # Post message for game state
        self.post_message(self.CustomerServed(customer, result, emotion, amount))

        # Notify user
        self.notify(f"{customer.name}: {result.message} ({result.stars}⭐)", severity="information")

    def on_tutorial_customer_trade(self, customer: TutorialCustomer) -> None:
        """Handle tutorial customer automatic trade."""
        if not isinstance(customer, TutorialCustomer):
            return

        # Tutorial trades are automatic
        self.post_message(self.TutorialTradeAccepted(customer))

        # Show notification
        self.notify(
            f"{customer.name}: {customer.get_trade_description()}",
            severity="information",
            timeout=5.0
        )

        # Show unlock message
        self.notify(
            customer.get_unlock_message(),
            severity="information",
            timeout=10.0
        )

    def tick_customer_patience(self) -> None:
        """
        Tick down patience for all customers in queue.
        Call this periodically (e.g., every 10 seconds).
        """
        customers_to_remove = []

        for customer in self.queue:
            if customer.customer_type.value != "tutorial":  # Tutorial customers don't leave
                if customer.tick_patience():
                    customers_to_remove.append(customer)

        # Remove customers who ran out of patience
        for customer in customers_to_remove:
            self.remove_customer_from_queue(customer)
            self.notify(
                f"{customer.name} left due to long wait",
                severity="warning"
            )
            # Negative reputation impact
            self.current_reputation = max(0.0, self.current_reputation - 0.2)
