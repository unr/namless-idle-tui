"""Customer queue widget for displaying waiting customers."""

from typing import List, Optional

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, ListView, ListItem, Label
from textual.containers import Container, Vertical, Horizontal
from textual.reactive import reactive

from ..models.customer import Customer, CustomerType


class CustomerQueueItem(Static):
    """Widget representing a single customer in the queue."""

    DEFAULT_CSS = """
    CustomerQueueItem {
        height: auto;
        border: solid transparent;
        padding: 1;
        margin: 0 0 1 0;
    }

    CustomerQueueItem.selected {
        border: solid $accent;
        background: $boost;
    }

    CustomerQueueItem:hover {
        background: $panel;
    }

    .customer_header {
        text-style: bold;
    }

    .customer_need {
        color: $warning;
    }

    .customer_budget {
        color: $success;
    }

    .patience_bar {
        width: 100%;
        height: 1;
    }

    .special_tag {
        color: $error;
        text-style: bold;
    }

    .returning_tag {
        color: $accent;
    }
    """

    def __init__(self, customer: Customer, is_selected: bool = False):
        super().__init__()
        self.customer = customer
        self.is_selected = is_selected

    def render(self) -> str:
        """Render the customer queue item."""
        c = self.customer

        # Build header with name and avatar
        header = f"{c.avatar} {c.name}"

        # Add special tags
        tags = []
        if c.customer_type == CustomerType.VIP:
            tags.append("[VIP]")
        elif c.customer_type == CustomerType.DESPERATE:
            tags.append("[URGENT]")
        elif c.customer_type == CustomerType.ADDICTED:
            tags.append("[RETURNING]")

        if c.is_returning and c.customer_type == CustomerType.REGULAR:
            tags.append("[RETURN]")

        if tags:
            header += f" {' '.join(tags)}"

        # Build need line
        intensity_text = "High" if c.need_intensity > 0.7 else "Med" if c.need_intensity > 0.3 else "Low"
        need_line = f"   Needs: {c.primary_need.title()} ({intensity_text})"

        # Build budget line
        budget_line = f"   Budget: {c.budget:,.0f}◊"

        # Build patience bar
        patience_pct = c.get_patience_percentage()
        bar_width = 10
        filled = int((patience_pct / 100.0) * bar_width)
        empty = bar_width - filled
        patience_bar = f"   ⏱ Patience: [{'█' * filled}{'─' * empty}] {c.patience}/{c.max_patience}"

        # Add dependency warning if applicable
        dependency_line = ""
        if c.dependency_level > 0.5:
            dependency_line = f"   ⚠ Dependency Risk: {int(c.dependency_level * 100)}%"

        # Combine all lines
        lines = [header, need_line, budget_line, patience_bar]
        if dependency_line:
            lines.append(dependency_line)

        return "\n".join(lines)

    def on_click(self) -> None:
        """Handle click event."""
        # Clicks would be handled by parent CustomerQueue widget
        pass


class CustomerQueue(Widget):
    """Widget displaying the queue of waiting customers."""

    DEFAULT_CSS = """
    CustomerQueue {
        height: 1fr;
        width: 100%;
        border: solid $primary-darken-1;
        padding: 1;
    }

    #queue_header {
        dock: top;
        height: 3;
        content-align: center middle;
        text-style: bold;
        background: $primary-darken-2;
        color: $text;
    }

    #empty_queue {
        height: 100%;
        content-align: center middle;
        color: $text-muted;
    }

    #queue_content {
        height: 1fr;
        overflow-y: auto;
    }
    """

    # Reactive attributes
    customers: reactive[List[Customer]] = reactive(list, init=False)
    selected_customer_id: reactive[Optional[str]] = reactive(None)
    max_queue_size: reactive[int] = reactive(5)

    def __init__(self):
        super().__init__()
        self._customer_widgets: dict[str, CustomerQueueItem] = {}

    def compose(self) -> ComposeResult:
        """Compose the queue widget."""
        with Vertical():
            # Header showing queue count
            yield Static("", id="queue_header")

            # Queue content container
            yield Container(id="queue_content")

            # Empty state
            yield Static("No customers waiting", id="empty_queue")

    def on_mount(self) -> None:
        """Initialize on mount."""
        self._update_display()

    def watch_customers(self, new_customers: List[Customer]) -> None:
        """React to customer list changes."""
        if self.is_mounted:
            self._update_display()

    def watch_selected_customer_id(self, new_id: Optional[str]) -> None:
        """React to selection changes."""
        if self.is_mounted:
            self._update_display()

    def _update_display(self) -> None:
        """Update the queue display."""
        if not self.is_mounted:
            return
        try:
            # Update header
            count = len(self.customers)
            header_text = f"CUSTOMER QUEUE ({count}/{self.max_queue_size} waiting)"
            if header_widget := self.query_one("#queue_header", Static):
                header_widget.update(header_text)

            # Show/hide empty state
            if empty_widget := self.query_one("#empty_queue", Static):
                empty_widget.display = (count == 0)

            # Update queue content
            if content_container := self.query_one("#queue_content", Container):
                # Clear existing widgets
                content_container.remove_children()

                # Add customer widgets
                for idx, customer in enumerate(self.customers):
                    is_selected = (customer.id == self.selected_customer_id)

                    item = CustomerQueueItem(customer, is_selected)
                    if is_selected:
                        item.add_class("selected")

                    content_container.mount(item)
        except Exception:
            pass

    def get_customer_by_index(self, index: int) -> Optional[Customer]:
        """Get customer by queue position (0-indexed)."""
        if 0 <= index < len(self.customers):
            return self.customers[index]
        return None

    def get_selected_customer(self) -> Optional[Customer]:
        """Get the currently selected customer."""
        if self.selected_customer_id:
            for customer in self.customers:
                if customer.id == self.selected_customer_id:
                    return customer
        return None

    def get_queue_fullness(self) -> float:
        """Get queue fullness as percentage (0-100)."""
        return (len(self.customers) / self.max_queue_size) * 100.0

    def is_queue_full(self) -> bool:
        """Check if queue is at capacity."""
        return len(self.customers) >= self.max_queue_size

    def get_queue_summary(self) -> dict:
        """Get summary statistics about the queue."""
        if not self.customers:
            return {
                "count": 0,
                "avg_patience": 0,
                "avg_budget": 0,
                "needs": {}
            }

        total_patience = sum(c.get_patience_percentage() for c in self.customers)
        total_budget = sum(c.budget for c in self.customers)

        # Count needs
        needs = {}
        for customer in self.customers:
            need = customer.primary_need
            needs[need] = needs.get(need, 0) + 1

        return {
            "count": len(self.customers),
            "avg_patience": total_patience / len(self.customers),
            "avg_budget": total_budget / len(self.customers),
            "needs": needs,
            "vip_count": sum(1 for c in self.customers if c.customer_type == CustomerType.VIP),
            "desperate_count": sum(1 for c in self.customers if c.customer_type == CustomerType.DESPERATE)
        }
