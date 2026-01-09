"""Tests for game state management."""

from decimal import Decimal
from src.emotion_merchant.game.state import GameStateManager, ResourceState
from src.emotion_merchant.game.resources import EmotionTier, PrimaryEmotion


class TestGameState:
    """Test suite for GameState functionality."""

    def test_initial_state(self):
        """Test that initial game state is set up correctly."""
        manager = GameStateManager()
        assert manager.state.resources[EmotionTier.SMILES].unlocked
        assert not manager.state.resources[EmotionTier.JOY].unlocked

    def test_add_resource(self):
        """Test adding resources to unlocked tiers."""
        manager = GameStateManager()
        added = manager.add_resource(EmotionTier.SMILES, Decimal("10"))
        assert added == Decimal("10")
        assert manager.state.resources[EmotionTier.SMILES].amount == Decimal("10")

    def test_storage_limit(self):
        """Test that storage limits are respected."""
        manager = GameStateManager()
        manager.state.resources[EmotionTier.SMILES].storage_capacity = 50
        added = manager.add_resource(EmotionTier.SMILES, Decimal("100"))
        assert added == Decimal("50")

    def test_click_harvest(self):
        """Test manual click harvesting."""
        manager = GameStateManager()
        harvested = manager.click_harvest()
        assert harvested == Decimal("5")
        assert manager.state.total_clicks == 1

    def test_unlock_resource(self):
        """Test unlocking new resource tiers."""
        manager = GameStateManager()
        manager.unlock_resource(EmotionTier.JOY)
        assert manager.state.resources[EmotionTier.JOY].unlocked

    def test_spend_resource_success(self):
        """Test successful resource spending."""
        manager = GameStateManager()
        manager.add_resource(EmotionTier.SMILES, Decimal("20"))
        success = manager.spend_resource(EmotionTier.SMILES, Decimal("10"))
        assert success
        assert manager.state.resources[EmotionTier.SMILES].amount == Decimal("10")

    def test_spend_resource_insufficient(self):
        """Test spending when insufficient resources."""
        manager = GameStateManager()
        manager.add_resource(EmotionTier.SMILES, Decimal("5"))
        success = manager.spend_resource(EmotionTier.SMILES, Decimal("10"))
        assert not success
        assert manager.state.resources[EmotionTier.SMILES].amount == Decimal("5")

    def test_unlock_primary_emotion(self):
        """Test unlocking primary emotions."""
        manager = GameStateManager()
        manager.unlock_primary_emotion(PrimaryEmotion.JOY)
        assert manager.state.primary_emotions[PrimaryEmotion.JOY]

    def test_serve_customer_ethical(self):
        """Test serving customer with ethical choice."""
        manager = GameStateManager()
        initial_score = manager.state.ethical_score
        manager.serve_customer(ethical_choice=True)
        assert manager.state.customers_served == 1
        assert manager.state.ethical_score > initial_score

    def test_serve_customer_unethical(self):
        """Test serving customer with unethical choice."""
        manager = GameStateManager()
        initial_score = manager.state.ethical_score
        manager.serve_customer(ethical_choice=False)
        assert manager.state.customers_served == 1
        assert manager.state.ethical_score < initial_score

    def test_update_reputation(self):
        """Test reputation updates."""
        manager = GameStateManager()
        manager.update_reputation(1.0)
        assert manager.state.reputation == 4.0
        manager.update_reputation(-2.0)
        assert manager.state.reputation == 2.0

    def test_reputation_bounds(self):
        """Test reputation stays within 0-5 bounds."""
        manager = GameStateManager()
        manager.update_reputation(10.0)
        assert manager.state.reputation == 5.0
        manager.update_reputation(-20.0)
        assert manager.state.reputation == 0.0

    def test_add_producer(self):
        """Test adding producers to a resource."""
        manager = GameStateManager()
        manager.add_producer(EmotionTier.SMILES, 5)
        assert manager.state.resources[EmotionTier.SMILES].producers == 5

    def test_upgrade_storage(self):
        """Test storage capacity upgrades."""
        manager = GameStateManager()
        manager.upgrade_storage(EmotionTier.SMILES, 200)
        assert manager.state.resources[EmotionTier.SMILES].storage_capacity == 200


class TestResourceState:
    """Test suite for ResourceState functionality."""

    def test_resource_state_creation(self):
        """Test creating a resource state."""
        resource = ResourceState()
        assert resource.amount == Decimal("0")
        assert resource.storage_capacity == 100
        assert resource.purity == 100.0
        assert resource.producers == 0
        assert not resource.unlocked

    def test_storage_percent(self):
        """Test storage percentage calculation."""
        resource = ResourceState(storage_capacity=100)
        resource.amount = Decimal("50")
        assert resource.storage_percent == 50.0

    def test_is_full(self):
        """Test storage full detection."""
        resource = ResourceState(storage_capacity=100)
        resource.amount = Decimal("100")
        assert resource.is_full

    def test_is_empty(self):
        """Test storage empty detection."""
        resource = ResourceState()
        assert resource.is_empty

    def test_can_afford(self):
        """Test affordability checking."""
        resource = ResourceState()
        resource.amount = Decimal("50")
        assert resource.can_afford(Decimal("25"))
        assert not resource.can_afford(Decimal("100"))


class TestStateObserver:
    """Test suite for state change observation."""

    def test_subscribe_to_changes(self):
        """Test subscribing to state changes."""
        manager = GameStateManager()
        events = []

        def callback(event, data):
            events.append((event, data))

        manager.subscribe(callback)
        manager.add_resource(EmotionTier.SMILES, Decimal("10"))

        assert len(events) == 1
        assert events[0][0] == "resource_changed"

    def test_multiple_subscribers(self):
        """Test multiple subscribers receive notifications."""
        manager = GameStateManager()
        events1 = []
        events2 = []

        def callback1(event, data):
            events1.append(event)

        def callback2(event, data):
            events2.append(event)

        manager.subscribe(callback1)
        manager.subscribe(callback2)
        manager.unlock_resource(EmotionTier.JOY)

        assert len(events1) == 1
        assert len(events2) == 1
        assert events1[0] == "resource_unlocked"
        assert events2[0] == "resource_unlocked"
