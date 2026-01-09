"""Customer service widget for interacting with selected customer."""

from decimal import Decimal
from typing import Optional, List, Dict

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, Button, Label, OptionList
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.reactive import reactive
from textual.message import Message

from ..models.customer import Customer, TutorialCustomer, CustomerType


class CustomerService(Widget):
    """Widget for serving a selected customer."""

    DEFAULT_CSS = """
    CustomerService {
        height: 1fr;
        width: 100%;
        border: solid $accent-darken-1;
        padding: 1;
    }

    #service_header {
        dock: top;
        height: 3;
        content-align: center middle;
        text-style: bold;
        background: $accent-darken-2;
        color: $text;
    }

    #no_customer {
        height: 100%;
        content-align: center middle;
        color: $text-muted;
    }

    #customer_details {
        height: 1fr;
    }

    .portrait_container {
        height: 5;
        content-align: center middle;
        text-style: bold;
    }

    .customer_name {
        text-style: bold;
        color: $accent;
        content-align: center middle;
    }

    .customer_mood {
        color: $warning;
        text-style: italic;
        content-align: center middle;
    }

    .dialogue_box {
        border: solid $primary;
        padding: 1;
        margin: 1 0;
        background: $panel;
        height: auto;
        min-height: 4;
    }

    .analysis_section {
        border: solid $warning-darken-1;
        padding: 1;
        margin: 1 0;
        background: $surface;
        height: auto;
    }

    .section_title {
        text-style: bold underline;
        color: $text;
        margin: 0 0 1 0;
    }

    .warning_text {
        color: $error;
        text-style: bold;
    }

    .info_text {
        color: $text-muted;
    }

    #service_options {
        height: auto;
        border: solid $success-darken-1;
        padding: 1;
        margin: 1 0;
    }

    .tutorial_note {
        color: $accent;
        text-style: italic;
        padding: 1;
        background: $boost;
    }
    """

    # Reactive attributes
    customer: reactive[Optional[Customer]] = reactive(None)
    available_emotions: reactive[Dict[str, dict]] = reactive(dict, init=False)

    class ServiceOptionSelected(Message):
        """Message sent when a service option is chosen."""
        def __init__(self, emotion: str, amount: int, purity: float, price: Decimal):
            super().__init__()
            self.emotion = emotion
            self.amount = amount
            self.purity = purity
            self.price = price

    class TutorialTradeAccepted(Message):
        """Message sent when tutorial trade is accepted."""
        def __init__(self, customer: TutorialCustomer):
            super().__init__()
            self.customer = customer

    def __init__(self):
        super().__init__()
        self._showing_options = False

    def compose(self) -> ComposeResult:
        """Compose the service widget."""
        with Vertical():
            # Header
            yield Static("CUSTOMER SERVICE", id="service_header")

            # No customer state
            yield Static("Select a customer from the queue", id="no_customer")

            # Customer details container
            with ScrollableContainer(id="customer_details"):
                yield Container(id="details_content")

    def on_mount(self) -> None:
        """Initialize on mount."""
        self._update_display()

    def watch_customer(self, new_customer: Optional[Customer]) -> None:
        """React to customer changes."""
        self._showing_options = False
        if self.is_mounted:
            self._update_display()

    def watch_available_emotions(self, emotions: Dict[str, dict]) -> None:
        """React to available emotions changes."""
        if self._showing_options and self.is_mounted:
            self._update_display()

    def _update_display(self) -> None:
        """Update the service display."""
        if not self.is_mounted:
            return
        try:
            # Show/hide no customer message
            if no_customer_widget := self.query_one("#no_customer", Static):
                no_customer_widget.display = (self.customer is None)

            # Show/hide details
            if details_widget := self.query_one("#customer_details", ScrollableContainer):
                details_widget.display = (self.customer is not None)

            # Update customer details
            if self.customer:
                self._render_customer_details()
        except Exception:
            pass

    def _render_customer_details(self) -> None:
        """Render the customer details."""
        if not self.customer:
            return

        c = self.customer

        # Clear and rebuild details
        if details_container := self.query_one("#details_content", Container):
            details_container.remove_children()

            # Portrait
            portrait = Static(f"{c.avatar}", classes="portrait_container")
            portrait.styles.height = 3

            # Name
            name_display = f"{c.name}"
            if c.customer_type != CustomerType.REGULAR:
                type_name = c.customer_type.value.upper()
                name_display = f"[{type_name}] {name_display}"

            name_widget = Static(name_display, classes="customer_name")

            # Mood
            mood_icon = self._get_mood_icon(c.emotion_state)
            mood_text = f"{mood_icon} {c.emotion_state.title()}"
            if c.need_intensity > 0.7:
                mood_text += " (Intense)"
            mood_widget = Static(mood_text, classes="customer_mood")

            # Dialogue box
            dialogue_widget = Static(f'"{c.dialogue}"', classes="dialogue_box")

            # Analysis section
            analysis = self._build_analysis()
            analysis_widget = Static(analysis, classes="analysis_section")

            # Mount all widgets
            details_container.mount(portrait, name_widget, mood_widget, dialogue_widget, analysis_widget)

            # Add service options if showing
            if self._showing_options:
                self._render_service_options(details_container)
            elif isinstance(c, TutorialCustomer):
                self._render_tutorial_trade(details_container)

    def _get_mood_icon(self, emotion_state: str) -> str:
        """Get emoji for emotion state."""
        mood_icons = {
            "happy": "😊", "sad": "😢", "angry": "😠", "anxious": "😰",
            "scared": "😨", "content": "😌", "frustrated": "😤", "worried": "😟",
            "depressed": "😞", "neutral": "😐", "excited": "😃", "calm": "😌"
        }
        return mood_icons.get(emotion_state.lower(), "😐")

    def _build_analysis(self) -> str:
        """Build customer analysis text."""
        if not self.customer:
            return ""

        c = self.customer
        lines = ["📊 ANALYSIS:", ""]

        # Visit history
        if c.visit_count > 1:
            lines.append(f"• Visit #{c.visit_count} (returning customer)")
            if c.satisfaction_history:
                avg_sat = sum(c.satisfaction_history) / len(c.satisfaction_history)
                lines.append(f"• Average satisfaction: {avg_sat:.0f}%")

        # Need details
        intensity_desc = "desperately needs" if c.need_intensity > 0.7 else "wants" if c.need_intensity > 0.4 else "is curious about"
        lines.append(f"• {intensity_desc.title()} {c.primary_need.title()}")
        lines.append(f"• Will accept purity above {c.acceptable_purity:.0f}%")

        # Economic info
        lines.append(f"• Budget: {c.budget:,.0f}◊")
        lines.append(f"• Expected price: ~{c.base_price:,.0f}◊")

        # Warnings
        if c.dependency_level > 0.3:
            lines.append("")
            level_text = "HIGH" if c.dependency_level > 0.6 else "MODERATE"
            lines.append(f"⚠ {level_text} DEPENDENCY RISK: {int(c.dependency_level * 100)}%")

        if c.customer_type == CustomerType.ADDICTED:
            lines.append("⚠ ADDICTED: Ethical concerns about serving")

        if c.customer_type == CustomerType.VIP:
            lines.append("")
            lines.append("✨ VIP CUSTOMER:")
            lines.append("  • Willing to pay premium prices")
            lines.append("  • Expects highest quality (90%+ purity)")
            lines.append("  • Major reputation impact")

        if c.customer_type == CustomerType.DESPERATE:
            lines.append("")
            lines.append("❗ DESPERATE CUSTOMER:")
            lines.append("  • Will pay 3x normal price")
            lines.append("  • Ethical dilemma: exploit or help?")

        return "\n".join(lines)

    def _render_tutorial_trade(self, container: Container) -> None:
        """Render tutorial customer trade interface."""
        if not isinstance(self.customer, TutorialCustomer):
            return

        tutorial = self.customer

        # Tutorial note
        note_text = f"📚 TUTORIAL CUSTOMER\n\n{tutorial.get_trade_description()}\n\nThis trade will unlock: {tutorial.template.unlocks_emotion.title()}"
        note_widget = Static(note_text, classes="tutorial_note")

        # Accept button
        accept_btn = Button("Accept Trade [ENTER]", variant="success", id="accept_tutorial_btn")

        container.mount(note_widget, accept_btn)

    def _render_service_options(self, container: Container) -> None:
        """Render service options interface."""
        if not self.customer:
            return

        # Options container
        options_text = ["🛒 SERVICE OPTIONS:", ""]

        if not self.available_emotions:
            options_text.append("No emotions available to sell.")
            options_text.append("You need to produce emotions first!")
        else:
            # List available emotions that match or are useful
            for emotion_name, data in self.available_emotions.items():
                amount = data.get("amount", 0)
                purity = data.get("purity", 0)
                base_price = data.get("base_price", 100)

                if amount > 0:
                    match_indicator = "✓" if emotion_name == self.customer.primary_need else " "
                    price = Decimal(str(base_price))
                    options_text.append(f"{match_indicator} {emotion_name.title()} - {purity:.0f}% pure - {price:,.0f}◊")

            options_text.append("")
            options_text.append("Press number key to select option")

        options_widget = Static("\n".join(options_text), id="service_options")
        container.mount(options_widget)

    def show_service_options(self) -> None:
        """Show service options for current customer."""
        if not self.customer:
            return

        # For tutorial customers, just trigger the trade
        if isinstance(self.customer, TutorialCustomer):
            self.post_message(self.TutorialTradeAccepted(self.customer))
            return

        self._showing_options = True
        self._update_display()

    def select_service_option(self, emotion: str, amount: int = 1) -> None:
        """
        Select a service option to serve the customer.

        Args:
            emotion: The emotion to sell
            amount: Amount to sell (default 1)
        """
        if not self.customer or not self.available_emotions:
            return

        emotion_data = self.available_emotions.get(emotion)
        if not emotion_data:
            return

        purity = emotion_data.get("purity", 50.0)
        base_price = Decimal(str(emotion_data.get("base_price", 100)))

        # Calculate actual price (could add markup logic here)
        price = base_price * Decimal(str(amount))

        # Post message to parent screen
        self.post_message(self.ServiceOptionSelected(emotion, amount, purity, price))

    def get_service_preview(self, emotion: str, purity: float, price: Decimal) -> str:
        """
        Get a preview of expected satisfaction for a service option.

        Returns:
            Preview text with estimated satisfaction
        """
        if not self.customer:
            return "No customer selected"

        # Calculate satisfaction preview
        result = self.customer.calculate_satisfaction(
            emotion_sold=emotion,
            purity=purity,
            price_charged=price,
            wait_time=self.customer.max_patience - self.customer.patience
        )

        preview_lines = [
            f"Expected Satisfaction: {result.score:.0f}%",
            f"Stars: {'⭐' * result.stars}",
            f"Reputation Impact: {result.reputation_change:+.2f}",
        ]

        if result.ethical_impact != 0:
            preview_lines.append(f"Ethical Impact: {result.ethical_impact:+.1f}")

        if result.tips_received > 0:
            preview_lines.append(f"Expected Tip: {result.tips_received:,.0f}◊")

        return "\n".join(preview_lines)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "accept_tutorial_btn":
            if isinstance(self.customer, TutorialCustomer):
                self.post_message(self.TutorialTradeAccepted(self.customer))
