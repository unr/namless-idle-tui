# Textual TUI Implementation Plan (Python)

## Project Overview
Build an incremental idle game using Textual (Python) that runs natively in terminal and deploys to web via textual-web.

## Core Requirements
- Load game with a counter starting at 0
- Counter increments over time (idle mechanic)  
- Persist state between sessions
- Calculate offline progression when returning

## Architecture

```
Terminal Mode:          Web Mode:
Python → Textual       Python → Textual → textual-web → WebSocket → Browser
        ↓                      ↓
    SQLite/JSON            SQLite/JSON
```

## Project Structure

```
idle-game-textual/
├── src/
│   ├── idle_game/
│   │   ├── __init__.py
│   │   ├── app.py           # Main Textual application
│   │   ├── game_state.py    # Game logic and state
│   │   ├── numbers.py       # Big number handling
│   │   ├── persistence.py   # Save/load system
│   │   ├── widgets/         # Custom UI components
│   │   │   ├── __init__.py
│   │   │   ├── counter.py
│   │   │   ├── upgrades.py
│   │   │   └── stats.py
│   │   └── styles/          # CSS-like styling
│   │       └── main.tcss
├── tests/
│   ├── test_game_state.py
│   ├── test_numbers.py
│   └── test_persistence.py
├── web/
│   ├── index.html           # Web wrapper
│   └── config.json          # textual-web config
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Phase 1: Core Implementation (Days 1-3)

### 1.1 Project Setup

```toml
# pyproject.toml
[tool.poetry]
name = "idle-game-textual"
version = "0.1.0"
description = "An incremental idle game built with Textual"

[tool.poetry.dependencies]
python = "^3.11"
textual = "^0.47.0"
textual-web = "^0.6.0"
decimal = "^1.3.0"
asyncio = "^3.4.3"
aiosqlite = "^0.19.0"
pydantic = "^2.5.0"
python-dateutil = "^2.8.2"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
black = "^23.0.0"
mypy = "^1.7.0"
ruff = "^0.1.0"

[tool.poetry.scripts]
idle-game = "idle_game.app:main"
```

### 1.2 Big Number Implementation

```python
# src/idle_game/numbers.py
from decimal import Decimal, getcontext
from typing import Optional, Tuple
import math
from dataclasses import dataclass
import json

# Set precision for Decimal operations
getcontext().prec = 50

