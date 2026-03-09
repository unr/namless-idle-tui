"""Unit tests for GameLoop class."""

import pytest
from decimal import Decimal
from src.idle_game.engine.game_loop import GameLoop
from src.idle_game.models.game_state import GameState


class TestGameLoop:
    """Tests for GameLoop class."""

    def test_initialization(self, fresh_game_state):
        """Test GameLoop initializes correctly."""
        loop = GameLoop(fresh_game_state)

        assert loop.game_state == fresh_game_state
        assert loop.accumulated_time == 0.0
        assert loop.customer_generator is not None

    def test_update_increases_playtime(self, game_loop):
        """Test update increases total playtime."""
        initial_playtime = game_loop.game_state.total_playtime

        game_loop.update(10.0)

        assert game_loop.game_state.total_playtime == initial_playtime + 10.0

    def test_update_skipped_when_paused(self, game_loop):
        """Test update is skipped when game is paused."""
        game_loop.game_state.game_paused = True
        initial_playtime = game_loop.game_state.total_playtime

        game_loop.update(10.0)

        # Playtime shouldn't change when paused
        assert game_loop.game_state.total_playtime == initial_playtime

    def test_passive_generation_single_tier(self, mid_game_state):
        """Test passive generation with single tier."""
        loop = GameLoop(mid_game_state)

        initial_smiles = mid_game_state.get_resource("smiles").amount

        loop.update(10.0)  # 10 seconds

        final_smiles = mid_game_state.get_resource("smiles").amount

        # Should have produced some smiles
        assert final_smiles > initial_smiles

    def test_passive_generation_no_producers(self, fresh_game_state):
        """Test no passive generation without producers."""
        loop = GameLoop(fresh_game_state)

        initial_smiles = fresh_game_state.get_resource("smiles").amount

        loop.update(10.0)

        final_smiles = fresh_game_state.get_resource("smiles").amount

        # No change without producers
        assert final_smiles == initial_smiles

    def test_passive_generation_multi_tier(self, advanced_game_state):
        """Test passive generation across multiple tiers."""
        loop = GameLoop(advanced_game_state)

        initial_smiles = advanced_game_state.get_resource("smiles").amount
        initial_joy = advanced_game_state.get_resource("joy").amount

        loop.update(10.0)

        final_smiles = advanced_game_state.get_resource("smiles").amount
        final_joy = advanced_game_state.get_resource("joy").amount

        # Both should increase
        assert final_smiles > initial_smiles
        assert final_joy > initial_joy

    def test_purity_decay(self, mid_game_state):
        """Test purity decays over time."""
        loop = GameLoop(mid_game_state)

        initial_purity = mid_game_state.get_resource("joy").purity

        loop.update(120.0)  # 2 minutes

        final_purity = mid_game_state.get_resource("joy").purity

        # Purity should decrease
        assert final_purity < initial_purity

    def test_storage_overflow_penalty(self, fresh_game_state):
        """Test storage overflow applies penalty."""
        loop = GameLoop(fresh_game_state)

        # Set smiles to exceed capacity
        smiles = fresh_game_state.get_resource("smiles")
        smiles.amount = Decimal("150")
        smiles.storage_capacity = 100
        initial_purity = smiles.purity

        loop.check_storage_capacity()

        # Amount should be capped
        assert smiles.amount <= Decimal("100")
        # Purity should be reduced
        assert smiles.purity < initial_purity

    def test_tutorial_milestone_triggered(self, fresh_game_state):
        """Test tutorial customer triggers at milestone."""
        loop = GameLoop(fresh_game_state)

        # Set smiles to trigger first tutorial (10 smiles)
        fresh_game_state.get_resource("smiles").amount = Decimal("15")

        loop.check_tutorial_milestones()

        # Should have pending tutorial customer
        assert fresh_game_state.pending_tutorial_customer is not None

    def test_tutorial_milestone_not_triggered_twice(self, fresh_game_state):
        """Test tutorial doesn't trigger if already completed."""
        loop = GameLoop(fresh_game_state)

        fresh_game_state.get_resource("smiles").amount = Decimal("15")
        fresh_game_state.completed_tutorials = ["joy_seeker"]

        loop.check_tutorial_milestones()

        # Should NOT have pending tutorial customer
        assert fresh_game_state.pending_tutorial_customer is None

    def test_tutorial_milestone_not_triggered_if_pending(self, fresh_game_state):
        """Test tutorial doesn't trigger if one is already pending."""
        loop = GameLoop(fresh_game_state)

        fresh_game_state.get_resource("smiles").amount = Decimal("15")

        loop.check_tutorial_milestones()
        first_customer = fresh_game_state.pending_tutorial_customer

        loop.check_tutorial_milestones()
        second_customer = fresh_game_state.pending_tutorial_customer

        # Should be the same customer (not triggered again)
        assert first_customer == second_customer

    def test_get_production_rate_no_producers(self, fresh_game_state):
        """Test production rate is 0 without producers."""
        loop = GameLoop(fresh_game_state)

        rate = loop.get_production_rate("joy")

        assert rate == Decimal("0")

    def test_get_production_rate_with_producers(self, mid_game_state):
        """Test production rate calculation with producers."""
        loop = GameLoop(mid_game_state)

        rate = loop.get_production_rate("joy")

        # Should have positive production rate
        assert rate > Decimal("0")

    def test_get_all_production_rates(self, mid_game_state):
        """Test getting all production rates."""
        loop = GameLoop(mid_game_state)

        rates = loop.get_all_production_rates()

        assert isinstance(rates, dict)
        assert "smiles" in rates
        assert "joy" in rates

    def test_force_tick(self, mid_game_state):
        """Test force_tick simulates game update."""
        loop = GameLoop(mid_game_state)

        initial_smiles = mid_game_state.get_resource("smiles").amount

        loop.force_tick(5.0)

        final_smiles = mid_game_state.get_resource("smiles").amount

        # Should have produced resources
        assert final_smiles > initial_smiles

    def test_reset(self, game_loop):
        """Test reset clears accumulated time."""
        game_loop.accumulated_time = 100.0

        game_loop.reset()

        assert game_loop.accumulated_time == 0.0
