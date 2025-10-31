import pytest
import asyncio
from pathlib import Path
from decimal import Decimal
from src.idle_game.database import GameDatabase
from src.idle_game.models import GameState, GameNumber


@pytest.fixture
async def test_db():
    """Create test database"""
    db_path = "data/test_game.db"
    db = GameDatabase(db_path)
    await db.initialize()
    yield db
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_save_and_load(test_db):
    # Create and save state
    state = GameState(
        counter=GameNumber(Decimal("12345")),
        click_power=GameNumber(Decimal("50")),
        auto_increment=GameNumber(Decimal("10")),
    )
    await test_db.save_state(state)

    # Load state
    loaded = await test_db.load_state()
    assert loaded is not None
    assert loaded.counter.value == Decimal("12345")
    assert loaded.click_power.value == Decimal("50")
    assert loaded.auto_increment.value == Decimal("10")


@pytest.mark.asyncio
async def test_empty_database(test_db):
    loaded = await test_db.load_state()
    assert loaded is None