@dataclass
class GameNumber:
    """Handles large numbers in scientific notation for idle games."""
    
    mantissa: Decimal  # 1.234
    exponent: int      # 10^6
    
    # Suffix list for formatting
    SUFFIXES = [
        "", "K", "M", "B", "T", "Qa", "Qi", "Sx", "Sp", "Oc", "No", "Dc",
        "Ud", "Dd", "Td", "Qad", "Qid", "Sxd", "Spd", "Od", "Nd", "Vg",
        "Uvg", "Dvg", "Tvg", "Qavg", "Qivg", "Sxvg", "Spvg", "Ovg", "Nvg", "Tg"
    ]
    
    def __init__(self, value: float | Decimal | str = 0):
        """Initialize from various number types."""
        if isinstance(value, str):
            # Parse scientific notation
            if 'e' in value.lower():
                parts = value.lower().split('e')
                self.mantissa = Decimal(parts[0])
                self.exponent = int(parts[1])
            else:
                self._from_decimal(Decimal(value))
        elif isinstance(value, Decimal):
            self._from_decimal(value)
        else:
            self._from_float(float(value))
        
        self._normalize()
    
    def _from_float(self, value: float):
        """Convert from float to mantissa/exponent."""
        if value == 0:
            self.mantissa = Decimal(0)
            self.exponent = 0
        else:
            exp = math.floor(math.log10(abs(value)))
            self.mantissa = Decimal(str(value / (10 ** exp)))
            self.exponent = exp
    
    def _from_decimal(self, value: Decimal):
        """Convert from Decimal to mantissa/exponent."""
        if value == 0:
            self.mantissa = Decimal(0)
            self.exponent = 0
        else:
            # Convert to string and parse
            str_val = str(value)
            if 'E' in str_val:
                parts = str_val.split('E')
                self.mantissa = Decimal(parts[0])
                self.exponent = int(parts[1])
            else:
                # Calculate exponent manually
                abs_val = abs(value)
                if abs_val >= 10:
                    exp = 0
                    temp = abs_val
                    while temp >= 10:
                        temp /= 10
                        exp += 1
                    self.mantissa = value / (Decimal(10) ** exp)
                    self.exponent = exp
                elif abs_val < 1:
                    exp = 0
                    temp = abs_val
                    while temp < 1 and temp != 0:
                        temp *= 10
                        exp -= 1
                    self.mantissa = value / (Decimal(10) ** exp)
                    self.exponent = exp
                else:
                    self.mantissa = value
                    self.exponent = 0
    
    def _normalize(self):
        """Normalize mantissa to be between 1 and 10."""
        if self.mantissa == 0:
            self.exponent = 0
            return
        
        while abs(self.mantissa) >= 10:
            self.mantissa /= 10
            self.exponent += 1
        
        while abs(self.mantissa) < 1 and self.mantissa != 0:
            self.mantissa *= 10
            self.exponent -= 1
    
    def add(self, other: 'GameNumber') -> 'GameNumber':
        """Add two GameNumbers."""
        # If exponents differ by more than 15, smaller number is negligible
        exp_diff = abs(self.exponent - other.exponent)
        if exp_diff > 15:
            return self if self.exponent > other.exponent else other
        
        # Align exponents
        if self.exponent > other.exponent:
            aligned_other = other.mantissa * (Decimal(10) ** (other.exponent - self.exponent))
            result_mantissa = self.mantissa + aligned_other
            result_exponent = self.exponent
        else:
            aligned_self = self.mantissa * (Decimal(10) ** (self.exponent - other.exponent))
            result_mantissa = aligned_self + other.mantissa
            result_exponent = other.exponent
        
        result = GameNumber(0)
        result.mantissa = result_mantissa
        result.exponent = result_exponent
        result._normalize()
        return result
    
    def multiply(self, scalar: float | Decimal | 'GameNumber') -> 'GameNumber':
        """Multiply by a scalar or another GameNumber."""
        if isinstance(scalar, GameNumber):
            result = GameNumber(0)
            result.mantissa = self.mantissa * scalar.mantissa
            result.exponent = self.exponent + scalar.exponent
            result._normalize()
            return result
        else:
            result = GameNumber(0)
            result.mantissa = self.mantissa * Decimal(str(scalar))
            result.exponent = self.exponent
            result._normalize()
            return result
    
    def subtract(self, other: 'GameNumber') -> 'GameNumber':
        """Subtract another GameNumber."""
        neg_other = GameNumber(0)
        neg_other.mantissa = -other.mantissa
        neg_other.exponent = other.exponent
        return self.add(neg_other)
    
    def compare(self, other: 'GameNumber') -> int:
        """Compare two GameNumbers. Returns -1, 0, or 1."""
        if self.exponent != other.exponent:
            return 1 if self.exponent > other.exponent else -1
        
        if self.mantissa > other.mantissa:
            return 1
        elif self.mantissa < other.mantissa:
            return -1
        return 0
    
    def __gt__(self, other: 'GameNumber') -> bool:
        return self.compare(other) > 0
    
    def __ge__(self, other: 'GameNumber') -> bool:
        return self.compare(other) >= 0
    
    def __lt__(self, other: 'GameNumber') -> bool:
        return self.compare(other) < 0
    
    def __le__(self, other: 'GameNumber') -> bool:
        return self.compare(other) <= 0
    
    def __eq__(self, other: 'GameNumber') -> bool:
        return self.compare(other) == 0
    
    def format(self, precision: int = 2) -> str:
        """Format number for display with suffixes."""
        if self.mantissa == 0:
            return "0"
        
        # For small numbers, show exact value
        if -3 <= self.exponent <= 6:
            value = self.mantissa * (Decimal(10) ** self.exponent)
            if self.exponent <= 0:
                return f"{value:.{precision}f}"
            else:
                return f"{int(value):,}" if value == int(value) else f"{value:,.{precision}f}"
        
        # Use suffix notation
        suffix_index = self.exponent // 3
        if suffix_index < len(self.SUFFIXES):
            adjusted_mantissa = self.mantissa * (Decimal(10) ** (self.exponent % 3))
            return f"{adjusted_mantissa:.{precision}f}{self.SUFFIXES[suffix_index]}"
        
        # Fall back to scientific notation for very large numbers
        return f"{self.mantissa:.{precision}f}e{self.exponent}"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "mantissa": str(self.mantissa),
            "exponent": self.exponent
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GameNumber':
        """Create from dictionary."""
        num = cls(0)
        num.mantissa = Decimal(data["mantissa"])
        num.exponent = data["exponent"]
        return num
```

### 1.3 Game State Implementation

```python
# src/idle_game/game_state.py
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from .numbers import GameNumber
import json
import asyncio

@dataclass
class Upgrade:
    """Represents a purchasable upgrade."""
    id: str
    name: str
    description: str
    base_cost: GameNumber
    cost_multiplier: float
    effect: GameNumber
    owned: int = 0
    
    @property
    def current_cost(self) -> GameNumber:
        """Calculate current cost based on owned amount."""
        if self.owned == 0:
            return self.base_cost
        return self.base_cost.multiply(self.cost_multiplier ** self.owned)
    
    @property
    def total_effect(self) -> GameNumber:
        """Calculate total effect from all owned upgrades."""
        return self.effect.multiply(self.owned)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "base_cost": self.base_cost.to_dict(),
            "cost_multiplier": self.cost_multiplier,
            "effect": self.effect.to_dict(),
            "owned": self.owned
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Upgrade':
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            base_cost=GameNumber.from_dict(data["base_cost"]),
            cost_multiplier=data["cost_multiplier"],
            effect=GameNumber.from_dict(data["effect"]),
            owned=data["owned"]
        )

