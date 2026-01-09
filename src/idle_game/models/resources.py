"""
Resource management classes for the Emotion Merchant idle game.

This module handles emotion resources, their storage, purity tracking,
and all production/cost calculations.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, Optional

from src.idle_game.data.emotions import EmotionDefinition, get_emotion


@dataclass
class EmotionResource:
    """Represents a stored emotion resource with amount, purity, and capacity.

    Attributes:
        emotion_type: The name of the emotion (e.g., "smiles", "joy")
        amount: Current amount stored (using Decimal for precision)
        purity: Quality percentage (0-100), affects sell price and satisfaction
        storage_capacity: Current maximum storage capacity
        producer_count: Number of producers (buildings) generating this emotion
    """
    emotion_type: str
    amount: Decimal = Decimal("0")
    purity: Decimal = Decimal("100.0")
    storage_capacity: int = 0
    producer_count: int = 0

    def __post_init__(self):
        """Initialize storage capacity to the minimum for this emotion type."""
        if self.storage_capacity == 0:
            emotion = get_emotion(self.emotion_type)
            self.storage_capacity = emotion.min_storage

    @property
    def storage_percentage(self) -> float:
        """Calculate the percentage of storage currently used.

        Returns:
            Float between 0.0 and 1.0+ (can exceed 1.0 if overflowing)
        """
        if self.storage_capacity == 0:
            return 0.0
        return float(self.amount / Decimal(self.storage_capacity))

    @property
    def is_full(self) -> bool:
        """Check if storage is at or near capacity (95%+)."""
        return self.storage_percentage >= 0.95

    @property
    def is_overflowing(self) -> bool:
        """Check if storage has exceeded capacity."""
        return self.storage_percentage > 1.0

    def add_amount(self, amount: Decimal) -> Decimal:
        """Add resources, respecting storage capacity.

        Args:
            amount: Amount to add

        Returns:
            Amount that was actually added (may be less if storage is full)
        """
        if amount <= 0:
            return Decimal("0")

        available_space = Decimal(self.storage_capacity) - self.amount
        if available_space <= 0:
            return Decimal("0")

        amount_to_add = min(amount, available_space)
        self.amount += amount_to_add
        return amount_to_add

    def remove_amount(self, amount: Decimal) -> bool:
        """Remove resources if available.

        Args:
            amount: Amount to remove

        Returns:
            True if the full amount was removed, False if insufficient resources
        """
        if amount <= 0:
            return True

        if self.amount >= amount:
            self.amount -= amount
            return True
        return False

    def can_afford(self, amount: Decimal) -> bool:
        """Check if we have enough of this resource.

        Args:
            amount: Amount to check

        Returns:
            True if we have at least this amount
        """
        return self.amount >= amount


class ResourceCalculator:
    """Handles all production and cost calculations for resources.

    This class implements the game's mathematical formulas for:
    - Exponential cost scaling
    - Production rate calculations with multipliers
    - Purity decay over time
    - Storage efficiency modifiers
    """

    # Cost growth formula: base_cost * (growth_rate ^ count)
    COST_GROWTH_RATE = Decimal("1.15")

    # Purity decay rate: 0.1% per minute in storage
    PURITY_DECAY_PER_MINUTE = Decimal("0.1")

    # Storage state modifiers for production
    STORAGE_MODIFIERS = {
        "empty": Decimal("1.0"),      # 0-25%: Normal production
        "moderate": Decimal("1.0"),   # 25-75%: Normal production
        "near_full": Decimal("0.5"),  # 75-95%: Reduced production
        "full": Decimal("0.0"),       # 95%+: Production stops
    }

    @staticmethod
    def calculate_producer_cost(
        base_cost: Decimal,
        current_count: int
    ) -> Decimal:
        """Calculate the cost to purchase the next producer.

        Uses exponential scaling: base_cost * (1.15 ^ current_count)

        Args:
            base_cost: The base cost of the first producer
            current_count: Number of producers already owned

        Returns:
            Cost for the next producer
        """
        return base_cost * (ResourceCalculator.COST_GROWTH_RATE ** current_count)

    @staticmethod
    def calculate_production(
        base_rate: Decimal,
        producer_count: int,
        global_multiplier: Decimal = Decimal("1.0"),
        prestige_bonus: Decimal = Decimal("1.0"),
        storage_state: Optional[str] = None
    ) -> Decimal:
        """Calculate the total production rate per second.

        Formula: base_rate * producer_count * global_multiplier * prestige_bonus * storage_modifier

        Args:
            base_rate: Base production rate per producer
            producer_count: Number of producers owned
            global_multiplier: Global production multiplier from upgrades
            prestige_bonus: Multiplier from prestige (Emotional Depth)
            storage_state: Current storage state ('empty', 'moderate', 'near_full', 'full')

        Returns:
            Total production per second
        """
        if producer_count == 0:
            return Decimal("0")

        production = base_rate * Decimal(producer_count)
        production *= global_multiplier
        production *= prestige_bonus

        # Apply storage modifier if provided
        if storage_state:
            modifier = ResourceCalculator.STORAGE_MODIFIERS.get(
                storage_state, Decimal("1.0")
            )
            production *= modifier

        return production

    @staticmethod
    def calculate_purity_decay(
        current_purity: Decimal,
        delta_time: float
    ) -> Decimal:
        """Calculate purity decay over time.

        Purity decays at 0.1% per minute in storage.

        Args:
            current_purity: Current purity percentage (0-100)
            delta_time: Time elapsed in seconds

        Returns:
            New purity value after decay
        """
        if current_purity <= Decimal("0"):
            return Decimal("0")

        decay_per_second = ResourceCalculator.PURITY_DECAY_PER_MINUTE / Decimal("60")
        decay_amount = decay_per_second * Decimal(str(delta_time))

        new_purity = current_purity - decay_amount
        return max(Decimal("0"), new_purity)

    @staticmethod
    def get_storage_state(storage_percentage: float) -> str:
        """Determine the storage state based on fill percentage.

        Args:
            storage_percentage: Float between 0.0 and 1.0+

        Returns:
            Storage state: 'empty', 'moderate', 'near_full', or 'full'
        """
        if storage_percentage >= 0.95:
            return "full"
        elif storage_percentage >= 0.75:
            return "near_full"
        elif storage_percentage >= 0.25:
            return "moderate"
        else:
            return "empty"

    @staticmethod
    def calculate_prestige_bonus(emotional_depth: int) -> Decimal:
        """Calculate the prestige production bonus.

        Formula: 1 + (emotional_depth * 0.03)
        Each point of Emotional Depth gives +3% to all production.

        Args:
            emotional_depth: Total Emotional Depth accumulated

        Returns:
            Multiplier to apply to all production
        """
        return Decimal("1.0") + (Decimal(str(emotional_depth)) * Decimal("0.03"))

    @staticmethod
    def calculate_click_power(
        base_click: Decimal,
        click_multiplier: Decimal = Decimal("1.0"),
        mood_bonus: Decimal = Decimal("1.0")
    ) -> Decimal:
        """Calculate the amount gained from a manual click.

        Formula: base_click * click_multiplier * mood_bonus

        Args:
            base_click: Base click value (from emotion definition)
            click_multiplier: Multiplier from upgrades
            mood_bonus: Multiplier from mood rating (0.5x - 2x)

        Returns:
            Total amount gained per click
        """
        return base_click * click_multiplier * mood_bonus

    @staticmethod
    def calculate_purity_price_modifier(purity: Decimal) -> Decimal:
        """Calculate sell price modifier based on purity.

        Formula: purity% × base_price

        Args:
            purity: Purity percentage (0-100)

        Returns:
            Multiplier to apply to base price (0.0 - 1.0)
        """
        return purity / Decimal("100")

    @staticmethod
    def calculate_offline_production(
        production_rate: Decimal,
        offline_seconds: float,
        storage_capacity: int,
        offline_efficiency: Decimal = Decimal("1.0")
    ) -> Decimal:
        """Calculate resources gained during offline time.

        Production is capped by storage capacity and affected by offline efficiency.

        Args:
            production_rate: Production per second
            offline_seconds: Time spent offline in seconds
            storage_capacity: Maximum storage capacity
            offline_efficiency: Multiplier for offline production (upgradeable)

        Returns:
            Amount of resources gained (capped by storage)
        """
        if offline_seconds <= 0:
            return Decimal("0")

        # Calculate total production
        raw_production = production_rate * Decimal(str(offline_seconds))
        raw_production *= offline_efficiency

        # Cap by storage capacity
        max_amount = Decimal(str(storage_capacity))
        return min(raw_production, max_amount)
