# Phase 2: Passive Income System

## Objective
Implement the core idle game mechanic: earning 1 gold coin per second automatically with proper timing and state updates.

## Prerequisites
- Phase 1 complete with working game state and display

## Tasks

### 2.1 Create Game Timer System
```python
# src/idle_game/engine/timing.py
import asyncio
import time
from typing import Callable, Optional

class GameTimer:
    """Manages game loop timing for consistent updates."""
    
    def __init__(self, target_fps: int = 60):
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        self.running = False
        self.last_update = time.perf_counter()
        self.accumulated_time = 0.0
        
    def start(self):
        """Start the timer."""
        self.running = True
        self.last_update = time.perf_counter()
        self.accumulated_time = 0.0
        
    def stop(self):
        """Stop the timer."""
        self.running = False
        
    def tick(self) -> float:
        """Update timer and return delta time."""
        if not self.running:
            return 0.0
            
        current_time = time.perf_counter()
        delta = current_time - self.last_update
        self.last_update = current_time
        self.accumulated_time += delta
        
        return delta
    
    def should_update_income(self, income_rate: float = 1.0) -> bool:
        """Check if enough time has passed for income update."""
        if self.accumulated_time >= income_rate:
            self.accumulated_time -= income_rate
            return True
        return False
```

### 2.2 Add Passive Income to Game State
```python
# Update src/idle_game/core/game_state.py
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Callable
import time

@dataclass
class GameState:
    """Manages all game state and progression."""
    
    gold: Decimal = Decimal("0")
    total_earned: Decimal = Decimal("0")
    passive_rate: Decimal = Decimal("1")  # Gold per second
    
    # Timing
    last_passive_time: float = field(default_factory=time.perf_counter)
    passive_accumulator: float = 0.0
    
    # Event callbacks
    on_gold_earned: List[Callable] = field(default_factory=list)
    
    # Unlock thresholds
    CHEST_THRESHOLD = Decimal("100")
    BUTTON2_THRESHOLD = Decimal("500")
    
    def update(self, current_time: float) -> Decimal:
        """Update game state and return gold earned from passive income."""
        delta = current_time - self.last_passive_time
        self.last_passive_time = current_time
        self.passive_accumulator += delta
        
        gold_earned = Decimal("0")
        
        # Check if we should award passive income
        if self.passive_accumulator >= 1.0:  # 1 second
            gold_earned = self.passive_rate
            self.add_gold(gold_earned)
            self.passive_accumulator -= 1.0
            
            # Trigger callbacks
            for callback in self.on_gold_earned:
                callback(gold_earned, "passive")
        
        return gold_earned
    
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

### 2.3 Update Game Canvas for Passive Updates
```python
# Update src/idle_game/widgets/game_canvas.py
from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
from rich.align import Align
from rich.panel import Panel
from decimal import Decimal
import time

class GameCanvas(Static):
    """Main game display area."""
    
    gold = reactive(Decimal("0"))
    passive_indicator = reactive(False)
    
    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
        self.last_passive_flash = 0
        
        # Register for gold earned events
        game_state.on_gold_earned.append(self.on_passive_gold)
    
    def on_mount(self) -> None:
        """Set up the game canvas when mounted."""
        self.update_display()
        # Start passive income timer
        self.set_interval(1/60, self.update_passive_income)
    
    def update_passive_income(self) -> None:
        """Check for passive income updates."""
        current_time = time.perf_counter()
        gold_earned = self.game_state.update(current_time)
        
        if gold_earned > 0:
            self.gold = self.game_state.gold
    
    def on_passive_gold(self, amount: Decimal, source: str) -> None:
        """Handle passive gold earned event."""
        if source == "passive":
            self.passive_indicator = True
            self.set_timer(0.5, self.clear_passive_indicator)
    
    def clear_passive_indicator(self) -> None:
        """Clear the passive income indicator."""
        self.passive_indicator = False
    
    def watch_gold(self, old_value: Decimal, new_value: Decimal) -> None:
        """React to gold changes."""
        self.update_display()
    
    def watch_passive_indicator(self, value: bool) -> None:
        """React to passive indicator changes."""
        self.update_display()
    
    def update_display(self) -> None:
        """Update the canvas display."""
        # Create gold display with passive indicator
        gold_text = f"💰 Gold: {int(self.gold)}"
        if self.passive_indicator:
            gold_text += " ⬆️ +1"
        
        display_text = Text(gold_text, style="bold yellow")
        
        # Add passive income rate
        rate_text = Text(f"\n📈 Rate: {self.game_state.passive_rate}/sec", 
                        style="dim cyan")
        display_text.append(rate_text)
        
        # Center everything
        panel = Panel(
            Align.center(display_text, vertical="middle"),
            title="💎 Idle Gold Mine 💎",
            border_style="green"
        )
        
        self.update(panel)
    
    def add_gold(self, amount: Decimal) -> None:
        """Add gold with visual feedback."""
        self.gold = self.game_state.add_gold(amount)