@dataclass
class GameState:
    """Main game state management."""
    
    user_id: str
    counter: GameNumber = field(default_factory=lambda: GameNumber(0))
    total_earned: GameNumber = field(default_factory=lambda: GameNumber(0))
    clicks: int = 0
    last_save: datetime = field(default_factory=datetime.now)
    last_update: datetime = field(default_factory=datetime.now)
    play_time: timedelta = field(default_factory=timedelta)
    upgrades: List[Upgrade] = field(default_factory=list)
    achievements: Dict[str, bool] = field(default_factory=dict)
    settings: Dict[str, any] = field(default_factory=dict)
    
    # Game balance constants
    OFFLINE_EFFICIENCY = 0.5  # 50% production while offline
    MAX_OFFLINE_HOURS = 8     # Cap offline progress at 8 hours
    BASE_PRODUCTION = GameNumber(1)  # Base production per second
    
    def __post_init__(self):
        """Initialize upgrades if not loaded from save."""
        if not self.upgrades:
            self.upgrades = self._create_default_upgrades()
    
    def _create_default_upgrades(self) -> List[Upgrade]:
        """Create the default upgrade tree."""
        return [
            Upgrade(
                id="auto_clicker",
                name="Auto Clicker",
                description="Automatically generates 1 resource per second",
                base_cost=GameNumber(10),
                cost_multiplier=1.15,
                effect=GameNumber(1)
            ),
            Upgrade(
                id="better_clicker",
                name="Better Clicker",
                description="Each auto clicker is twice as effective",
                base_cost=GameNumber(100),
                cost_multiplier=1.25,
                effect=GameNumber(2)
            ),
            Upgrade(
                id="click_factory",
                name="Click Factory",
                description="Produces 10 resources per second",
                base_cost=GameNumber(1000),
                cost_multiplier=1.3,
                effect=GameNumber(10)
            ),
            Upgrade(
                id="quantum_processor",
                name="Quantum Processor",
                description="Generates 100 resources per second",
                base_cost=GameNumber(10000),
                cost_multiplier=1.35,
                effect=GameNumber(100)
            ),
            Upgrade(
                id="time_machine",
                name="Time Machine",
                description="Produces 1K resources per second",
                base_cost=GameNumber(100000),
                cost_multiplier=1.4,
                effect=GameNumber(1000)
            ),
            Upgrade(
                id="dimension_portal",
                name="Dimension Portal",
                description="Opens portal generating 10K resources per second",
                base_cost=GameNumber(1000000),
                cost_multiplier=1.45,
                effect=GameNumber(10000)
            ),
            Upgrade(
                id="galaxy_harvester",
                name="Galaxy Harvester",
                description="Harvests entire galaxies for 1M resources per second",
                base_cost=GameNumber("1e9"),
                cost_multiplier=1.5,
                effect=GameNumber("1e6")
            ),
            Upgrade(
                id="universe_engine",
                name="Universe Engine",
                description="Harnesses universal energy for 1B resources per second",
                base_cost=GameNumber("1e15"),
                cost_multiplier=1.55,
                effect=GameNumber("1e9")
            ),
        ]
    
    @property
    def production_rate(self) -> GameNumber:
        """Calculate total production per second."""
        rate = self.BASE_PRODUCTION
        
        for upgrade in self.upgrades:
            if upgrade.owned > 0:
                rate = rate.add(upgrade.total_effect)
        
        return rate
    
    def calculate_offline_progress(self) -> GameNumber:
        """Calculate resources earned while offline."""
        now = datetime.now()
        time_diff = now - self.last_update
        
        # Cap at maximum offline time
        offline_seconds = min(
            time_diff.total_seconds(),
            self.MAX_OFFLINE_HOURS * 3600
        )
        
        # Apply offline efficiency
        effective_seconds = offline_seconds * self.OFFLINE_EFFICIENCY
        
        # Calculate earnings
        earnings = self.production_rate.multiply(effective_seconds)
        
        # Update state
        self.last_update = now
        
        return earnings
    
    def tick(self, delta_time: float):
        """Update game state for one tick."""
        # Calculate earnings
        earnings = self.production_rate.multiply(delta_time)
        
        # Update counters
        self.counter = self.counter.add(earnings)
        self.total_earned = self.total_earned.add(earnings)
        
        # Update play time
        self.play_time += timedelta(seconds=delta_time)
        self.last_update = datetime.now()
        
        # Check achievements
        self._check_achievements()
    
    def click(self) -> GameNumber:
        """Handle manual click."""
        click_value = GameNumber(1)
        
        # Apply click multipliers from upgrades
        # (can be extended with click-specific upgrades)
        
        self.counter = self.counter.add(click_value)
        self.total_earned = self.total_earned.add(click_value)
        self.clicks += 1
        
        self._check_achievements()
        
        return click_value
    
    def can_afford(self, upgrade: Upgrade) -> bool:
        """Check if player can afford an upgrade."""
        return self.counter >= upgrade.current_cost
    
    def purchase_upgrade(self, upgrade_id: str) -> bool:
        """Purchase an upgrade if affordable."""
        upgrade = next((u for u in self.upgrades if u.id == upgrade_id), None)
        
        if not upgrade:
            return False
        
        if not self.can_afford(upgrade):
            return False
        
        # Deduct cost
        self.counter = self.counter.subtract(upgrade.current_cost)
        
        # Add upgrade
        upgrade.owned += 1
        
        # Check achievements
        self._check_achievements()
        
        return True
    
    def _check_achievements(self):
        """Check and unlock achievements."""
        # First click
        if self.clicks >= 1 and not self.achievements.get("first_click"):
            self.achievements["first_click"] = True
        
        # First upgrade
        if any(u.owned > 0 for u in self.upgrades) and not self.achievements.get("first_upgrade"):
            self.achievements["first_upgrade"] = True
        
        # Resource milestones
        milestones = [
            (GameNumber(100), "hundred"),
            (GameNumber(1000), "thousand"),
            (GameNumber("1e6"), "million"),
            (GameNumber("1e9"), "billion"),
            (GameNumber("1e12"), "trillion"),
            (GameNumber("1e15"), "quadrillion"),
        ]
        
        for threshold, achievement_id in milestones:
            if self.total_earned >= threshold and not self.achievements.get(achievement_id):
                self.achievements[achievement_id] = True
    
    def get_statistics(self) -> Dict:
        """Get game statistics."""
        return {
            "Total Earned": self.total_earned.format(),
            "Current Rate": f"{self.production_rate.format()}/s",
            "Total Clicks": f"{self.clicks:,}",
            "Play Time": str(self.play_time).split('.')[0],
            "Upgrades Owned": sum(u.owned for u in self.upgrades),
            "Achievements": f"{sum(self.achievements.values())}/{len(self.achievements)}"
        }
    
    def to_dict(self) -> dict:
        """Serialize game state to dictionary."""
        return {
            "user_id": self.user_id,
            "counter": self.counter.to_dict(),
            "total_earned": self.total_earned.to_dict(),
            "clicks": self.clicks,
            "last_save": self.last_save.isoformat(),
            "last_update": self.last_update.isoformat(),
            "play_time": self.play_time.total_seconds(),
            "upgrades": [u.to_dict() for u in self.upgrades],
            "achievements": self.achievements,
            "settings": self.settings
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GameState':
        """Deserialize game state from dictionary."""
        state = cls(
            user_id=data["user_id"],
            counter=GameNumber.from_dict(data["counter"]),
            total_earned=GameNumber.from_dict(data["total_earned"]),
            clicks=data["clicks"],
            last_save=datetime.fromisoformat(data["last_save"]),
            last_update=datetime.fromisoformat(data["last_update"]),
            play_time=timedelta(seconds=data["play_time"]),
            upgrades=[Upgrade.from_dict(u) for u in data["upgrades"]],
            achievements=data.get("achievements", {}),
            settings=data.get("settings", {})
        )
        return state
```

### 1.4 Persistence System

```python
# src/idle_game/persistence.py
import json
import aiosqlite
import asyncio
from pathlib import Path
from typing import Optional
from datetime import datetime
from .game_state import GameState

class Persistence:
    """Handles saving and loading game state."""
    
    def __init__(self, db_path: str = "game_saves.db"):
        self.db_path = db_path
        self._initialized = False
    
    async def initialize(self):
        """Initialize the database."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS game_saves (
                    user_id TEXT PRIMARY KEY,
                    save_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
        self._initialized = True
    
    async def save(self, game_state: GameState):
        """Save game state to database."""
        if not self._initialized:
            await self.initialize()
        
        save_data = json.dumps(game_state.to_dict())
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO game_saves (user_id, save_data, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    save_data = excluded.save_data,
                    updated_at = CURRENT_TIMESTAMP
            """, (game_state.user_id, save_data))
            await db.commit()
        
        game_state.last_save = datetime.now()
    
    async def load(self, user_id: str) -> Optional[GameState]:
        """Load game state from database."""
        if not self._initialized:
            await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT save_data FROM game_saves WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                
                if row:
                    save_data = json.loads(row[0])
                    game_state = GameState.from_dict(save_data)
                    
                    # Calculate offline progress
                    offline_earnings = game_state.calculate_offline_progress()
                    if offline_earnings.mantissa > 0:
                        game_state.counter = game_state.counter.add(offline_earnings)
                        game_state.total_earned = game_state.total_earned.add(offline_earnings)
                    
                    return game_state
        
        return None
    
    async def delete(self, user_id: str):
        """Delete a save file."""
        if not self._initialized:
            await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM game_saves WHERE user_id = ?",
                (user_id,)
            )
            await db.commit()
    
    async def list_saves(self) -> list:
        """List all saved games."""
        if not self._initialized:
            await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT user_id, updated_at FROM game_saves ORDER BY updated_at DESC"
            ) as cursor:
                saves = []
                async for row in cursor:
                    saves.append({
                        "user_id": row[0],
                        "updated_at": row[1]
                    })
                return saves

