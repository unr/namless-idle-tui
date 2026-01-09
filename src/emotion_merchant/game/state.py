"""Central game state management for Emotion Merchant.

This module provides the core game state container and management system,
including resource tracking, progression flags, and an observer pattern
for UI updates.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, Optional, Callable, List, Any
from datetime import datetime
import json

from .resources import EmotionTier, PrimaryEmotion, EMOTION_CONFIGS


@dataclass
class ResourceState:
    """State for a single resource type.

    Attributes:
        amount: Current amount of this resource
        storage_capacity: Maximum amount that can be stored
        purity: Quality of the resource (0-100%)
        producers: Number of active producers for this resource
        unlocked: Whether this resource is available to the player
    """
    amount: Decimal = field(default_factory=lambda: Decimal("0"))
    storage_capacity: int = 100
    purity: float = 100.0  # 0-100%
    producers: int = 0
    unlocked: bool = False

    @property
    def storage_percent(self) -> float:
        """Calculate percentage of storage capacity used.

        Returns:
            Percentage from 0.0 to 100.0
        """
        if self.storage_capacity == 0:
            return 100.0
        return float(self.amount / self.storage_capacity * 100)

    @property
    def is_full(self) -> bool:
        """Check if storage is at capacity.

        Returns:
            True if amount >= storage_capacity
        """
        return self.amount >= self.storage_capacity

    @property
    def is_empty(self) -> bool:
        """Check if storage is empty.

        Returns:
            True if amount is 0
        """
        return self.amount == Decimal("0")

    def can_afford(self, cost: Decimal) -> bool:
        """Check if there's enough of this resource to afford a cost.

        Args:
            cost: Amount needed

        Returns:
            True if amount >= cost
        """
        return self.amount >= cost


@dataclass
class GameState:
    """Central game state container.

    This dataclass holds all persistent game state including resources,
    progression flags, and player statistics.
    """
    # Resources
    resources: Dict[EmotionTier, ResourceState] = field(default_factory=dict)
    primary_emotions: Dict[PrimaryEmotion, bool] = field(default_factory=dict)

    # Progress
    click_power: Decimal = field(default_factory=lambda: Decimal("5"))
    global_multiplier: Decimal = field(default_factory=lambda: Decimal("1"))

    # Customer/Story
    customers_served: int = 0
    ethical_score: float = 50.0  # 0-100 scale
    reputation: float = 3.0      # 0-5 star rating

    # Prestige
    prestige_count: int = 0
    emotional_depth: Decimal = field(default_factory=lambda: Decimal("0"))

    # Progression flags
    tutorial_complete: bool = False
    alchemy_unlocked: bool = False
    queue_unlocked: bool = False

    # Meta
    total_clicks: int = 0
    play_time_seconds: float = 0.0
    last_save: Optional[datetime] = None

    def __post_init__(self):
        """Initialize default resource states if not loaded from save."""
        # Initialize all resource states
        if not self.resources:
            for tier in EmotionTier:
                config = EMOTION_CONFIGS[tier]
                self.resources[tier] = ResourceState(
                    storage_capacity=config.base_storage,
                    unlocked=(tier == EmotionTier.SMILES)  # Only Smiles unlocked initially
                )

        # Initialize primary emotions
        if not self.primary_emotions:
            for emotion in PrimaryEmotion:
                self.primary_emotions[emotion] = False


class GameStateManager:
    """Manages game state with observer pattern for UI updates.

    This class wraps the GameState dataclass and provides methods for
    modifying state while notifying observers of changes. This enables
    reactive UI updates.
    """

    def __init__(self):
        """Initialize a new game state manager with default state."""
        self.state = GameState()
        self._observers: List[Callable[[str, Any], None]] = []

    def subscribe(self, callback: Callable[[str, Any], None]) -> None:
        """Subscribe to state changes.

        Args:
            callback: Function to call when state changes.
                      Receives (event_name, event_data) parameters.
        """
        if callback not in self._observers:
            self._observers.append(callback)

    def unsubscribe(self, callback: Callable[[str, Any], None]) -> None:
        """Unsubscribe from state changes.

        Args:
            callback: The callback function to remove
        """
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify(self, event: str, data: Any = None) -> None:
        """Notify all observers of state change.

        Args:
            event: Name of the event that occurred
            data: Optional data associated with the event
        """
        for callback in self._observers:
            try:
                callback(event, data)
            except Exception as e:
                # Log error but don't break other observers
                print(f"Error in observer callback: {e}")

    def add_resource(self, tier: EmotionTier, amount: Decimal) -> Decimal:
        """Add resources, respecting storage limits.

        Args:
            tier: The emotion tier to add to
            amount: Amount to add

        Returns:
            Actual amount added (may be less than requested if storage is full)
        """
        resource = self.state.resources[tier]
        if not resource.unlocked:
            return Decimal("0")

        space_available = Decimal(resource.storage_capacity) - resource.amount
        actual_add = min(amount, space_available)

        if actual_add > 0:
            resource.amount += actual_add
            self._notify("resource_changed", {
                "tier": tier,
                "amount": resource.amount,
                "added": actual_add
            })

        return actual_add

    def spend_resource(self, tier: EmotionTier, amount: Decimal) -> bool:
        """Spend resources if available.

        Args:
            tier: The emotion tier to spend from
            amount: Amount to spend

        Returns:
            True if successful, False if insufficient resources
        """
        resource = self.state.resources[tier]
        if resource.amount >= amount:
            resource.amount -= amount
            self._notify("resource_changed", {
                "tier": tier,
                "amount": resource.amount,
                "spent": amount
            })
            return True
        return False

    def can_afford(self, tier: EmotionTier, amount: Decimal) -> bool:
        """Check if player can afford a cost.

        Args:
            tier: The emotion tier to check
            amount: Amount needed

        Returns:
            True if player has enough resources
        """
        resource = self.state.resources[tier]
        return resource.unlocked and resource.amount >= amount

    def click_harvest(self) -> Decimal:
        """Process a manual click harvest.

        Returns:
            Amount of Smiles harvested
        """
        base_amount = self.state.click_power * self.state.global_multiplier
        actual = self.add_resource(EmotionTier.SMILES, base_amount)
        self.state.total_clicks += 1
        self._notify("click", {"amount": actual})
        return actual

    def unlock_resource(self, tier: EmotionTier) -> None:
        """Unlock a resource tier.

        Args:
            tier: The emotion tier to unlock
        """
        resource = self.state.resources[tier]
        if not resource.unlocked:
            resource.unlocked = True
            self._notify("resource_unlocked", {"tier": tier})

    def unlock_primary_emotion(self, emotion: PrimaryEmotion) -> None:
        """Unlock a primary emotion.

        Args:
            emotion: The primary emotion to unlock
        """
        if not self.state.primary_emotions[emotion]:
            self.state.primary_emotions[emotion] = True
            self._notify("emotion_unlocked", {"emotion": emotion})

    def add_producer(self, tier: EmotionTier, count: int = 1) -> None:
        """Add producers for a resource tier.

        Args:
            tier: The emotion tier to add producers for
            count: Number of producers to add (default: 1)
        """
        resource = self.state.resources[tier]
        resource.producers += count
        self._notify("producer_added", {
            "tier": tier,
            "count": count,
            "total": resource.producers
        })

    def upgrade_storage(self, tier: EmotionTier, new_capacity: int) -> None:
        """Upgrade storage capacity for a resource.

        Args:
            tier: The emotion tier to upgrade
            new_capacity: New storage capacity
        """
        resource = self.state.resources[tier]
        old_capacity = resource.storage_capacity
        resource.storage_capacity = min(new_capacity, EMOTION_CONFIGS[tier].max_storage)
        self._notify("storage_upgraded", {
            "tier": tier,
            "old_capacity": old_capacity,
            "new_capacity": resource.storage_capacity
        })

    def serve_customer(self, ethical_choice: Optional[bool] = None) -> None:
        """Record a customer being served.

        Args:
            ethical_choice: True if ethical choice, False if unethical, None if neutral
        """
        self.state.customers_served += 1

        if ethical_choice is True:
            self.state.ethical_score = min(100.0, self.state.ethical_score + 1.0)
        elif ethical_choice is False:
            self.state.ethical_score = max(0.0, self.state.ethical_score - 1.0)

        self._notify("customer_served", {
            "total": self.state.customers_served,
            "ethical_score": self.state.ethical_score
        })

    def update_reputation(self, delta: float) -> None:
        """Update player reputation.

        Args:
            delta: Amount to change reputation by (can be negative)
        """
        old_reputation = self.state.reputation
        self.state.reputation = max(0.0, min(5.0, self.state.reputation + delta))

        if self.state.reputation != old_reputation:
            self._notify("reputation_changed", {
                "old": old_reputation,
                "new": self.state.reputation,
                "delta": delta
            })

    def prestige(self, depth_gained: Decimal) -> None:
        """Perform a prestige reset.

        Args:
            depth_gained: Amount of Emotional Depth gained from prestige
        """
        self.state.prestige_count += 1
        self.state.emotional_depth += depth_gained

        # Reset game state but keep prestige progress
        old_depth = self.state.emotional_depth
        old_count = self.state.prestige_count
        old_play_time = self.state.play_time_seconds

        self.state = GameState()
        self.state.emotional_depth = old_depth
        self.state.prestige_count = old_count
        self.state.play_time_seconds = old_play_time

        self._notify("prestige", {
            "count": self.state.prestige_count,
            "depth": self.state.emotional_depth,
            "depth_gained": depth_gained
        })

    def update_play_time(self, delta_seconds: float) -> None:
        """Update total play time.

        Args:
            delta_seconds: Seconds to add to play time
        """
        self.state.play_time_seconds += delta_seconds

    def to_dict(self) -> dict:
        """Serialize state to dictionary for saving.

        Returns:
            Dictionary representation of game state
        """
        return {
            "resources": {
                tier.name: {
                    "amount": str(state.amount),
                    "storage_capacity": state.storage_capacity,
                    "purity": state.purity,
                    "producers": state.producers,
                    "unlocked": state.unlocked
                }
                for tier, state in self.state.resources.items()
            },
            "primary_emotions": {
                emotion.value: unlocked
                for emotion, unlocked in self.state.primary_emotions.items()
            },
            "click_power": str(self.state.click_power),
            "global_multiplier": str(self.state.global_multiplier),
            "customers_served": self.state.customers_served,
            "ethical_score": self.state.ethical_score,
            "reputation": self.state.reputation,
            "prestige_count": self.state.prestige_count,
            "emotional_depth": str(self.state.emotional_depth),
            "tutorial_complete": self.state.tutorial_complete,
            "alchemy_unlocked": self.state.alchemy_unlocked,
            "queue_unlocked": self.state.queue_unlocked,
            "total_clicks": self.state.total_clicks,
            "play_time_seconds": self.state.play_time_seconds,
            "last_save": self.state.last_save.isoformat() if self.state.last_save else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GameStateManager":
        """Load state from dictionary.

        Args:
            data: Dictionary representation of game state

        Returns:
            New GameStateManager with loaded state
        """
        manager = cls()

        # Load resources
        if "resources" in data:
            for tier_name, resource_data in data["resources"].items():
                tier = EmotionTier[tier_name]
                resource = manager.state.resources[tier]
                resource.amount = Decimal(resource_data["amount"])
                resource.storage_capacity = resource_data["storage_capacity"]
                resource.purity = resource_data["purity"]
                resource.producers = resource_data["producers"]
                resource.unlocked = resource_data["unlocked"]

        # Load primary emotions
        if "primary_emotions" in data:
            for emotion_value, unlocked in data["primary_emotions"].items():
                emotion = PrimaryEmotion(emotion_value)
                manager.state.primary_emotions[emotion] = unlocked

        # Load simple fields
        if "click_power" in data:
            manager.state.click_power = Decimal(data["click_power"])
        if "global_multiplier" in data:
            manager.state.global_multiplier = Decimal(data["global_multiplier"])
        if "customers_served" in data:
            manager.state.customers_served = data["customers_served"]
        if "ethical_score" in data:
            manager.state.ethical_score = data["ethical_score"]
        if "reputation" in data:
            manager.state.reputation = data["reputation"]
        if "prestige_count" in data:
            manager.state.prestige_count = data["prestige_count"]
        if "emotional_depth" in data:
            manager.state.emotional_depth = Decimal(data["emotional_depth"])
        if "tutorial_complete" in data:
            manager.state.tutorial_complete = data["tutorial_complete"]
        if "alchemy_unlocked" in data:
            manager.state.alchemy_unlocked = data["alchemy_unlocked"]
        if "queue_unlocked" in data:
            manager.state.queue_unlocked = data["queue_unlocked"]
        if "total_clicks" in data:
            manager.state.total_clicks = data["total_clicks"]
        if "play_time_seconds" in data:
            manager.state.play_time_seconds = data["play_time_seconds"]
        if "last_save" in data and data["last_save"]:
            manager.state.last_save = datetime.fromisoformat(data["last_save"])

        return manager

    def save_to_file(self, filepath: str) -> None:
        """Save game state to a JSON file.

        Args:
            filepath: Path to save file
        """
        self.state.last_save = datetime.now()
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str) -> "GameStateManager":
        """Load game state from a JSON file.

        Args:
            filepath: Path to save file

        Returns:
            GameStateManager with loaded state

        Raises:
            FileNotFoundError: If save file doesn't exist
            json.JSONDecodeError: If save file is corrupted
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
