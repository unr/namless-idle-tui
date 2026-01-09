"""Comprehensive tests for the Emotion Merchant game engine.

Tests the core resource and state management systems including:
- Resource initialization and unlocking
- Click harvesting and resource production
- Storage management and capacity limits
- Observer pattern for UI updates
- Serialization and deserialization
- Prestige system
- Customer serving and ethical choices
"""

import pytest
from decimal import Decimal
from src.emotion_merchant import (
    EmotionTier,
    PrimaryEmotion,
    EMOTION_CONFIGS,
    get_emotion_config,
    get_next_tier,
    get_previous_tier,
    GameStateManager,
    ResourceState,
)


class TestEmotionConfigs:
    """Test emotion tier configurations."""

    def test_all_tiers_configured(self):
        """Verify all 10 emotion tiers are configured."""
        assert len(EMOTION_CONFIGS) == 10
        for tier in EmotionTier:
            assert tier in EMOTION_CONFIGS

    def test_smiles_config(self):
        """Test Smiles (base tier) configuration."""
        config = EMOTION_CONFIGS[EmotionTier.SMILES]
        assert config.name == "Smiles"
        assert config.symbol == "☺"
        assert config.base_cost == Decimal("0")
        assert config.production_rate == Decimal("1")
        assert config.base_storage == 100
        assert config.max_storage == 1000000

    def test_singularity_config(self):
        """Test Singularity (top tier) configuration."""
        config = EMOTION_CONFIGS[EmotionTier.SINGULARITY]
        assert config.name == "Singularity"
        assert config.symbol == "∞"
        assert config.base_cost == Decimal("10000000")
        assert config.production_rate == Decimal("10000")
        assert config.base_storage == 1
        assert config.max_storage == 5

    def test_get_emotion_config(self):
        """Test get_emotion_config helper function."""
        config = get_emotion_config(EmotionTier.JOY)
        assert config.name == "Joy"
        assert config.tier == EmotionTier.JOY

    def test_tier_navigation(self):
        """Test get_next_tier and get_previous_tier."""
        assert get_next_tier(EmotionTier.SMILES) == EmotionTier.JOY
        assert get_next_tier(EmotionTier.SINGULARITY) is None
        assert get_previous_tier(EmotionTier.JOY) == EmotionTier.SMILES
        assert get_previous_tier(EmotionTier.SMILES) is None


class TestResourceState:
    """Test ResourceState dataclass."""

    def test_initialization(self):
        """Test default resource state initialization."""
        resource = ResourceState()
        assert resource.amount == Decimal("0")
        assert resource.storage_capacity == 100
        assert resource.purity == 100.0
        assert resource.producers == 0
        assert resource.unlocked is False

    def test_storage_percent(self):
        """Test storage percentage calculation."""
        resource = ResourceState(amount=Decimal("50"), storage_capacity=100)
        assert resource.storage_percent == 50.0

    def test_is_full(self):
        """Test full storage detection."""
        resource = ResourceState(amount=Decimal("100"), storage_capacity=100)
        assert resource.is_full is True

    def test_is_empty(self):
        """Test empty storage detection."""
        resource = ResourceState()
        assert resource.is_empty is True

    def test_can_afford(self):
        """Test affordability check."""
        resource = ResourceState(amount=Decimal("50"))
        assert resource.can_afford(Decimal("30")) is True
        assert resource.can_afford(Decimal("60")) is False


