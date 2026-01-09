"""Emotion Merchant - An idle game TUI about managing emotions.

This package contains the complete game implementation including:
- Core game engine and state management
- TUI widgets and display components
- Resource and progression systems
- Customer interactions and narrative elements
"""

from .game import (
    EmotionTier,
    PrimaryEmotion,
    EmotionConfig,
    EMOTION_CONFIGS,
    get_emotion_config,
    get_next_tier,
    get_previous_tier,
    ResourceState,
    GameState,
    GameStateManager,
)

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
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
]
