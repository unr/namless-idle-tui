import aiosqlite
from pathlib import Path
from datetime import datetime
from typing import Optional
from .models import GameState, GameNumber
from decimal import Decimal


class GameDatabase:
    def __init__(self, db_path: str = "data/game.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(exist_ok=True)

    async def initialize(self):
        """Create tables if they don't exist"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS game_state (
                    id INTEGER PRIMARY KEY DEFAULT 1,
                    counter TEXT NOT NULL,
                    click_power TEXT NOT NULL,
                    auto_increment TEXT NOT NULL,
                    last_update TEXT NOT NULL,
                    last_save TEXT NOT NULL,
                    CHECK (id = 1)
                )
            """
            )
            await db.commit()

    async def save_state(self, state: GameState):
        """Save current game state"""
        async with aiosqlite.connect(self.db_path) as db:
            state.last_save = datetime.now()
            await db.execute(
                """
                INSERT OR REPLACE INTO game_state 
                (id, counter, click_power, auto_increment, last_update, last_save)
                VALUES (1, ?, ?, ?, ?, ?)
            """,
                (
                    str(state.counter.value),
                    str(state.click_power.value),
                    str(state.auto_increment.value),
                    state.last_update.isoformat(),
                    state.last_save.isoformat(),
                ),
            )
            await db.commit()

    async def load_state(self) -> Optional[GameState]:
        """Load saved game state"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT counter, click_power, auto_increment, last_update, last_save "
                "FROM game_state WHERE id = 1"
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return GameState(
                        counter=GameNumber(Decimal(row[0])),
                        click_power=GameNumber(Decimal(row[1])),
                        auto_increment=GameNumber(Decimal(row[2])),
                        last_update=datetime.fromisoformat(row[3]),
                        last_save=datetime.fromisoformat(row[4]),
                    )
        return None