class TestGameStateManager:
    """Test GameStateManager functionality."""

    def test_initialization(self):
        """Test game state manager initialization."""
        manager = GameStateManager()
        assert manager.state is not None
        assert len(manager.state.resources) == 10
        assert manager.state.resources[EmotionTier.SMILES].unlocked is True
        assert manager.state.resources[EmotionTier.JOY].unlocked is False

    def test_click_harvest(self):
        """Test manual click harvesting."""
        manager = GameStateManager()
        initial = manager.state.resources[EmotionTier.SMILES].amount

        harvested = manager.click_harvest()
        assert harvested == Decimal("5")  # Default click_power
        assert manager.state.total_clicks == 1
        assert manager.state.resources[EmotionTier.SMILES].amount == initial + Decimal("5")

    def test_add_resource_with_storage_limit(self):
        """Test adding resources respects storage limits."""
        manager = GameStateManager()
        resource = manager.state.resources[EmotionTier.SMILES]

        # Add within limit
        added = manager.add_resource(EmotionTier.SMILES, Decimal("50"))
        assert added == Decimal("50")
        assert resource.amount == Decimal("50")

        # Try to add more than available space
        added = manager.add_resource(EmotionTier.SMILES, Decimal("100"))
        assert added == Decimal("50")  # Only 50 space left
        assert resource.amount == Decimal("100")  # Full storage

    def test_spend_resource(self):
        """Test resource spending."""
        manager = GameStateManager()
        manager.add_resource(EmotionTier.SMILES, Decimal("100"))

        # Successful spend
        success = manager.spend_resource(EmotionTier.SMILES, Decimal("30"))
        assert success is True
        assert manager.state.resources[EmotionTier.SMILES].amount == Decimal("70")

        # Failed spend (insufficient resources)
        success = manager.spend_resource(EmotionTier.SMILES, Decimal("100"))
        assert success is False
        assert manager.state.resources[EmotionTier.SMILES].amount == Decimal("70")

    def test_can_afford(self):
        """Test affordability checking."""
        manager = GameStateManager()
        manager.add_resource(EmotionTier.SMILES, Decimal("50"))

        assert manager.can_afford(EmotionTier.SMILES, Decimal("30")) is True
        assert manager.can_afford(EmotionTier.SMILES, Decimal("60")) is False
        assert manager.can_afford(EmotionTier.JOY, Decimal("10")) is False  # Not unlocked

    def test_unlock_resource(self):
        """Test unlocking resources."""
        manager = GameStateManager()
        assert manager.state.resources[EmotionTier.JOY].unlocked is False

        manager.unlock_resource(EmotionTier.JOY)
        assert manager.state.resources[EmotionTier.JOY].unlocked is True

    def test_unlock_primary_emotion(self):
        """Test unlocking primary emotions."""
        manager = GameStateManager()
        assert manager.state.primary_emotions[PrimaryEmotion.JOY] is False

        manager.unlock_primary_emotion(PrimaryEmotion.JOY)
        assert manager.state.primary_emotions[PrimaryEmotion.JOY] is True

    def test_add_producer(self):
        """Test adding producers."""
        manager = GameStateManager()
        resource = manager.state.resources[EmotionTier.SMILES]

        manager.add_producer(EmotionTier.SMILES, 1)
        assert resource.producers == 1

        manager.add_producer(EmotionTier.SMILES, 5)
        assert resource.producers == 6

    def test_upgrade_storage(self):
        """Test storage capacity upgrades."""
        manager = GameStateManager()
        resource = manager.state.resources[EmotionTier.SMILES]
        initial_capacity = resource.storage_capacity

        manager.upgrade_storage(EmotionTier.SMILES, 500)
        assert resource.storage_capacity == 500

        # Cannot exceed max storage
        manager.upgrade_storage(EmotionTier.SMILES, 2000000)
        max_storage = EMOTION_CONFIGS[EmotionTier.SMILES].max_storage
        assert resource.storage_capacity == max_storage

    def test_serve_customer(self):
        """Test customer serving and ethical scoring."""
        manager = GameStateManager()

        # Ethical choice
        manager.serve_customer(ethical_choice=True)
        assert manager.state.customers_served == 1
        assert manager.state.ethical_score == 51.0

        # Unethical choice
        manager.serve_customer(ethical_choice=False)
        assert manager.state.customers_served == 2
        assert manager.state.ethical_score == 50.0

        # Neutral choice
        initial_score = manager.state.ethical_score
        manager.serve_customer(ethical_choice=None)
        assert manager.state.customers_served == 3
        assert manager.state.ethical_score == initial_score

    def test_update_reputation(self):
        """Test reputation updates."""
        manager = GameStateManager()
        initial = manager.state.reputation

        manager.update_reputation(1.0)
        assert manager.state.reputation == initial + 1.0

        # Cannot exceed 5.0
        manager.update_reputation(10.0)
        assert manager.state.reputation == 5.0

        # Cannot go below 0.0
        manager.update_reputation(-10.0)
        assert manager.state.reputation == 0.0

    def test_prestige(self):
        """Test prestige system."""
        manager = GameStateManager()
        manager.add_resource(EmotionTier.SMILES, Decimal("100"))
        manager.state.customers_served = 10
        manager.state.total_clicks = 50
        manager.state.play_time_seconds = 100.0

        manager.prestige(Decimal("25"))

        # Should reset game state but keep prestige progress
        assert manager.state.prestige_count == 1
        assert manager.state.emotional_depth == Decimal("25")
        assert manager.state.resources[EmotionTier.SMILES].amount == Decimal("0")
        assert manager.state.customers_served == 0
        assert manager.state.play_time_seconds == 100.0  # Play time persists

    def test_observer_pattern(self):
        """Test state change notifications."""
        manager = GameStateManager()
        events = []

        def observer(event, data):
            events.append((event, data))

        manager.subscribe(observer)

        # Perform various actions
        manager.click_harvest()
        manager.unlock_resource(EmotionTier.JOY)
        manager.spend_resource(EmotionTier.SMILES, Decimal("1"))

        # Should have received events
        assert len(events) >= 3
        event_types = [e[0] for e in events]
        assert "click" in event_types
        assert "resource_unlocked" in event_types
        assert "resource_changed" in event_types

    def test_serialization(self):
        """Test state serialization to dict."""
        manager = GameStateManager()
        manager.add_resource(EmotionTier.SMILES, Decimal("42"))
        manager.state.customers_served = 5
        manager.state.tutorial_complete = True

        data = manager.to_dict()

        assert data["resources"]["SMILES"]["amount"] == "42"
        assert data["customers_served"] == 5
        assert data["tutorial_complete"] is True

    def test_deserialization(self):
        """Test state loading from dict."""
        manager = GameStateManager()
        manager.add_resource(EmotionTier.SMILES, Decimal("100"))
        manager.state.customers_served = 10
        manager.unlock_resource(EmotionTier.JOY)

        # Serialize
        data = manager.to_dict()

        # Deserialize into new manager
        loaded_manager = GameStateManager.from_dict(data)

        assert loaded_manager.state.resources[EmotionTier.SMILES].amount == Decimal("100")
        assert loaded_manager.state.customers_served == 10
        assert loaded_manager.state.resources[EmotionTier.JOY].unlocked is True

    def test_update_play_time(self):
        """Test play time tracking."""
        manager = GameStateManager()
        initial_time = manager.state.play_time_seconds

        manager.update_play_time(10.5)
        assert manager.state.play_time_seconds == initial_time + 10.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
