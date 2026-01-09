"""Game module for Emotion Merchant.

This module contains the core game engine including resource definitions,
state management, production systems, and game logic.
"""

from .resources import (
    EmotionTier,
    PrimaryEmotion,
    EmotionConfig,
    EMOTION_CONFIGS,
    get_emotion_config,
    get_next_tier,
    get_previous_tier,
)

from .state import (
    ResourceState,
    GameState,
    GameStateManager,
)

from .production import (
    StorageUpgrade,
    StorageUpgradeConfig,
    STORAGE_UPGRADES,
    Producer,
    ProductionEngine,
)

__all__ = [
    # Resources
    "EmotionTier",
    "PrimaryEmotion",
    "EmotionConfig",
    "EMOTION_CONFIGS",
    "get_emotion_config",
    "get_next_tier",
    "get_previous_tier",
    # State
    "ResourceState",
    "GameState",
    "GameStateManager",
    # Production
    "StorageUpgrade",
    "StorageUpgradeConfig",
    "STORAGE_UPGRADES",
    "Producer",
    "ProductionEngine",
]
