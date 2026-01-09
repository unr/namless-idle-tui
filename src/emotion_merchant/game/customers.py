"""Customer system for the Emotion Merchant game.

This module implements the customer queue and transaction system including:
- Tutorial customers that appear at specific milestones
- Regular customer generation (post-tutorial)
- Customer satisfaction calculations
- Reputation system based on service quality

Tutorial customers serve as both gameplay progression gates and narrative
introduction to the game's themes. Each unlocks a new emotion tier and
primary emotion type for use in recipes.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional, Callable, TYPE_CHECKING
from enum import Enum
import random

if TYPE_CHECKING:
    from .state import GameStateManager

from .resources import EmotionTier, PrimaryEmotion


class CustomerType(Enum):
    """Types of customers that can appear in the shop.

    Attributes:
        TUTORIAL: Scripted customers that appear at specific milestones
        REGULAR: Random customers with standard needs
        VIP: High-paying customers requiring high purity
        DESPERATE: Urgent customers paying premium but raising ethical concerns
        RETURNING: Previous customers showing potential dependency
    """
    TUTORIAL = "tutorial"
    REGULAR = "regular"
    VIP = "vip"
    DESPERATE = "desperate"
    RETURNING = "returning"


@dataclass
class TutorialCustomerConfig:
    """Configuration for a tutorial customer.

    Tutorial customers are event-triggered NPCs that appear when the player
    reaches specific resource thresholds. They trade resources to help
    progress through tiers while unlocking new gameplay mechanics.

    Attributes:
        id: Unique identifier for this customer
        name: Display name of the customer
        avatar: Unicode emoji/symbol representing the customer
        dialogue: What the customer says when appearing
        trigger_tier: The resource tier to check for triggering
        trigger_amount: Amount of trigger_tier needed to appear
        cost_tier: Resource tier the player must spend
        cost_amount: Amount of cost_tier required for the trade
        reward_tier: Resource tier the player receives
        reward_amount: Amount of reward_tier given to player
        unlocks_emotion: Primary emotion unlocked by this customer (if any)
        unlocks_tier: Resource tier unlocked by this customer (if any)
    """
    id: str
    name: str
    avatar: str
    dialogue: str
    trigger_tier: EmotionTier
    trigger_amount: Decimal
    cost_tier: EmotionTier
    cost_amount: Decimal
    reward_tier: EmotionTier
    reward_amount: Decimal
    unlocks_emotion: Optional[PrimaryEmotion] = None
    unlocks_tier: Optional[EmotionTier] = None


# Define all 5 tutorial customers that introduce core game mechanics
TUTORIAL_CUSTOMERS: List[TutorialCustomerConfig] = [
    TutorialCustomerConfig(
        id="joy_seeker",
        name="Joy Seeker",
        avatar="😊",
        dialogue="I heard you collect smiles. Can I buy some happiness?",
        trigger_tier=EmotionTier.SMILES,
        trigger_amount=Decimal("10"),
        cost_tier=EmotionTier.SMILES,
        cost_amount=Decimal("10"),
        reward_tier=EmotionTier.JOY,
        reward_amount=Decimal("1"),
        unlocks_emotion=PrimaryEmotion.JOY,
        unlocks_tier=EmotionTier.JOY
    ),
    TutorialCustomerConfig(
        id="melancholy_poet",
        name="Melancholy Poet",
        avatar="🎭",
        dialogue="I need sadness for my art. Too much joy lately.",
        trigger_tier=EmotionTier.JOY,
        trigger_amount=Decimal("50"),
        cost_tier=EmotionTier.JOY,
        cost_amount=Decimal("50"),
        reward_tier=EmotionTier.LOVE,
        reward_amount=Decimal("5"),
        unlocks_emotion=PrimaryEmotion.SADNESS,
        unlocks_tier=EmotionTier.LOVE
    ),
    TutorialCustomerConfig(
        id="frustrated_worker",
        name="Frustrated Worker",
        avatar="💢",
        dialogue="I'm too content. I need anger to demand change.",
        trigger_tier=EmotionTier.LOVE,
        trigger_amount=Decimal("100"),
        cost_tier=EmotionTier.LOVE,
        cost_amount=Decimal("100"),
        reward_tier=EmotionTier.NOSTALGIA,
        reward_amount=Decimal("10"),
        unlocks_emotion=PrimaryEmotion.ANGER,
        unlocks_tier=EmotionTier.NOSTALGIA
    ),
    TutorialCustomerConfig(
        id="thrill_seeker",
        name="Thrill Seeker",
        avatar="🎢",
        dialogue="Life's too predictable. I need some fear.",
        trigger_tier=EmotionTier.NOSTALGIA,
        trigger_amount=Decimal("500"),
        cost_tier=EmotionTier.NOSTALGIA,
        cost_amount=Decimal("500"),
        reward_tier=EmotionTier.SERENITY,
        reward_amount=Decimal("20"),
        unlocks_emotion=PrimaryEmotion.FEAR,
        unlocks_tier=EmotionTier.SERENITY
    ),
    TutorialCustomerConfig(
        id="boundary_setter",
        name="Boundary Setter",
        avatar="🛑",
        dialogue="I need to reject toxic people. Give me disgust.",
        trigger_tier=EmotionTier.SERENITY,
        trigger_amount=Decimal("1000"),
        cost_tier=EmotionTier.SERENITY,
        cost_amount=Decimal("1000"),
        reward_tier=EmotionTier.EUPHORIA,
        reward_amount=Decimal("50"),
        unlocks_emotion=PrimaryEmotion.DISGUST,
        unlocks_tier=EmotionTier.EUPHORIA
    ),
]


@dataclass
class Customer:
    """A customer in the emotion shop.

    Represents either a tutorial NPC or procedurally generated customer
    seeking emotional products. Tracks their needs, budget, patience, and
    relationship with the shop.

    Attributes:
        id: Unique identifier for this customer instance
        name: Display name of the customer
        avatar: Unicode emoji/symbol for visual representation
        customer_type: Category of customer (tutorial, regular, VIP, etc.)
        primary_need: The emotion tier they primarily desire
        need_intensity: How urgently they need it (0.0-1.0 scale)
        acceptable_purity: Minimum quality they'll accept (0-100%)
        budget: Maximum amount they can pay
        patience: Turns remaining before they leave (decreases each tick)
        dialogue: What they say when interacting
        visit_count: Number of times they've visited (1 for first visit)
        dependency_level: Addiction/dependency level (0.0-1.0, for ethical system)
        tutorial_config: Configuration data if this is a tutorial customer
    """
    id: str
    name: str
    avatar: str
    customer_type: CustomerType

    # Need
    primary_need: EmotionTier
    need_intensity: float = 1.0  # How badly they need it (0.0-1.0)
    acceptable_purity: float = 50.0  # Minimum quality (0-100%)

    # Economics
    budget: Decimal = field(default_factory=lambda: Decimal("100"))
    patience: int = 5  # Turns before leaving

    # Interaction
    dialogue: str = ""
    visit_count: int = 1
    dependency_level: float = 0.0  # 0.0-1.0 addiction scale

    # Tutorial specific
    tutorial_config: Optional[TutorialCustomerConfig] = None


class CustomerManager:
    """Manages customer generation, queue, and interactions.

    The CustomerManager handles the customer lifecycle:
    1. Checks for tutorial customer triggers
    2. Generates random customers (post-tutorial)
    3. Maintains customer queue
    4. Processes transactions
    5. Calculates satisfaction and reputation

    Attributes:
        state_manager: Reference to game state for resource management
        queue: List of customers waiting to be served
        max_queue_size: Maximum number of customers that can wait
        current_customer: The customer currently being served (if any)
        tutorial_customers_served: IDs of tutorial customers already served
    """

    def __init__(self, state_manager: "GameStateManager"):
        """Initialize the customer manager.

        Args:
            state_manager: Game state manager for resource tracking
        """
        self.state_manager = state_manager
        self.queue: List[Customer] = []
        self.max_queue_size: int = 5
        self.current_customer: Optional[Customer] = None
        self.tutorial_customers_served: List[str] = []
        self._on_customer_arrive: List[Callable[[Customer], None]] = []

    def subscribe_customer_arrive(self, callback: Callable[[Customer], None]) -> None:
        """Subscribe to customer arrival events.

        Observers will be notified when a new customer enters the queue.

        Args:
            callback: Function to call when customer arrives, receives Customer object
        """
        self._on_customer_arrive.append(callback)

    def _notify_customer_arrive(self, customer: Customer) -> None:
        """Notify subscribers of customer arrival.

        Args:
            customer: The customer that just arrived
        """
        for callback in self._on_customer_arrive:
            callback(customer)

    def check_tutorial_triggers(self) -> Optional[Customer]:
        """Check if any tutorial customer should appear.

        Iterates through TUTORIAL_CUSTOMERS in order and checks if the
        player has reached the required threshold for the next unserved
        tutorial customer.

        Returns:
            Customer object if one should appear, None otherwise
        """
        state = self.state_manager.state

        for config in TUTORIAL_CUSTOMERS:
            # Skip if already served
            if config.id in self.tutorial_customers_served:
                continue

            # Check trigger condition
            resource = state.resources[config.trigger_tier]
            if resource.amount >= config.trigger_amount:
                customer = Customer(
                    id=config.id,
                    name=config.name,
                    avatar=config.avatar,
                    customer_type=CustomerType.TUTORIAL,
                    primary_need=config.reward_tier,
                    dialogue=config.dialogue,
                    tutorial_config=config
                )
                return customer

        return None

    def serve_tutorial_customer(self, customer: Customer) -> bool:
        """Process a tutorial customer transaction.

        Tutorial customers have fixed trades that advance game progression.
        This method:
        1. Validates the customer has tutorial config
        2. Checks if player can afford the cost
        3. Spends the cost
        4. Unlocks new tiers and emotions
        5. Gives the reward
        6. Marks tutorial complete after all 5 are served

        Args:
            customer: The tutorial customer to serve

        Returns:
            True if transaction successful, False if player can't afford
        """
        if customer.tutorial_config is None:
            return False

        config = customer.tutorial_config

        # Check if player has required resources
        if not self.state_manager.spend_resource(config.cost_tier, config.cost_amount):
            return False

        # Unlock tier if specified (must be done before giving reward)
        if config.unlocks_tier:
            self.state_manager.unlock_resource(config.unlocks_tier)

        # Unlock primary emotion if specified
        if config.unlocks_emotion:
            self.state_manager.unlock_primary_emotion(config.unlocks_emotion)

        # Give reward (after unlocking so it can be added)
        self.state_manager.add_resource(config.reward_tier, config.reward_amount)

        # Mark as served
        self.tutorial_customers_served.append(config.id)
        self.state_manager.state.customers_served += 1

        # Check if tutorial complete (all 5 served)
        if len(self.tutorial_customers_served) >= 5:
            self.state_manager.state.tutorial_complete = True
            self.state_manager.state.queue_unlocked = True

        return True

    def generate_regular_customer(self) -> Customer:
        """Generate a random regular customer.

        Creates a procedurally generated customer with random attributes
        based on the current game state. Only generates needs for emotions
        that have been unlocked.

        Returns:
            Newly generated Customer object
        """
        names = ["Alex", "Jordan", "Sam", "Morgan", "Casey", "Riley", "Quinn", "Avery"]
        avatars = ["😀", "😢", "😤", "😰", "🙂", "😔", "😊", "😟"]

        # Get unlocked tiers for needs
        state = self.state_manager.state
        unlocked_tiers = [
            tier for tier, resource in state.resources.items()
            if resource.unlocked and tier != EmotionTier.SMILES
        ]

        if not unlocked_tiers:
            unlocked_tiers = [EmotionTier.JOY]

        return Customer(
            id=f"customer_{random.randint(1000, 9999)}",
            name=random.choice(names),
            avatar=random.choice(avatars),
            customer_type=CustomerType.REGULAR,
            primary_need=random.choice(unlocked_tiers),
            budget=Decimal(str(random.randint(50, 500))),
            patience=random.randint(3, 7),
            dialogue=self._generate_dialogue()
        )

    def _generate_dialogue(self) -> str:
        """Generate random customer dialogue.

        Returns:
            Random dialogue string from predefined pool
        """
        dialogues = [
            "I could really use some emotional support today.",
            "Do you have what I'm looking for?",
            "I've heard good things about this shop.",
            "Can you help me feel something different?",
            "My friend recommended your services.",
        ]
        return random.choice(dialogues)

    def add_to_queue(self, customer: Customer) -> bool:
        """Add a customer to the queue.

        Args:
            customer: Customer to add to queue

        Returns:
            False if queue is full, True if successfully added
        """
        if len(self.queue) >= self.max_queue_size:
            return False
        self.queue.append(customer)
        self._notify_customer_arrive(customer)
        return True

    def serve_customer(
        self,
        customer: Customer,
        emotion_tier: EmotionTier,
        amount: Decimal
    ) -> float:
        """Serve a customer from the queue.

        Processes a transaction where the player provides a specific emotion
        to fulfill (or attempt to fulfill) a customer's needs. Calculates
        satisfaction based on emotion match, purity, and other factors.

        Args:
            customer: The customer being served
            emotion_tier: The emotion tier being provided
            amount: Amount of the emotion being given

        Returns:
            Satisfaction score from 0.0 to 100.0
        """
        state = self.state_manager.state
        resource = state.resources[emotion_tier]

        # Check if we can fulfill
        if resource.amount < amount:
            return 0.0

        # Spend the resource
        self.state_manager.spend_resource(emotion_tier, amount)

        # Calculate satisfaction
        satisfaction = self._calculate_satisfaction(customer, emotion_tier, resource.purity)

        # Update stats
        state.customers_served += 1
        self._update_reputation(satisfaction)

        # Remove from queue
        if customer in self.queue:
            self.queue.remove(customer)

        return satisfaction

    def _calculate_satisfaction(
        self,
        customer: Customer,
        provided_tier: EmotionTier,
        purity: float
    ) -> float:
        """Calculate customer satisfaction score.

        Satisfaction is based on:
        - Base: 50%
        - Emotion Match: +30% if exact need, -20% if wrong
        - Purity Bonus: +1% per 2% purity above 50%
        - Purity Penalty: -2% per 1% purity below acceptable threshold

        Args:
            customer: The customer being evaluated
            provided_tier: The emotion tier that was provided
            purity: The purity level of the provided emotion (0-100%)

        Returns:
            Satisfaction score clamped to 0.0-100.0 range
        """
        satisfaction = 50.0

        # Emotion match bonus/penalty
        if provided_tier == customer.primary_need:
            satisfaction += 30.0
        else:
            satisfaction -= 20.0

        # Purity bonus/penalty
        purity_threshold = customer.acceptable_purity
        if purity >= purity_threshold:
            # Bonus for high purity
            bonus = (purity - 50.0) / 2.0
            satisfaction += bonus
        else:
            # Penalty for low purity
            penalty = (purity_threshold - purity) * 2.0
            satisfaction -= penalty

        # Clamp to valid range
        return max(0.0, min(100.0, satisfaction))

    def _update_reputation(self, satisfaction: float) -> None:
        """Update shop reputation based on customer satisfaction.

        Uses a rolling average approach where recent satisfactions are
        weighted more heavily than past ones. Converts satisfaction
        (0-100%) to stars (0-5) for the reputation system.

        Args:
            satisfaction: The satisfaction score from latest customer (0-100%)
        """
        state = self.state_manager.state
        current = state.reputation

        # Convert satisfaction (0-100) to stars (0-5)
        stars = satisfaction / 20.0

        # Weighted average (approximates last ~20 customers)
        state.reputation = (current * 0.95) + (stars * 0.05)

    def tick_patience(self) -> None:
        """Reduce patience for all queued customers.

        Called each game tick to decrease patience for waiting customers.
        Customers who run out of patience leave and damage reputation.
        This creates time pressure to serve customers efficiently.
        """
        leaving = []
        for customer in self.queue:
            customer.patience -= 1
            if customer.patience <= 0:
                leaving.append(customer)

        for customer in leaving:
            self.queue.remove(customer)
            # Bad reputation for letting them leave
            self._update_reputation(0.0)