# Alternative JSON file persistence for simplicity
class JSONPersistence:
    """Simple JSON file-based persistence."""
    
    def __init__(self, save_dir: str = "saves"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
    
    def _get_save_path(self, user_id: str) -> Path:
        return self.save_dir / f"{user_id}.json"
    
    async def save(self, game_state: GameState):
        """Save game state to JSON file."""
        save_path = self._get_save_path(game_state.user_id)
        save_data = json.dumps(game_state.to_dict(), indent=2)
        
        # Use asyncio for non-blocking file write
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, save_path.write_text, save_data)
        
        game_state.last_save = datetime.now()
    
    async def load(self, user_id: str) -> Optional[GameState]:
        """Load game state from JSON file."""
        save_path = self._get_save_path(user_id)
        
        if not save_path.exists():
            return None
        
        # Use asyncio for non-blocking file read
        loop = asyncio.get_event_loop()
        save_data = await loop.run_in_executor(None, save_path.read_text)
        
        data = json.loads(save_data)
        game_state = GameState.from_dict(data)
        
        # Calculate offline progress
        offline_earnings = game_state.calculate_offline_progress()
        if offline_earnings.mantissa > 0:
            game_state.counter = game_state.counter.add(offline_earnings)
            game_state.total_earned = game_state.total_earned.add(offline_earnings)
        
        return game_state
    
    async def delete(self, user_id: str):
        """Delete a save file."""
        save_path = self._get_save_path(user_id)
        if save_path.exists():
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, save_path.unlink)
```

### 1.5 Custom Widgets

```python
# src/idle_game/widgets/counter.py
from textual.app import ComposeResult
from textual.widgets import Static, Button, Label
from textual.reactive import reactive
from textual.containers import Horizontal, Vertical
from textual.message import Message
from ..numbers import GameNumber

