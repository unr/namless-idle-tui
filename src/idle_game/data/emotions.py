"""
Emotion resource definitions for the Emotion Merchant idle game.

This module defines all 10 tiers of emotions with their properties including
base costs, production rates, storage capacities, and visual symbols.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class EmotionDefinition:
    """Defines the static properties of an emotion type.

    Attributes:
        name: The display name of the emotion (e.g., "Smiles", "Joy")
        tier: The tier level (0-9), where 0 is the base currency
        symbol: Unicode symbol for display in the UI
        base_cost: The cost to purchase the first producer for this emotion.
                   For tier 0 (Smiles), this represents clicks per harvest.
        production_rate: Base production rate per second for each producer
        min_storage: Starting storage capacity
        max_storage: Maximum storage capacity after all upgrades (None = unlimited)
        produces: The emotion type this produces (None for tier 0)
    """
    name: str
    tier: int
    symbol: str
    base_cost: Decimal
    production_rate: Decimal
    min_storage: int
    max_storage: Optional[int]
    produces: Optional[str] = None


# Define all 10 emotion tiers based on docs/game-design/resources.md
EMOTIONS = {
    "smiles": EmotionDefinition(
        name="Smiles",
        tier=0,
        symbol="☺",
        base_cost=Decimal("5"),  # Clicks per harvest
        production_rate=Decimal("1.0"),  # Base production: 1/sec
        min_storage=100,
        max_storage=None,  # Unlimited in late game
        produces=None  # Base currency - produced by clicking
    ),

    "joy": EmotionDefinition(
        name="Joy",
        tier=1,
        symbol="❤",
        base_cost=Decimal("10"),  # Cost in Smiles
        production_rate=Decimal("0.5"),  # Produces 0.5 Smiles/sec
        min_storage=50,
        max_storage=10000,
        produces="smiles"
    ),

    "love": EmotionDefinition(
        name="Love",
        tier=2,
        symbol="💕",
        base_cost=Decimal("100"),  # Cost in Joy
        production_rate=Decimal("2.0"),  # Produces 2 Joy/sec
        min_storage=25,
        max_storage=5000,
        produces="joy"
    ),

    "nostalgia": EmotionDefinition(
        name="Nostalgia",
        tier=3,
        symbol="❖",
        base_cost=Decimal("500"),  # Cost in Love
        production_rate=Decimal("5.0"),  # Produces 5 Love/sec
        min_storage=10,
        max_storage=1000,
        produces="love"
    ),

    "serenity": EmotionDefinition(
        name="Serenity",
        tier=4,
        symbol="◉",
        base_cost=Decimal("2500"),  # Cost in Nostalgia
        production_rate=Decimal("10.0"),  # Produces 10 Nostalgia/sec
        min_storage=5,
        max_storage=500,
        produces="nostalgia"
    ),

    "euphoria": EmotionDefinition(
        name="Euphoria",
        tier=5,
        symbol="✧",
        base_cost=Decimal("12500"),  # Cost in Serenity
        production_rate=Decimal("50.0"),  # Produces 50 Serenity/sec
        min_storage=3,
        max_storage=100,
        produces="serenity"
    ),

    "compassion": EmotionDefinition(
        name="Compassion",
        tier=6,
        symbol="❀",
        base_cost=Decimal("62500"),  # Cost in Euphoria
        production_rate=Decimal("100.0"),  # Produces 100 Euphoria/sec
        min_storage=2,
        max_storage=50,
        produces="euphoria"
    ),

    "wisdom": EmotionDefinition(
        name="Wisdom",
        tier=7,
        symbol="◈",
        base_cost=Decimal("312500"),  # Cost in Compassion
        production_rate=Decimal("500.0"),  # Produces 500 Compassion/sec
        min_storage=1,
        max_storage=25,
        produces="compassion"
    ),

    "transcendence": EmotionDefinition(
        name="Transcendence",
        tier=8,
        symbol="✵",
        base_cost=Decimal("1500000"),  # Cost in Wisdom
        production_rate=Decimal("1000.0"),  # Produces 1K Wisdom/sec
        min_storage=1,
        max_storage=10,
        produces="wisdom"
    ),

    "singularity": EmotionDefinition(
        name="Singularity",
        tier=9,
        symbol="∞",
        base_cost=Decimal("10000000"),  # Cost in Transcendence
        production_rate=Decimal("10000.0"),  # Produces 10K Transcendence/sec
        min_storage=1,
        max_storage=5,
        produces="transcendence"
    ),
}


# Convenience function to get emotion by name
def get_emotion(name: str) -> EmotionDefinition:
    """Get an emotion definition by name (case-insensitive).

    Args:
        name: The name of the emotion (e.g., "smiles", "joy")

    Returns:
        The EmotionDefinition for the requested emotion

    Raises:
        KeyError: If the emotion name is not found
    """
    return EMOTIONS[name.lower()]


# List of all emotion names in tier order
EMOTION_TIERS = [
    "smiles", "joy", "love", "nostalgia", "serenity",
    "euphoria", "compassion", "wisdom", "transcendence", "singularity"
]
