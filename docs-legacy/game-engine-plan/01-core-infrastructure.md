# Phase 1: Core Infrastructure

## Objective
Set up the foundational application structure with proper layout, game state management, and basic display components.

## Tasks

### 1.1 Create Application Structure
```python
# src/idle_game/app.py
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static, Header, Footer

class IdleGameApp(App):
    """Main application class for the idle game."""
    
    CSS = """
    #game-area {
        width: 70%;
        border: solid green;
        padding: 1;
    }
    
    #sidebar {
        width: 30%;
        border: solid blue;
        padding: 1;
    }
    
    #gold-display {
        text-align: center;
        text-style: bold;
        color: gold;
        padding: 2;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Static("Game Area", id="game-area")
            yield Static("Sidebar", id="sidebar")
        yield Footer()
```

### 1.2 Implement Game State
```python
# src/idle_game/core/game_state.py
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
import asyncio

@dataclass
class GameState:
    """Manages all game state and progression."""
    
    gold: Decimal = Decimal("0")
    total_earned: Decimal = Decimal("0")
    passive_rate: Decimal = Decimal("1")  # Gold per second
    
    # Unlock thresholds
    CHEST_THRESHOLD = Decimal("100")
    BUTTON2_THRESHOLD = Decimal("500")
    
    def add_gold(self, amount: Decimal) -> Decimal:
        """Add gold and track total earned."""
        amount = Decimal(str(amount))
        self.gold += amount
        self.total_earned += amount
        return amount
    
    def get_chest_count(self) -> int:
        """Calculate number of treasure chests to display."""
        return int(self.gold // self.CHEST_THRESHOLD)
    
    def is_button2_unlocked(self) -> bool:
        """Check if the +50 gold button should be visible."""
        return self.gold >= self.BUTTON2_THRESHOLD
```

### 1.3 Create Game Canvas Widget
```python
# src/idle_game/widgets/game_canvas.py
from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
from rich.align import Align
from decimal import Decimal

class GameCanvas(Static):
    """Main game display area."""
    
    gold = reactive(Decimal("0"))
    
    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
    
    def on_mount(self) -> None:
        """Set up the game canvas when mounted."""
        self.update_display()
    
    def watch_gold(self, old_value: Decimal, new_value: Decimal) -> None:
        """React to gold changes."""
        self.update_display()
    
    def update_display(self) -> None:
        """Update the canvas display."""
        # Create centered gold display
        gold_text = Text(f"💰 Gold: {int(self.gold)}", style="bold yellow")
        centered = Align.center(gold_text, vertical="middle")
        self.update(centered)
    
    def add_gold(self, amount: Decimal) -> None:
        """Add gold with visual feedback."""
        self.gold = self.game_state.add_gold(amount)
```

### 1.4 Create Sidebar Widget
```python
# src/idle_game/widgets/sidebar.py
from textual.widgets import Static
from textual.containers import Vertical
from textual.widgets import Button
from textual.app import ComposeResult

class Sidebar(Static):
    """Sidebar with action buttons."""
    
    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
    
    def compose(self) -> ComposeResult:
        """Create sidebar layout."""
        with Vertical():
            yield Button("Click for +10 Gold", id="gold-button-10")
```

### 1.5 Wire Everything Together
```python
# Update src/idle_game/app.py
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Header, Footer
from .core.game_state import GameState
from .widgets.game_canvas import GameCanvas
from .widgets.sidebar import Sidebar

class IdleGameApp(App):
    """Main application class for the idle game."""
    
    CSS = """
    GameCanvas {
        width: 70%;
        border: solid green;
        padding: 1;
        height: 100%;
    }
    
    Sidebar {
        width: 30%;
        border: solid blue;
        padding: 1;
        height: 100%;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.game_state = GameState()
        
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            yield GameCanvas(self.game_state)
            yield Sidebar(self.game_state)
        yield Footer()
    
    def on_button_pressed(self, event) -> None:
        """Handle button clicks."""
        if event.button.id == "gold-button-10":
            canvas = self.query_one(GameCanvas)
            canvas.add_gold(10)
```

## Tests to Write

### Test Game State
```python
# tests/test_game_state.py
import pytest
from decimal import Decimal
from src.idle_game.core.game_state import GameState

def test_game_state_initialization():
    state = GameState()
    assert state.gold == Decimal("0")
    assert state.total_earned == Decimal("0")

def test_add_gold():
    state = GameState()
    amount_added = state.add_gold(Decimal("10"))
    assert amount_added == Decimal("10")
    assert state.gold == Decimal("10")
    assert state.total_earned == Decimal("10")

def test_chest_count():
    state = GameState()
    state.add_gold(Decimal("250"))
    assert state.get_chest_count() == 2

def test_button2_unlock():
    state = GameState()
    assert not state.is_button2_unlocked()
    state.add_gold(Decimal("500"))
    assert state.is_button2_unlocked()
```

## Success Criteria
- [ ] App launches without errors
- [ ] 70/30 layout is visible and correct
- [ ] Gold counter displays in center of game area
- [ ] +10 gold button is visible in sidebar
- [ ] Clicking button increases gold counter
- [ ] All tests pass

## Commands to Run
```bash
# Create the file structure
mkdir -p src/idle_game/core
mkdir -p src/idle_game/widgets
mkdir -p tests

# Create __init__.py files
touch src/idle_game/__init__.py
touch src/idle_game/core/__init__.py
touch src/idle_game/widgets/__init__.py

# Run the app
python -m src.idle_game.app

# Run tests
pytest tests/test_game_state.py -v
```

## Next Phase
Once this phase is complete and all tests pass, proceed to Phase 2: Passive Income System.
