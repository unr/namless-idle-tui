"""Resource definitions for the Emotion Merchant game.

This module defines the emotion resource hierarchy, from basic Smiles
to transcendent Singularity. Each emotion tier has unique characteristics
including production rates, storage capacities, and unlock costs.
"""

from enum import Enum
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional


class EmotionTier(Enum):
    """Emotion tiers from basic to transcendent.

    Each tier represents a progressively more refined and rare emotion,
    starting from simple Smiles (the base currency) and culminating in
    the ultimate Singularity emotion.
    """
    SMILES = 0          # Base currency (click-generated)
    JOY = 1             # First refined emotion
    LOVE = 2            # Deep connection
    NOSTALGIA = 3       # Bittersweet memories
    SERENITY = 4        # Inner peace
    EUPHORIA = 5        # Intense bliss
    COMPASSION = 6      # Universal empathy
    WISDOM = 7          # Transcendent understanding
    TRANSCENDENCE = 8   # Beyond mortal emotion
    SINGULARITY = 9     # The ultimate emotion


class PrimaryEmotion(Enum):
    """Primary emotions unlocked via tutorial customers.

    These basic emotional states are introduced through the game's
    narrative tutorial system and unlock special gameplay mechanics.
    """
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    DISGUST = "disgust"


@dataclass
class EmotionConfig:
    """Configuration for each emotion tier.

    Attributes:
        tier: The emotion tier level
        name: Display name of the emotion
        symbol: Unicode symbol for UI display
        base_cost: Cost in previous tier's currency to unlock first producer
        production_rate: Base production per second for this emotion
        base_storage: Starting storage capacity when unlocked
        max_storage: Maximum storage capacity after all upgrades
        color: Display color as hex code for UI theming
    """
    tier: EmotionTier
    name: str
    symbol: str
    base_cost: Decimal          # Cost to unlock first producer
    production_rate: Decimal    # Base production per second
    base_storage: int           # Starting storage capacity
    max_storage: int            # Maximum upgraded storage
    color: str                  # Display color (hex code)


# Define all emotion configurations based on game design doc
EMOTION_CONFIGS: Dict[EmotionTier, EmotionConfig] = {
    EmotionTier.SMILES: EmotionConfig(
        tier=EmotionTier.SMILES,
        name="Smiles",
        symbol="☺",
        base_cost=Decimal("0"),
        production_rate=Decimal("1"),
        base_storage=100,
        max_storage=1000000,
        color="#FFD700"
    ),
    EmotionTier.JOY: EmotionConfig(
        tier=EmotionTier.JOY,
        name="Joy",
        symbol="❤",
        base_cost=Decimal("10"),
        production_rate=Decimal("0.5"),
        base_storage=50,
        max_storage=10000,
        color="#FF6B6B"
    ),
    EmotionTier.LOVE: EmotionConfig(
        tier=EmotionTier.LOVE,
        name="Love",
        symbol="💕",
        base_cost=Decimal("100"),
        production_rate=Decimal("2"),
        base_storage=25,
        max_storage=5000,
        color="#FF1493"
    ),
    EmotionTier.NOSTALGIA: EmotionConfig(
        tier=EmotionTier.NOSTALGIA,
        name="Nostalgia",
        symbol="❖",
        base_cost=Decimal("500"),
        production_rate=Decimal("5"),
        base_storage=10,
        max_storage=1000,
        color="#9370DB"
    ),
    EmotionTier.SERENITY: EmotionConfig(
        tier=EmotionTier.SERENITY,
        name="Serenity",
        symbol="◉",
        base_cost=Decimal("2500"),
        production_rate=Decimal("10"),
        base_storage=5,
        max_storage=500,
        color="#87CEEB"
    ),
    EmotionTier.EUPHORIA: EmotionConfig(
        tier=EmotionTier.EUPHORIA,
        name="Euphoria",
        symbol="✧",
        base_cost=Decimal("12500"),
        production_rate=Decimal("50"),
        base_storage=3,
        max_storage=100,
        color="#FFD700"
    ),
    EmotionTier.COMPASSION: EmotionConfig(
        tier=EmotionTier.COMPASSION,
        name="Compassion",
        symbol="❀",
        base_cost=Decimal("62500"),
        production_rate=Decimal("100"),
        base_storage=2,
        max_storage=50,
        color="#90EE90"
    ),
    EmotionTier.WISDOM: EmotionConfig(
        tier=EmotionTier.WISDOM,
        name="Wisdom",
        symbol="◈",
        base_cost=Decimal("312500"),
        production_rate=Decimal("500"),
        base_storage=1,
        max_storage=25,
        color="#DDA0DD"
    ),
    EmotionTier.TRANSCENDENCE: EmotionConfig(
        tier=EmotionTier.TRANSCENDENCE,
        name="Transcendence",
        symbol="✵",
        base_cost=Decimal("1500000"),
        production_rate=Decimal("1000"),
        base_storage=1,
        max_storage=10,
        color="#F0E68C"
    ),
    EmotionTier.SINGULARITY: EmotionConfig(
        tier=EmotionTier.SINGULARITY,
        name="Singularity",
        symbol="∞",
        base_cost=Decimal("10000000"),
        production_rate=Decimal("10000"),
        base_storage=1,
        max_storage=5,
        color="#FFFFFF"
    ),
}


def get_emotion_config(tier: EmotionTier) -> EmotionConfig:
    """Get the configuration for a specific emotion tier.

    Args:
        tier: The emotion tier to retrieve configuration for

    Returns:
        The EmotionConfig for the specified tier

    Raises:
        KeyError: If the tier is not found in EMOTION_CONFIGS
    """
    return EMOTION_CONFIGS[tier]


def get_next_tier(tier: EmotionTier) -> Optional[EmotionTier]:
    """Get the next emotion tier after the given tier.

    Args:
        tier: The current emotion tier

    Returns:
        The next EmotionTier, or None if already at maximum tier
    """
    if tier.value >= EmotionTier.SINGULARITY.value:
        return None

    for emotion_tier in EmotionTier:
        if emotion_tier.value == tier.value + 1:
            return emotion_tier

    return None


def get_previous_tier(tier: EmotionTier) -> Optional[EmotionTier]:
    """Get the previous emotion tier before the given tier.

    Args:
        tier: The current emotion tier

    Returns:
        The previous EmotionTier, or None if already at minimum tier
    """
    if tier.value <= EmotionTier.SMILES.value:
        return None

    for emotion_tier in EmotionTier:
        if emotion_tier.value == tier.value - 1:
            return emotion_tier

    return None
