"""
Core game state management for the Emotion Merchant idle game.

This module contains the GameState class which holds all game state using
Textual's reactive attributes for automatic UI updates.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Set

from textual.reactive import Reactive

from src.idle_game.data.emotions import EMOTION_TIERS, get_emotion
from src.idle_game.models.resources import EmotionResource, ResourceCalculator


class GameState:
    """Central game state with reactive attributes for UI updates.

    All attributes that affect the UI should be declared as reactive()
    to enable automatic data binding and UI updates.

    Attributes:
        resources: Dictionary mapping emotion_type -> EmotionResource
        unlocked_emotions: Set of emotion names that have been unlocked
        click_multiplier: Multiplier for manual clicking
        global_production_multiplier: Global multiplier for all production
        offline_efficiency: Multiplier for offline production (upgradeable)

        # Statistics
        total_clicks: Total number of manual clicks performed
        customers_served: Total customers served
        recipes_discovered: Set of recipe names discovered

        # Prestige
        prestige_count: Number of times prestiged
        emotional_depth: Total Emotional Depth currency accumulated

        # Metadata
        last_save_time: Timestamp of last save
        total_playtime: Total seconds played
        game_paused: Whether the game is currently paused
    """

    # Resources - dictionary of EmotionResource objects
    resources: Dict[str, EmotionResource]

    # Unlocked emotions - set
    unlocked_emotions: Set[str]

    # Multipliers - decimals
    click_multiplier: Decimal
    global_production_multiplier: Decimal
    offline_efficiency: Decimal
    mood_rating: Decimal

    # Statistics - integers/sets
    total_clicks: int
    customers_served: int
    recipes_discovered: Set[str]

    # Prestige - integers
    prestige_count: int
    emotional_depth: int

    # Ethical system - decimal
    ethical_score: Decimal

    # Metadata
    last_save_time: datetime
    total_playtime: float
    game_paused: bool

    # Tutorial progress
    tutorial_completed: bool
    tutorial_stage: int

    def __init__(self):
        """Initialize the game state with default values."""
        # Initialize with Smiles unlocked by default
        self.resources = {"smiles": EmotionResource("smiles", amount=Decimal("0"))}
        self.unlocked_emotions = {"smiles"}
        self.click_multiplier = Decimal("1.0")
        self.global_production_multiplier = Decimal("1.0")
        self.offline_efficiency = Decimal("1.0")
        self.mood_rating = Decimal("1.0")
        self.total_clicks = 0
        self.customers_served = 0
        self.recipes_discovered = set()
        self.prestige_count = 0
        self.emotional_depth = 0
        self.ethical_score = Decimal("50.0")
        self.last_save_time = datetime.now()
        self.total_playtime = 0.0
        self.game_paused = False
        self.tutorial_completed = False
        self.tutorial_stage = 0

    def unlock_emotion(self, emotion_type: str) -> bool:
        """Unlock a new emotion type.

        Args:
            emotion_type: Name of the emotion to unlock

        Returns:
            True if newly unlocked, False if already unlocked
        """
        emotion_type = emotion_type.lower()
        if emotion_type in self.unlocked_emotions:
            return False

        # Create the resource entry
        self.resources[emotion_type] = EmotionResource(emotion_type)
        self.unlocked_emotions = self.unlocked_emotions | {emotion_type}
        return True

    def get_resource(self, emotion_type: str) -> EmotionResource:
        """Get an emotion resource, creating it if necessary.

        Args:
            emotion_type: Name of the emotion

        Returns:
            The EmotionResource object
        """
        emotion_type = emotion_type.lower()
        if emotion_type not in self.resources:
            self.resources[emotion_type] = EmotionResource(emotion_type)
        return self.resources[emotion_type]

    def perform_click(self) -> Decimal:
        """Perform a manual click to harvest Smiles.

        Returns:
            Amount of Smiles harvested
        """
        smiles = self.get_resource("smiles")
        emotion = get_emotion("smiles")

        # Calculate click power
        amount = ResourceCalculator.calculate_click_power(
            emotion.base_cost,  # Base click value
            self.click_multiplier,
            self.mood_rating
        )

        # Add to resources
        added = smiles.add_amount(amount)
        self.total_clicks += 1

        # Trigger resource update for reactivity
        self.resources = dict(self.resources)

        return added

    def purchase_producer(self, emotion_type: str) -> bool:
        """Purchase a producer for an emotion type.

        Args:
            emotion_type: Name of the emotion to purchase producer for

        Returns:
            True if purchase successful, False if cannot afford
        """
        emotion_type = emotion_type.lower()

        # Check if emotion is unlocked
        if emotion_type not in self.unlocked_emotions:
            return False

        emotion = get_emotion(emotion_type)
        resource = self.get_resource(emotion_type)

        # Calculate cost
        cost = ResourceCalculator.calculate_producer_cost(
            emotion.base_cost,
            resource.producer_count
        )

        # For tier 0 (smiles), we can't purchase producers
        if emotion.tier == 0:
            return False

        # Check if we can afford (need to pay in the emotion below this tier)
        # For Joy (tier 1), we pay in Smiles (tier 0)
        if emotion.tier == 1:
            payment_resource = self.get_resource("smiles")
        else:
            # Find the emotion this one costs
            payment_emotion_name = None
            for name in EMOTION_TIERS:
                e = get_emotion(name)
                if e.produces == emotion_type:
                    payment_emotion_name = name
                    break

            if not payment_emotion_name:
                return False

            payment_resource = self.get_resource(payment_emotion_name)

        # Check affordability
        if not payment_resource.can_afford(cost):
            return False

        # Make purchase
        payment_resource.remove_amount(cost)
        resource.producer_count += 1

        # Trigger resource update for reactivity
        self.resources = dict(self.resources)

        return True

    def can_afford_producer(self, emotion_type: str) -> bool:
        """Check if we can afford to buy the next producer.

        Args:
            emotion_type: Name of the emotion

        Returns:
            True if we can afford it
        """
        emotion_type = emotion_type.lower()

        if emotion_type not in self.unlocked_emotions:
            return False

        emotion = get_emotion(emotion_type)
        resource = self.get_resource(emotion_type)

        cost = ResourceCalculator.calculate_producer_cost(
            emotion.base_cost,
            resource.producer_count
        )

        if emotion.tier == 0:
            return False

        # Find payment resource
        if emotion.tier == 1:
            payment_resource = self.get_resource("smiles")
        else:
            payment_emotion_name = None
            for name in EMOTION_TIERS:
                e = get_emotion(name)
                if e.produces == emotion_type:
                    payment_emotion_name = name
                    break

            if not payment_emotion_name:
                return False

            payment_resource = self.get_resource(payment_emotion_name)

        return payment_resource.can_afford(cost)

    def get_prestige_bonus(self) -> Decimal:
        """Calculate the current prestige production bonus.

        Returns:
            Multiplier from Emotional Depth
        """
        return ResourceCalculator.calculate_prestige_bonus(self.emotional_depth)

    def discover_recipe(self, recipe_name: str) -> bool:
        """Discover a new recipe.

        Args:
            recipe_name: Name of the recipe

        Returns:
            True if newly discovered, False if already known
        """
        if recipe_name in self.recipes_discovered:
            return False

        self.recipes_discovered = self.recipes_discovered | {recipe_name}
        return True

    def adjust_ethical_score(self, change: Decimal) -> None:
        """Adjust the ethical score.

        Args:
            change: Amount to change (positive or negative)
        """
        new_score = self.ethical_score + change
        # Clamp between 0 and 100
        self.ethical_score = max(Decimal("0"), min(Decimal("100"), new_score))

    def reset_for_prestige(self) -> int:
        """Reset the game state for prestige, calculating Emotional Depth gained.

        Returns:
            Amount of Emotional Depth gained from this prestige
        """
        # Calculate Emotional Depth gain
        # Formula: (Recipes × Satisfaction × Ethics) / 100
        # For now, simplified calculation
        recipes_bonus = len(self.recipes_discovered)
        satisfaction_bonus = self.customers_served // 10  # 1 point per 10 customers
        ethics_bonus = float(self.ethical_score) / 100.0

        ed_gained = int((recipes_bonus + satisfaction_bonus) * ethics_bonus)

        # Update prestige data
        self.emotional_depth += ed_gained
        self.prestige_count += 1

        # Reset resources (keep only smiles, reset amount)
        self.resources = {"smiles": EmotionResource("smiles", amount=Decimal("0"))}
        self.unlocked_emotions = {"smiles"}

        # Reset statistics (keep prestige data and ethical score)
        self.total_clicks = 0
        self.customers_served = 0
        self.recipes_discovered = set()

        # Reset multipliers (except prestige bonus)
        self.click_multiplier = Decimal("1.0")
        self.global_production_multiplier = Decimal("1.0")
        self.mood_rating = Decimal("1.0")

        # Reset tutorial
        self.tutorial_completed = False
        self.tutorial_stage = 0

        return ed_gained
