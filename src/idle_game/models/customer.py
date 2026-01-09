"""Customer models and generation logic."""

import random
import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional
from enum import Enum

from ..data.customer_templates import (
    TUTORIAL_CUSTOMERS,
    CUSTOMER_NAMES,
    CUSTOMER_AVATARS,
    DIALOGUE_TEMPLATES,
    EMOTION_STATES,
    SERVICE_DESCRIPTIONS,
    SPECIAL_CUSTOMER_TYPES,
    TutorialCustomerTemplate,
    SpecialCustomerType
)


class CustomerType(Enum):
    """Types of customers."""
    REGULAR = "regular"
    TUTORIAL = "tutorial"
    VIP = "vip"
    DESPERATE = "desperate"
    ADDICTED = "addicted"


@dataclass
class SatisfactionResult:
    """Result of customer satisfaction calculation."""
    score: float  # 0-100
    stars: int  # 1-5
    reputation_change: float
    ethical_impact: float
    message: str
    tips_received: Decimal = Decimal("0")


@dataclass
class Customer:
    """Represents a customer in the shop."""
    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    avatar: str = "👤"
    customer_type: CustomerType = CustomerType.REGULAR

    # Emotional Need
    primary_need: str = "joy"  # Emotion they want
    need_intensity: float = 0.5  # 0-1, how badly they need it
    acceptable_purity: float = 50.0  # Minimum purity they'll accept

    # Economics
    budget: Decimal = Decimal("100")
    base_price: Decimal = Decimal("50")  # What they expect to pay

    # Queue Management
    patience: int = 5  # Turns before leaving (starts at max)
    max_patience: int = 5
    arrival_time: float = 0.0  # Game time when arrived

    # History & Story
    visit_count: int = 1
    satisfaction_history: List[float] = field(default_factory=list)
    dependency_level: float = 0.0  # 0-1 addiction scale
    story_arc_id: Optional[str] = None

    # Display
    dialogue: str = "Hello, do you have any emotions for sale?"
    emotion_state: str = "neutral"  # Their current emotional state

    # Special Properties
    special_type: Optional[SpecialCustomerType] = None
    is_returning: bool = False

    def __post_init__(self):
        """Initialize computed properties."""
        if self.customer_type != CustomerType.REGULAR:
            self._apply_special_modifiers()

    def _apply_special_modifiers(self):
        """Apply special customer type modifiers."""
        if self.customer_type.value in SPECIAL_CUSTOMER_TYPES:
            self.special_type = SPECIAL_CUSTOMER_TYPES[self.customer_type.value]
            self.budget *= Decimal(str(self.special_type.budget_multiplier))
            self.patience += self.special_type.patience_modifier
            self.max_patience = self.patience
            self.acceptable_purity = self.special_type.min_purity_required

            # Update dialogue with prefix
            if self.special_type.dialogue_prefix:
                self.dialogue = self.special_type.dialogue_prefix + self.dialogue

    def tick_patience(self) -> bool:
        """Decrease patience by 1. Returns True if customer leaves."""
        self.patience -= 1
        return self.patience <= 0

    def get_patience_percentage(self) -> float:
        """Get patience as percentage (0-100)."""
        return (self.patience / max(self.max_patience, 1)) * 100.0

    def calculate_satisfaction(
        self,
        emotion_sold: str,
        purity: float,
        price_charged: Decimal,
        wait_time: int = 0
    ) -> SatisfactionResult:
        """
        Calculate customer satisfaction based on service.

        From docs/game-design/shop-system.md:
        Base Satisfaction = 50%
        + Emotion Match Bonus (+30% if exact need)
        + Purity Bonus (+1% per 2% purity above 50%)
        + Price Fairness (+10% if below budget)
        + Speed Bonus (+5% if served quickly)
        - Wrong Emotion (-20%)
        - Low Purity (-2% per 1% below threshold)
        - Overpriced (-15% if above budget)
        - Kept Waiting (-5% per patience bar lost)
        = Final Satisfaction (0-100%)
        """
        satisfaction = 50.0

        # Emotion match
        if emotion_sold == self.primary_need:
            satisfaction += 30.0
        else:
            satisfaction -= 20.0

        # Purity bonus/penalty
        if purity >= 50.0:
            purity_bonus = (purity - 50.0) / 2.0
            satisfaction += purity_bonus

        if purity < self.acceptable_purity:
            purity_penalty = (self.acceptable_purity - purity) * 2.0
            satisfaction -= purity_penalty

        # Price fairness
        if price_charged <= self.budget:
            satisfaction += 10.0
        else:
            satisfaction -= 15.0

        # Speed bonus
        patience_lost = self.max_patience - self.patience
        if patience_lost == 0:
            satisfaction += 5.0
        else:
            satisfaction -= (patience_lost * 5.0)

        # Clamp to 0-100
        satisfaction = max(0.0, min(100.0, satisfaction))

        # Convert to stars (1-5)
        if satisfaction >= 90:
            stars = 5
            message = "Perfect service!"
        elif satisfaction >= 70:
            stars = 4
            message = "Great service!"
        elif satisfaction >= 50:
            stars = 3
            message = "Good service."
        elif satisfaction >= 30:
            stars = 2
            message = "Poor service..."
        else:
            stars = 1
            message = "Terrible service!"

        # Calculate reputation change
        reputation_change = (satisfaction - 50.0) / 25.0  # -2 to +2

        # Apply special modifiers
        if self.special_type:
            reputation_change *= self.special_type.reputation_impact

        # Calculate ethical impact
        ethical_impact = 0.0

        # Selling to addicted customers is ethically questionable
        if self.customer_type == CustomerType.ADDICTED:
            ethical_impact -= 3.0

        # Price gouging is unethical
        if price_charged > self.budget * Decimal("1.5"):
            ethical_impact -= 2.0

        # Low purity is unethical
        if purity < 50.0:
            ethical_impact -= 5.0

        # Helping desperate customers is ethical (if not overcharging)
        if self.customer_type == CustomerType.DESPERATE and price_charged <= self.budget:
            ethical_impact += 2.0

        # Calculate tips for exceptional service
        tips = Decimal("0")
        if satisfaction >= 90 and stars == 5:
            tips = price_charged * Decimal("0.1")  # 10% tip

        return SatisfactionResult(
            score=satisfaction,
            stars=stars,
            reputation_change=reputation_change,
            ethical_impact=ethical_impact,
            message=message,
            tips_received=tips
        )

    def to_dict(self) -> Dict:
        """Serialize customer to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "avatar": self.avatar,
            "customer_type": self.customer_type.value,
            "primary_need": self.primary_need,
            "need_intensity": self.need_intensity,
            "acceptable_purity": self.acceptable_purity,
            "budget": str(self.budget),
            "patience": self.patience,
            "max_patience": self.max_patience,
            "visit_count": self.visit_count,
            "satisfaction_history": self.satisfaction_history,
            "dependency_level": self.dependency_level,
            "dialogue": self.dialogue,
            "emotion_state": self.emotion_state,
            "is_returning": self.is_returning
        }


@dataclass
class TutorialCustomer(Customer):
    """Special tutorial customer that triggers at milestones."""
    template: Optional[TutorialCustomerTemplate] = None
    auto_trade: bool = True  # Tutorial trades are automatic

    def __init__(self, template: TutorialCustomerTemplate):
        """Initialize from template."""
        super().__init__(
            name=template.name,
            avatar=template.avatar,
            customer_type=CustomerType.TUTORIAL,
            dialogue=template.dialogue,
            patience=999,  # Tutorial customers don't leave
            max_patience=999
        )
        self.template = template

    def get_trade_description(self) -> str:
        """Get human-readable trade description."""
        if not self.template:
            return ""

        trade = self.template.trade
        return (
            f"Trade {trade.gives_amount} {trade.gives_emotion.title()} "
            f"for {trade.receives_amount} {trade.receives_emotion.title()}"
        )

    def get_unlock_message(self) -> str:
        """Get unlock notification message."""
        if not self.template:
            return ""
        return f"{self.template.unlocks_emotion.title()} unlocked! {self.template.unlocks_description}"


class CustomerGenerator:
    """Generates regular customers for the queue."""

    def __init__(self, unlocked_emotions: List[str], seed: Optional[int] = None):
        """
        Initialize generator.

        Args:
            unlocked_emotions: List of emotions available to generate needs for
            seed: Optional random seed for reproducibility
        """
        self.unlocked_emotions = unlocked_emotions
        self.customer_history: Dict[str, Customer] = {}  # Track returning customers
        self.generation_count = 0

        if seed is not None:
            random.seed(seed)

    def generate_regular_customer(
        self,
        reputation: float = 3.0,
        current_time: float = 0.0
    ) -> Customer:
        """
        Generate a regular customer.

        Args:
            reputation: Shop reputation (0-5 stars), affects customer quality
            current_time: Current game time

        Returns:
            Generated Customer instance
        """
        self.generation_count += 1

        # Choose customer type based on reputation
        customer_type = self._choose_customer_type(reputation)

        # Generate base properties
        name = random.choice(CUSTOMER_NAMES)
        avatar = random.choice(CUSTOMER_AVATARS)
        primary_need = random.choice(self.unlocked_emotions)

        # Generate economic properties
        base_budget = Decimal(str(random.randint(100, 1000)))
        need_intensity = random.random()

        # Generate dialogue
        dialogue = self._generate_dialogue(primary_need, need_intensity)

        # Determine emotion state
        emotion_state = self._get_emotion_state(primary_need)

        # Base customer
        customer = Customer(
            name=name,
            avatar=avatar,
            customer_type=customer_type,
            primary_need=primary_need,
            need_intensity=need_intensity,
            acceptable_purity=random.uniform(30.0, 80.0),
            budget=base_budget,
            base_price=base_budget * Decimal("0.7"),
            patience=5,
            max_patience=5,
            arrival_time=current_time,
            dialogue=dialogue,
            emotion_state=emotion_state
        )

        # Check if this is a returning customer
        if name in self.customer_history:
            previous = self.customer_history[name]
            customer.visit_count = previous.visit_count + 1
            customer.satisfaction_history = previous.satisfaction_history.copy()
            customer.dependency_level = previous.dependency_level
            customer.is_returning = True

            # Update dependency based on visit frequency
            if customer.visit_count > 3:
                customer.dependency_level = min(1.0, customer.dependency_level + 0.1)

            # High dependency might trigger addicted customer type
            if customer.dependency_level > 0.6 and random.random() < 0.3:
                customer.customer_type = CustomerType.ADDICTED

        # Store in history
        self.customer_history[name] = customer

        return customer

    def _choose_customer_type(self, reputation: float) -> CustomerType:
        """Choose customer type based on reputation."""
        # Higher reputation attracts better customers
        roll = random.random()

        if reputation >= 4.5 and roll < 0.15:
            return CustomerType.VIP
        elif roll < 0.1:
            return CustomerType.DESPERATE
        else:
            return CustomerType.REGULAR

    def _generate_dialogue(self, need: str, intensity: float) -> str:
        """Generate contextual dialogue."""
        template = random.choice(DIALOGUE_TEMPLATES)

        # Get emotion state for dialogue
        states = EMOTION_STATES.get(need, ["emotional"])
        emotion_state = random.choice(states)

        # Get service description
        service = SERVICE_DESCRIPTIONS.get(need, "emotional services")

        # Fill template
        dialogue = template.format(
            emotion_state=emotion_state,
            need=need.title(),
            service=service
        )

        return dialogue

    def _get_emotion_state(self, need: str) -> str:
        """Get customer's emotional state based on their need."""
        # They usually lack what they need
        states = EMOTION_STATES.get(need, ["neutral"])
        return random.choice(states)

    def check_tutorial_trigger(
        self,
        resources: Dict[str, float],
        completed_tutorials: List[str]
    ) -> Optional[TutorialCustomer]:
        """
        Check if any tutorial customer should trigger.

        Args:
            resources: Current resource amounts {emotion_name: amount}
            completed_tutorials: List of completed tutorial IDs

        Returns:
            TutorialCustomer if one should trigger, None otherwise
        """
        for template in TUTORIAL_CUSTOMERS:
            # Skip if already completed
            if template.id in completed_tutorials:
                continue

            # Check trigger condition
            trigger_emotion = template.trigger_emotion
            trigger_amount = template.trigger_amount

            current_amount = resources.get(trigger_emotion, 0)

            if current_amount >= trigger_amount:
                return TutorialCustomer(template)

        return None

    def generate_queue(
        self,
        count: int,
        reputation: float = 3.0,
        current_time: float = 0.0
    ) -> List[Customer]:
        """
        Generate multiple customers for initial queue.

        Args:
            count: Number of customers to generate
            reputation: Shop reputation
            current_time: Current game time

        Returns:
            List of generated customers
        """
        return [
            self.generate_regular_customer(reputation, current_time)
            for _ in range(count)
        ]