class CounterDisplay(Static):
    """Main counter display widget."""
    
    value = reactive(GameNumber(0))
    rate = reactive(GameNumber(0))
    
    class Clicked(Message):
        """Message sent when counter is clicked."""
        pass
    
    def compose(self) -> ComposeResult:
        with Vertical(id="counter-container"):
            yield Label("Resources", id="counter-title")
            yield Label("0", id="counter-value")
            yield Label("0/s", id="counter-rate")
            yield Button("Click!", id="click-button", variant="primary")
    
    def watch_value(self, value: GameNumber):
        """Update display when value changes."""
        self.query_one("#counter-value", Label).update(value.format())
    
    def watch_rate(self, rate: GameNumber):
        """Update rate display."""
        self.query_one("#counter-rate", Label).update(f"{rate.format()}/s")
    
    def on_button_pressed(self, event: Button.Pressed):
        """Handle click button."""
        if event.button.id == "click-button":
            self.post_message(self.Clicked())
```

```python
# src/idle_game/widgets/upgrades.py
from textual.app import ComposeResult
from textual.widgets import Static, Button, Label, ScrollableContainer
from textual.containers import Horizontal, Vertical
from textual.message import Message
from typing import List
from ..game_state import Upgrade

class UpgradeCard(Static):
    """Individual upgrade display."""
    
    class Purchase(Message):
        """Message sent when upgrade is purchased."""
        def __init__(self, upgrade_id: str):
            super().__init__()
            self.upgrade_id = upgrade_id
    
    def __init__(self, upgrade: Upgrade, affordable: bool = False):
        super().__init__()
        self.upgrade = upgrade
        self.affordable = affordable
    
    def compose(self) -> ComposeResult:
        with Vertical(classes="upgrade-card"):
            with Horizontal(classes="upgrade-header"):
                yield Label(self.upgrade.name, classes="upgrade-name")
                yield Label(f"Owned: {self.upgrade.owned}", classes="upgrade-owned")
            
            yield Label(self.upgrade.description, classes="upgrade-description")
            
            with Horizontal(classes="upgrade-footer"):
                yield Label(f"Cost: {self.upgrade.current_cost.format()}", classes="upgrade-cost")
                yield Button(
                    "Buy",
                    id=f"buy-{self.upgrade.id}",
                    classes="upgrade-buy",
                    disabled=not self.affordable
                )
    
    def update_upgrade(self, upgrade: Upgrade, affordable: bool):
        """Update the upgrade display."""
        self.upgrade = upgrade
        self.affordable = affordable
        
        self.query_one(".upgrade-name", Label).update(upgrade.name)
        self.query_one(".upgrade-owned", Label).update(f"Owned: {upgrade.owned}")
        self.query_one(".upgrade-cost", Label).update(f"Cost: {upgrade.current_cost.format()}")
        self.query_one(".upgrade-buy", Button).disabled = not affordable
    
    def on_button_pressed(self, event: Button.Pressed):
        """Handle buy button."""
        if event.button.id.startswith("buy-"):
            self.post_message(self.Purchase(self.upgrade.id))

class UpgradePanel(Static):
    """Panel containing all upgrades."""
    
    def __init__(self, upgrades: List[Upgrade], counter: GameNumber):
        super().__init__()
        self.upgrades = upgrades
        self.counter = counter
        self.cards = {}
    
    def compose(self) -> ComposeResult:
        with ScrollableContainer(id="upgrades-container"):
            yield Label("Upgrades", id="upgrades-title")
            for upgrade in self.upgrades:
                card = UpgradeCard(
                    upgrade,
                    affordable=self.counter >= upgrade.current_cost
                )
                self.cards[upgrade.id] = card
                yield card
    
    def update_upgrades(self, upgrades: List[Upgrade], counter: GameNumber):
        """Update all upgrade displays."""
        self.upgrades = upgrades
        self.counter = counter
        
        for upgrade in upgrades:
            if upgrade.id in self.cards:
                self.cards[upgrade.id].update_upgrade(
                    upgrade,
                    affordable=counter >= upgrade.current_cost
                )
