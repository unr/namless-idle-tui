"""
Game loop and update logic for the Emotion Merchant idle game.

This module handles the core game loop, including passive resource generation,
purity decay, and storage management with delta-time based calculations.
"""

from decimal import Decimal
from typing import Optional

from src.idle_game.models.game_state import GameState
from src.idle_game.models.resources import ResourceCalculator
from src.idle_game.data.emotions import get_emotion


class GameLoop:
    """Manages the game update loop with delta-time calculations.

    The game loop processes passive generation, purity decay, and storage
    checks at regular intervals using frame-rate independent calculations.
    """

    def __init__(self, game_state: GameState):
        """Initialize the game loop.

        Args:
            game_state: The game state to update
        """
        self.game_state = game_state
        self.accumulated_time = 0.0

    def update(self, delta_time: float) -> None:
        """Main update method called each frame.

        Args:
            delta_time: Time elapsed since last update in seconds
        """
        # Skip updates if game is paused
        if self.game_state.game_paused:
            return

        # Update total playtime
        self.game_state.total_playtime += delta_time

        # Apply game logic
        self.apply_passive_generation(delta_time)
        self.apply_purity_decay(delta_time)
        self.check_storage_capacity()

    def apply_passive_generation(self, delta_time: float) -> None:
        """Apply passive resource generation based on producers.

        Args:
            delta_time: Time elapsed in seconds
        """
        if delta_time <= 0:
            return

        # Calculate prestige bonus once
        prestige_bonus = self.game_state.get_prestige_bonus()

        # Process each emotion type
        for emotion_type, resource in self.game_state.resources.items():
            # Skip if no producers
            if resource.producer_count == 0:
                continue

            # Get emotion definition
            emotion = get_emotion(emotion_type)

            # Skip tier 0 (smiles don't produce anything themselves)
            if emotion.tier == 0:
                continue

            # Get the emotion this produces
            produced_emotion = emotion.produces
            if not produced_emotion:
                continue

            # Get or create the target resource
            target_resource = self.game_state.get_resource(produced_emotion)

            # Get storage state for production modifier
            storage_state = ResourceCalculator.get_storage_state(
                target_resource.storage_percentage
            )

            # Calculate production rate
            production_rate = ResourceCalculator.calculate_production(
                emotion.production_rate,
                resource.producer_count,
                self.game_state.global_production_multiplier,
                prestige_bonus,
                storage_state
            )

            # Calculate amount produced this frame
            amount_produced = production_rate * Decimal(str(delta_time))

            # Add to target resource (respects storage capacity)
            if amount_produced > Decimal("0"):
                target_resource.add_amount(amount_produced)

        # Trigger reactivity update
        self.game_state.resources = dict(self.game_state.resources)

    def apply_purity_decay(self, delta_time: float) -> None:
        """Apply purity decay to all stored emotions.

        Args:
            delta_time: Time elapsed in seconds
        """
        if delta_time <= 0:
            return

        # Apply decay to all resources with stored amounts
        for resource in self.game_state.resources.values():
            if resource.amount > Decimal("0"):
                resource.purity = ResourceCalculator.calculate_purity_decay(
                    resource.purity,
                    delta_time
                )

        # Trigger reactivity update
        self.game_state.resources = dict(self.game_state.resources)

    def check_storage_capacity(self) -> None:
        """Check storage capacity and apply overflow penalties.

        When storage overflows, purity is damaged and excess resources are lost.
        """
        for emotion_type, resource in self.game_state.resources.items():
            if resource.is_overflowing:
                # Apply overflow penalty: -10% purity
                resource.purity = max(
                    Decimal("0"),
                    resource.purity - Decimal("10.0")
                )

                # Cap resources at storage capacity
                resource.amount = min(
                    resource.amount,
                    Decimal(str(resource.storage_capacity))
                )

        # Trigger reactivity update if any overflow occurred
        self.game_state.resources = dict(self.game_state.resources)

    def get_production_rate(self, emotion_type: str) -> Decimal:
        """Get the current production rate for an emotion type.

        Args:
            emotion_type: Name of the emotion

        Returns:
            Production rate per second (of what it produces)
        """
        emotion_type = emotion_type.lower()

        # Check if emotion exists and has producers
        if emotion_type not in self.game_state.resources:
            return Decimal("0")

        resource = self.game_state.resources[emotion_type]
        if resource.producer_count == 0:
            return Decimal("0")

        # Get emotion definition
        emotion = get_emotion(emotion_type)

        # Tier 0 doesn't produce
        if emotion.tier == 0 or not emotion.produces:
            return Decimal("0")

        # Get storage state for the target resource
        target_resource = self.game_state.get_resource(emotion.produces)
        storage_state = ResourceCalculator.get_storage_state(
            target_resource.storage_percentage
        )

        # Calculate production rate
        prestige_bonus = self.game_state.get_prestige_bonus()
        production_rate = ResourceCalculator.calculate_production(
            emotion.production_rate,
            resource.producer_count,
            self.game_state.global_production_multiplier,
            prestige_bonus,
            storage_state
        )

        return production_rate

    def get_all_production_rates(self) -> dict[str, Decimal]:
        """Get production rates for all emotion types.

        Returns:
            Dictionary mapping emotion_type -> production rate
        """
        rates = {}
        for emotion_type in self.game_state.resources.keys():
            rates[emotion_type] = self.get_production_rate(emotion_type)
        return rates

    def force_tick(self, duration: float) -> None:
        """Force a game tick for a specific duration (for testing).

        Args:
            duration: Duration in seconds to simulate
        """
        self.update(duration)

    def reset(self) -> None:
        """Reset the game loop state."""
        self.accumulated_time = 0.0
