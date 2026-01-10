"""Pytest configuration and fixtures for Emotion Merchant tests."""

import pytest
from decimal import Decimal
from src.idle_game.models.game_state import GameState
from src.idle_game.engine.game_loop import GameLoop


@pytest.fixture
def fresh_game_state():
    """Provide a fresh GameState instance."""
    return GameState()


@pytest.fixture
def mid_game_state():
    """Provide a game state with Joy unlocked and some resources."""
    state = GameState()
    state.unlock_emotion("joy")
    state.get_resource("smiles").amount = Decimal("50")  # Keep below 95% capacity to allow production
    state.get_resource("joy").amount = Decimal("10")
    state.get_resource("joy").producer_count = 1
    return state


@pytest.fixture
def advanced_game_state():
    """Provide a game state with multiple emotions unlocked."""
    state = GameState()
    state.unlock_emotion("joy")
    state.unlock_emotion("love")
    state.unlock_emotion("nostalgia")

    # Increase storage capacity before setting amounts to avoid production stoppage
    state.get_resource("smiles").storage_capacity = 10000
    state.get_resource("smiles").amount = Decimal("5000")
    state.get_resource("joy").storage_capacity = 1000
    state.get_resource("joy").amount = Decimal("500")
    state.get_resource("joy").producer_count = 5
    state.get_resource("love").storage_capacity = 200
    state.get_resource("love").amount = Decimal("50")
    state.get_resource("love").producer_count = 2

    state.total_clicks = 100
    state.customers_served = 5

    return state


@pytest.fixture
def prestige_ready_state():
    """Provide a game state ready for prestige."""
    state = GameState()
    state.customers_served = 15
    state.recipes_discovered = {"recipe1", "recipe2", "recipe3", "recipe4"}
    state.ethical_score = Decimal("75.0")
    return state


@pytest.fixture
def game_loop(fresh_game_state):
    """Provide a GameLoop instance with fresh game state."""
    return GameLoop(fresh_game_state)