```

```python
# src/idle_game/widgets/stats.py
from textual.app import ComposeResult
from textual.widgets import Static, Label, DataTable
from textual.containers import Vertical
from typing import Dict

class StatsPanel(Static):
    """Statistics display panel."""
    
    def __init__(self):
        super().__init__()
        self.stats = {}
    
    def compose(self) -> ComposeResult:
        with Vertical(id="stats-container"):
            yield Label("Statistics", id="stats-title")
            yield DataTable(id="stats-table")
    
    def on_mount(self):
        """Initialize the data table."""
        table = self.query_one("#stats-table", DataTable)
        table.add_column("Stat", width=20)
        table.add_column("Value", width=30)
    
    def update_stats(self, stats: Dict):
        """Update statistics display."""
        self.stats = stats
        table = self.query_one("#stats-table", DataTable)
        
        # Clear existing rows
        table.clear()
        
        # Add updated stats
        for key, value in stats.items():
            table.add_row(key, value)
```

### 1.6 Main Application

```python
# src/idle_game/app.py
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Label
from textual.reactive import reactive
from textual.timer import Timer
import asyncio
from datetime import datetime
import sys

from .game_state import GameState
from .persistence import JSONPersistence
from .widgets.counter import CounterDisplay
from .widgets.upgrades import UpgradePanel
from .widgets.stats import StatsPanel

class IdleGameApp(App):
    """Main Textual application for the idle game."""
    
    CSS_PATH = "styles/main.tcss"
    TITLE = "Idle Game"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "save", "Save"),
        ("r", "reset", "Reset"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
    ]
    
    # Game update rate
    TICK_RATE = 0.1  # 10 updates per second
    SAVE_INTERVAL = 10.0  # Auto-save every 10 seconds
    
    def __init__(self, user_id: str = "default"):
        super().__init__()
        self.user_id = user_id
        self.persistence = JSONPersistence()
        self.game_state = None
        self.last_tick = datetime.now()
        self.tick_timer = None
        self.save_timer = None
    
    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header()
        
        with Container(id="main-container"):
            with Horizontal(id="game-layout"):
                with Vertical(id="left-panel"):
                    yield CounterDisplay(id="counter")
                
                with Vertical(id="center-panel"):
                    yield UpgradePanel([], GameNumber(0), id="upgrades")
                
                with Vertical(id="right-panel"):
                    yield StatsPanel(id="stats")
        
        yield Footer()
    
    async def on_mount(self):
        """Initialize the game when app starts."""
        # Load or create game state
        saved_state = await self.persistence.load(self.user_id)
        if saved_state:
            self.game_state = saved_state
            self.notify(f"Welcome back! You earned {saved_state.calculate_offline_progress().format()} while away!")
        else:
            self.game_state = GameState(self.user_id)
            self.notify("Welcome to Idle Game! Click to start earning!")
        
        # Update UI with initial state
        self.update_display()
        
        # Start game loop
        self.tick_timer = self.set_interval(self.TICK_RATE, self.game_tick)
        self.save_timer = self.set_interval(self.SAVE_INTERVAL, self.auto_save)
    
    def update_display(self):
        """Update all UI elements with current game state."""
        # Update counter
        counter = self.query_one("#counter", CounterDisplay)
        counter.value = self.game_state.counter
        counter.rate = self.game_state.production_rate
        
        # Update upgrades
        upgrades = self.query_one("#upgrades", UpgradePanel)
        upgrades.update_upgrades(self.game_state.upgrades, self.game_state.counter)
        
        # Update stats
        stats = self.query_one("#stats", StatsPanel)
        stats.update_stats(self.game_state.get_statistics())
    
    def game_tick(self):
        """Main game update loop."""
        now = datetime.now()
        delta = (now - self.last_tick).total_seconds()
        self.last_tick = now
        
        # Update game state
        self.game_state.tick(delta)
        
        # Update display
        self.update_display()
    
    async def auto_save(self):
        """Automatic save interval."""
        await self.persistence.save(self.game_state)
        self.notify("Game saved", severity="information")
    
    async def on_counter_display_clicked(self, event: CounterDisplay.Clicked):
        """Handle manual clicks."""
        click_value = self.game_state.click()
        self.update_display()
    
    async def on_upgrade_card_purchase(self, event):
        """Handle upgrade purchases."""
        if self.game_state.purchase_upgrade(event.upgrade_id):
            self.update_display()
            self.notify(f"Purchased upgrade!", severity="success")
        else:
            self.notify("Not enough resources!", severity="error")
    
    async def action_save(self):
        """Manual save action."""
        await self.persistence.save(self.game_state)
        self.notify("Game saved!", severity="success")
    
    async def action_reset(self):
        """Reset the game."""
        # Confirm reset
        if await self.confirm("Are you sure you want to reset? This cannot be undone!"):
            await self.persistence.delete(self.user_id)
            self.game_state = GameState(self.user_id)
            self.update_display()
            self.notify("Game reset!", severity="warning")
    
    async def action_quit(self):
        """Save and quit."""
        await self.persistence.save(self.game_state)
        self.exit()
    
    def action_toggle_dark(self):
        """Toggle dark mode."""
        self.dark = not self.dark