```

### 2.4 Add Visual Feedback for Passive Income
```python
# src/idle_game/core/events.py
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

@dataclass
class GoldEarnedEvent:
    """Event fired when gold is earned."""
    amount: Decimal
    source: Literal["passive", "click", "bonus"]
    timestamp: float

class EventBus:
    """Simple event bus for game events."""
    
    def __init__(self):
        self.listeners = {}
    
    def subscribe(self, event_type: type, callback):
        """Subscribe to an event type."""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
    
    def emit(self, event):
        """Emit an event to all listeners."""
        event_type = type(event)
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                callback(event)
```

### 2.5 Update Main App with Timer
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
        height: 100%;
    }
    
    Sidebar {
        width: 30%;
        height: 100%;
    }
    
    #gold-button-10 {
        margin: 1;
        width: 100%;
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
    
    def on_mount(self) -> None:
        """Start game systems when app mounts."""
        self.title = "Idle Gold Mine"
        self.sub_title = "Click or wait to earn gold!"
    
    def on_button_pressed(self, event) -> None:
        """Handle button clicks."""
        if event.button.id == "gold-button-10":
            canvas = self.query_one(GameCanvas)
            canvas.add_gold(10)
```

## Tests to Write

### Test Timer System
```python
# tests/test_timing.py
import pytest
import time
from src.idle_game.engine.timing import GameTimer

def test_timer_initialization():
    timer = GameTimer(60)
    assert timer.target_fps == 60
    assert timer.frame_time == pytest.approx(1/60, rel=1e-3)
    assert not timer.running

def test_timer_start_stop():
    timer = GameTimer()
    timer.start()
    assert timer.running
    timer.stop()
    assert not timer.running

def test_timer_tick():
    timer = GameTimer()
    timer.start()
    time.sleep(0.1)
    delta = timer.tick()
    assert delta >= 0.1
    assert delta < 0.15  # Some tolerance

def test_income_update():
    timer = GameTimer()
    timer.start()
    timer.accumulated_time = 0.5
    assert not timer.should_update_income(1.0)
    timer.accumulated_time = 1.5
    assert timer.should_update_income(1.0)
    assert timer.accumulated_time < 1.0
```

### Test Passive Income
```python
# tests/test_passive_income.py
import pytest
import time
from decimal import Decimal
from src.idle_game.core.game_state import GameState

def test_passive_income_accumulation():
    state = GameState()
    start_time = time.perf_counter()
    
    # Simulate 1 second passing
    time.sleep(1.1)
    current_time = time.perf_counter()
    
    gold_earned = state.update(current_time)
    assert gold_earned == Decimal("1")
    assert state.gold == Decimal("1")

def test_passive_income_callbacks():
    state = GameState()
    callback_called = False
    earned_amount = None
    
    def callback(amount, source):
        nonlocal callback_called, earned_amount
        callback_called = True
        earned_amount = amount
    
    state.on_gold_earned.append(callback)
    
    # Force passive income
    state.passive_accumulator = 1.0
    state.update(time.perf_counter())
    
    assert callback_called
    assert earned_amount == Decimal("1")
```

## Success Criteria
- [ ] Gold increases by 1 every second automatically
- [ ] Visual indicator shows when passive income is earned
- [ ] Passive rate is displayed on screen
- [ ] Game continues earning while idle
- [ ] All timing tests pass
- [ ] No performance issues at 60fps

## Commands to Run
```bash
# Create engine directory
mkdir -p src/idle_game/engine
touch src/idle_game/engine/__init__.py

# Run the app
python -m src.idle_game.app

# Run tests
pytest tests/test_timing.py -v
pytest tests/test_passive_income.py -v

# Monitor performance
python -m cProfile -s cumulative src/idle_game/app.py
```

## Next Phase
Once passive income is working smoothly, proceed to Phase 3: Animation Engine.