# Entry point
def main():
    """Main entry point for the application."""
    user_id = sys.argv[1] if len(sys.argv) > 1 else "default"
    app = IdleGameApp(user_id=user_id)
    app.run()

if __name__ == "__main__":
    main()
```

### 1.7 Styling

```css
/* src/idle_game/styles/main.tcss */
/* Main layout */
#main-container {
    height: 100%;
    padding: 1;
}

#game-layout {
    height: 100%;
}

#left-panel {
    width: 30%;
    border: solid $primary;
    padding: 1;
    margin: 1;
}

#center-panel {
    width: 40%;
    border: solid $primary;
    padding: 1;
    margin: 1;
}

#right-panel {
    width: 30%;
    border: solid $primary;
    padding: 1;
    margin: 1;
}

/* Counter display */
#counter-container {
    align: center middle;
    padding: 2;
}

#counter-title {
    text-style: bold;
    text-align: center;
    color: $text;
    margin-bottom: 1;
}

#counter-value {
    text-style: bold;
    text-align: center;
    color: $warning;
    content-align: center middle;
    height: 3;
}

#counter-rate {
    text-style: italic;
    text-align: center;
    color: $success;
    margin-bottom: 2;
}

#click-button {
    width: 100%;
    margin-top: 1;
}

/* Upgrades */
#upgrades-container {
    height: 100%;
}

#upgrades-title {
    text-style: bold;
    text-align: center;
    margin-bottom: 1;
}

.upgrade-card {
    border: rounded $primary-lighten-2;
    padding: 1;
    margin-bottom: 1;
}

.upgrade-card:hover {
    border: rounded $secondary;
}

.upgrade-header {
    margin-bottom: 1;
}

.upgrade-name {
    text-style: bold;
    width: 70%;
}

.upgrade-owned {
    text-align: right;
    width: 30%;
    color: $text-muted;
}

.upgrade-description {
    margin-bottom: 1;
    color: $text-muted;
}

.upgrade-footer {
    align: left middle;
}

.upgrade-cost {
    width: 70%;
    color: $warning;
}

.upgrade-buy {
    width: 30%;
}

.upgrade-buy:disabled {
    opacity: 50%;
}

/* Stats panel */
#stats-container {
    padding: 1;
}

#stats-title {
    text-style: bold;
    text-align: center;
    margin-bottom: 1;
}

#stats-table {
    height: 100%;
}
```

## Phase 2: Web Deployment (Day 4)

### 2.1 Web Configuration

```json
// web/config.json
{
  "app": "idle_game.app:IdleGameApp",
  "host": "0.0.0.0",
  "port": 8000,
  "title": "Idle Game - Web Version",
  "debug": false,
  "watch": true
}
```

### 2.2 Web Wrapper

```html
<!-- web/index.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Idle Game</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: #0c0c0c;
            color: #00ff00;
            font-family: 'Cascadia Code', 'SF Mono', Monaco, monospace;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }
        
        #terminal-container {
            width: 90vw;
            height: 80vh;
            max-width: 1400px;
            border: 2px solid #00ff00;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 0 40px rgba(0, 255, 0, 0.3);
        }
        
        #loading {
            position: absolute;
            text-align: center;
            font-size: 24px;
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .controls {
            margin-top: 20px;
            display: flex;
            gap: 10px;
        }
        
        button {
            background: #00ff00;
            color: #000;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            font-family: inherit;
            cursor: pointer;
            border-radius: 4px;
            transition: all 0.3s;
        }
        
        button:hover {
            background: #00cc00;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 255, 0, 0.3);
        }
    </style>
</head>
<body>
    <div id="loading">Loading Idle Game...</div>
    <div id="terminal-container"></div>
    
    <div class="controls">
        <button onclick="toggleFullscreen()">Fullscreen</button>
        <button onclick="changeTheme()">Change Theme</button>
        <button onclick="exportSave()">Export Save</button>
        <button onclick="importSave()">Import Save</button>
    </div>
    
    <script>
        // Connect to textual-web WebSocket
        function connectGame() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onopen = () => {
                document.getElementById('loading').style.display = 'none';
            };
            
            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                document.getElementById('loading').textContent = 'Connection failed. Retrying...';
                setTimeout(connectGame, 3000);
            };
        }
        
        function toggleFullscreen() {
            const container = document.getElementById('terminal-container');
            if (!document.fullscreenElement) {
                container.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        }
        
        function changeTheme() {
            // Send theme change message to Textual app
            // Implementation depends on textual-web API
        }
        
        function exportSave() {
            // Request save data from server
            fetch('/api/export-save')
                .then(res => res.blob())
                .then(blob => {
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'idle-game-save.json';
                    a.click();
                });
        }
        
        function importSave() {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.json';
            input.onchange = (e) => {
                const file = e.target.files[0];
                const reader = new FileReader();
                reader.onload = (event) => {
                    fetch('/api/import-save', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: event.target.result
                    }).then(() => location.reload());
                };
                reader.readAsText(file);
            };
            input.click();
        }
        
        // Start connection
        window.addEventListener('load', connectGame);
    </script>
</body>
</html>
```

### 2.3 Deployment Script

```python
# deploy.py
#!/usr/bin/env python3
"""Deployment script for Textual idle game."""

import subprocess
import sys
from pathlib import Path

def deploy_terminal():
    """Run in terminal mode."""
    subprocess.run([sys.executable, "-m", "idle_game.app"])

def deploy_web():
    """Run in web mode."""
    subprocess.run(["textual-web", "--config", "web/config.json"])

def build_docker():
    """Build Docker image."""
    subprocess.run(["docker", "build", "-t", "idle-game:latest", "."])

def run_docker():
    """Run Docker container."""
    subprocess.run([
        "docker", "run",
        "-p", "8000:8000",
        "-v", "./saves:/app/saves",
        "idle-game:latest"
    ])

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy Idle Game")
    parser.add_argument(
        "mode",
        choices=["terminal", "web", "docker-build", "docker-run"],
        help="Deployment mode"
    )
    
    args = parser.parse_args()
    
    if args.mode == "terminal":
        deploy_terminal()
    elif args.mode == "web":
        deploy_web()
    elif args.mode == "docker-build":
        build_docker()
    elif args.mode == "docker-run":
        run_docker()
```

## Phase 3: Production Features (Day 5+)

### 3.1 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY web/ ./web/

# Create saves directory
RUN mkdir -p /app/saves

# Expose port for web mode
EXPOSE 8000

# Default to web mode
CMD ["textual-web", "--config", "web/config.json"]
```

### 3.2 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  idle-game:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./saves:/app/saves
      - ./logs:/app/logs
    environment:
      - PYTHONUNBUFFERED=1
      - GAME_MODE=web
    restart: unless-stopped
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - idle-game
    restart: unless-stopped
```

## Testing

```python
# tests/test_numbers.py
import pytest
from idle_game.numbers import GameNumber

def test_number_creation():
    n1 = GameNumber(1234.56)
    assert n1.format() == "1,235"
    
    n2 = GameNumber("1.23e10")
    assert n2.format() == "12.30B"
    
    n3 = GameNumber(0)
    assert n3.format() == "0"

def test_number_addition():
    n1 = GameNumber(100)
    n2 = GameNumber(200)
    result = n1.add(n2)
    assert result.format() == "300"

def test_number_multiplication():
    n1 = GameNumber(100)
    result = n1.multiply(10)
    assert result.format() == "1.00K"

def test_large_numbers():
    n1 = GameNumber("1e308")
    assert "e308" in n1.format()
```

## Performance Considerations

### Number System Optimization
1. **Lazy Formatting**: Only format numbers when displayed
2. **Comparison Shortcuts**: Compare exponents first
3. **Operation Batching**: Accumulate operations before normalizing
4. **Cache Common Values**: Pre-calculate common multipliers

### UI Optimization
1. **Reactive Updates**: Only update changed elements
2. **Throttled Rendering**: Limit to 10 FPS
3. **Virtual Scrolling**: For long upgrade lists
4. **CSS Animations**: Offload to browser in web mode

### Save System Optimization
1. **Differential Saves**: Only save changed data
2. **Compression**: Compress large save files
3. **Async I/O**: Non-blocking save operations
4. **Save Queuing**: Batch rapid save requests

## Deployment Options

### Terminal Mode
```bash
pip install -e .
idle-game [username]
```

### Web Mode (Single User)
```bash
textual-web --config web/config.json
```

### Web Mode (Multi User)
```bash
# With authentication
textual-web serve --auth --port 8000
```

### Cloud Deployment
- **Heroku**: Use Procfile with `web: textual-web`
- **AWS**: Deploy on EC2 with nginx reverse proxy
- **Docker**: Use provided Dockerfile
- **Kubernetes**: Scale horizontally with StatefulSets

## Monitoring & Analytics

1. **Metrics to Track**:
   - Active users
   - Average session duration
   - Most purchased upgrades
   - Resource generation rates
   - Achievement unlock rates

2. **Performance Monitoring**:
   - Frame rate in web mode
   - Save/load times
   - Memory usage over time
   - WebSocket latency

## Future Enhancements

1. **Prestige System**: Reset with multipliers
2. **Achievements**: Unlock bonuses
3. **Events**: Time-limited bonuses
4. **Leaderboards**: Global rankings
5. **Cloud Saves**: Cross-device progression
6. **Modding Support**: Custom upgrades/themes

## Conclusion

This Textual implementation provides:
- ✅ Single codebase for terminal and web
- ✅ Efficient big number handling
- ✅ Offline progression
- ✅ Auto-save system
- ✅ Beautiful TUI with CSS-like styling
- ✅ Production-ready deployment options
- ✅ Extensible architecture for future features

Total development time: 3-5 days for MVP, 1-2 weeks for production-ready version.