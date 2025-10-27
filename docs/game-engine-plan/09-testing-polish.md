# Phase 9: Testing & Polish

## Objective
Complete comprehensive testing, fix bugs, optimize performance, and polish the user experience.

## Prerequisites
- Phases 1-8 complete with all features implemented

## Tasks

### 9.1 Create Integration Tests
```python
# tests/test_integration.py
import pytest
from decimal import Decimal
import asyncio
from textual.pilot import Pilot
from src.idle_game.app import IdleGameApp
from src.idle_game.core.game_state import GameState

@pytest.mark.asyncio
async def test_app_startup():
    """Test app starts without errors."""
    app = IdleGameApp()
    async with app.run_test() as pilot:
        # Check main components exist
        assert app.query_one("GameCanvas")
        assert app.query_one("Sidebar")
        assert app.query_one("#gold-button-10")

@pytest.mark.asyncio  
async def test_passive_income_integration():
    """Test passive income updates UI."""
    app = IdleGameApp()
    async with app.run_test() as pilot:
        canvas = app.query_one("GameCanvas")
        initial_gold = canvas.gold
        
        # Wait for passive income
        await pilot.pause(1.5)
        
        # Should have earned at least 1 gold
        assert canvas.gold > initial_gold

@pytest.mark.asyncio
async def test_click_button_integration():
    """Test clicking button adds gold."""
    app = IdleGameApp()
    async with app.run_test() as pilot:
        canvas = app.query_one("GameCanvas")
        initial_gold = canvas.gold
        
        # Click the button
        await pilot.click("#gold-button-10")
        
        # Should have added 10 gold
        assert canvas.gold == initial_gold + 10

@pytest.mark.asyncio
async def test_treasure_spawn_integration():
    """Test treasures appear at correct thresholds."""
    app = IdleGameApp()
    async with app.run_test() as pilot:
        canvas = app.query_one("GameCanvas")
        
        # Add gold to trigger treasure
        canvas.game_state.gold = Decimal("100")
        canvas.check_treasure_spawns()
        
        assert canvas.treasure_manager.last_chest_count == 1

@pytest.mark.asyncio
async def test_unlock_integration():
    """Test button unlock at 500 gold."""
    app = IdleGameApp()
    async with app.run_test() as pilot:
        # Give enough gold
        canvas = app.query_one("GameCanvas")
        sidebar = app.query_one("Sidebar")
        
        canvas.game_state.gold = Decimal("500")
        sidebar.check_unlocks()
        
        # Should have unlocked button_50
        assert sidebar.unlock_manager.is_unlocked("button_50")
```

### 9.2 Create Performance Tests
```python
# tests/test_performance.py
import pytest
import time
import psutil
import gc
from src.idle_game.engine.animation_manager import AnimationManager
from src.idle_game.engine.particles import ParticleEmitter, Vector2
from src.idle_game.engine.coin_effects import CoinShower

def test_animation_performance():
    """Test animation system can handle many sprites."""
    manager = AnimationManager()
    
    # Add 100 animations
    for i in range(100):
        shower = CoinShower(i % 60, i % 20, count=5)
        for coin in shower.get_animations():
            manager.add_animation(coin)
    
    # Measure update time
    start = time.perf_counter()
    for _ in range(60):  # 1 second at 60fps
        manager.update(1/60)
    elapsed = time.perf_counter() - start
    
    # Should complete in under 2 seconds (allowing overhead)
    assert elapsed < 2.0

def test_particle_performance():
    """Test particle system performance."""
    emitters = []
    
    # Create 20 emitters
    for i in range(20):
        emitter = ParticleEmitter(Vector2(i * 3, 10))
        emitter.burst(50)  # 50 particles each
        emitters.append(emitter)
    
    # Update for 60 frames
    start = time.perf_counter()
    for _ in range(60):
        for emitter in emitters:
            emitter.update(1/60)
    elapsed = time.perf_counter() - start
    
    # Should handle 1000 particles in under 1 second
    assert elapsed < 1.0

def test_memory_usage():
    """Test for memory leaks."""
    process = psutil.Process()
    
    # Get initial memory
    gc.collect()
    initial_mem = process.memory_info().rss / 1024 / 1024  # MB
    
    # Create and destroy many objects
    for _ in range(100):
        manager = AnimationManager()
        for i in range(50):
            shower = CoinShower(10, 10, count=10)
            for coin in shower.get_animations():
                manager.add_animation(coin)
        
        # Update until all complete
        for _ in range(200):
            manager.update(1/60)
        
        # Cleanup
        manager.clear()
        del manager
    
    # Force garbage collection
    gc.collect()
    final_mem = process.memory_info().rss / 1024 / 1024  # MB
    
    # Memory should not grow by more than 50MB
    assert final_mem - initial_mem < 50
```

### 9.3 Create CSS Polish
```python
# src/idle_game/styles/app.tcss
/* Textual CSS for polished appearance */

Screen {
    background: $surface;
}

GameCanvas {
    background: $panel;
    border: tall $primary;
    padding: 1;
}

Sidebar {
    background: $panel-darken-1;
    border: tall $secondary;
    padding: 1;
}

AnimatedButton {
    background: $primary;
    color: $text;
    text-style: bold;
    height: 3;
    margin: 1 2;
    border: tall $primary-lighten-2;
}

AnimatedButton:hover {
    background: $primary-lighten-1;
    border: tall $warning;
}

AnimatedButton:focus {
    background: $primary-lighten-2;
}

.button-pressed {
    background: $success !important;
    border: tall $success-lighten-2 !important;
}

.button-unlocked {
    background: $warning !important;
    color: $panel !important;
    border: tall $warning-lighten-2 !important;
}

.flash {
    background: $warning-lighten-3 !important;
}

StatsPanel {
    background: $panel-darken-2;
    border: tall $primary-darken-1;
    padding: 1;
    margin: 1;
}

#actions-title {
    background: $primary;
    color: $text;
    text-align: center;
    text-style: bold;
    padding: 1;
}

#gold-display {
    text-align: center;
    text-style: bold;
    color: $warning;
}
```

### 9.4 Add Error Handling
```python
# src/idle_game/core/error_handler.py
import logging
from functools import wraps
from typing import Any, Callable

# Configure logging
logging.basicConfig(
    filename='idle_game.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def safe_execute(default_return: Any = None):
    """Decorator for safe execution with error logging."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.error(f"Error in {func.__name__}: {str(e)}")
                return default_return
        return wrapper
    return decorator

class GameError(Exception):
    """Base exception for game errors."""
    pass

class SaveError(GameError):
    """Error during save operation."""
    pass

class LoadError(GameError):
    """Error during load operation."""
    pass
```

### 9.5 Add Save/Load System
```python
# src/idle_game/core/save_system.py
import json
from pathlib import Path
from decimal import Decimal
from typing import Dict, Any
from .error_handler import SaveError, LoadError, safe_execute

class SaveSystem:
    """Handle game save/load operations."""
    
    SAVE_FILE = Path.home() / ".idle_game" / "save.json"
    
    @classmethod
    def ensure_save_dir(cls) -> None:
        """Ensure save directory exists."""
        cls.SAVE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    @safe_execute()
    def save_game(cls, game_state) -> bool:
        """Save game state to file."""
        cls.ensure_save_dir()
        
        try:
            save_data = {
                'gold': str(game_state.gold),
                'total_earned': str(game_state.total_earned),
                'passive_rate': str(game_state.passive_rate),
                'unlocks': cls._save_unlocks(game_state)
            }
            
            with open(cls.SAVE_FILE, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            return True
            
        except Exception as e:
            raise SaveError(f"Failed to save game: {e}")
    
    @classmethod
    @safe_execute({})
    def load_game(cls) -> Dict[str, Any]:
        """Load game state from file."""
        if not cls.SAVE_FILE.exists():
            return {}
        
        try:
            with open(cls.SAVE_FILE, 'r') as f:
                save_data = json.load(f)
            
            # Convert strings back to Decimals
            save_data['gold'] = Decimal(save_data.get('gold', '0'))
            save_data['total_earned'] = Decimal(save_data.get('total_earned', '0'))
            save_data['passive_rate'] = Decimal(save_data.get('passive_rate', '1'))
            
            return save_data
            
        except Exception as e:
            raise LoadError(f"Failed to load game: {e}")
    
    @classmethod
    def _save_unlocks(cls, game_state) -> List[str]:
        """Save unlock IDs."""
        if hasattr(game_state, 'unlock_manager'):
            return [u.id for u in game_state.unlock_manager.unlocks if u.unlocked]
        return []
```

## Final Testing Checklist

### Functionality Tests
- [ ] Passive income works (1 gold/sec)
- [ ] Click button adds 10 gold
- [ ] Animations play smoothly
- [ ] Particles render correctly
- [ ] Treasures spawn at 100 gold intervals
- [ ] +50 button unlocks at 500 gold
- [ ] All visual effects work

### Performance Tests  
- [ ] Maintains 60fps with normal gameplay
- [ ] Handles 100+ simultaneous animations
- [ ] Memory usage stays under 100MB
- [ ] No memory leaks after extended play
- [ ] CPU usage under 30%

### Edge Cases
- [ ] App handles rapid clicking
- [ ] Works with terminal resize
- [ ] Recovers from errors gracefully
- [ ] Save/load preserves state
- [ ] Large gold amounts display correctly

### Polish Items
- [ ] Consistent visual style
- [ ] Smooth animations
- [ ] Clear UI feedback
- [ ] No visual glitches
- [ ] Keyboard shortcuts work

## Commands to Run

```bash
# Run all tests
pytest tests/ -v --cov=src/idle_game --cov-report=html

# Run performance profiling
python -m cProfile -o profile.stats src/idle_game/app.py
python -m pstats profile.stats

# Check memory usage
mprof run python -m src.idle_game.app
mprof plot

# Run type checking
mypy src/idle_game --ignore-missing-imports

# Format code
black src/ tests/
ruff check src/ tests/ --fix

# Generate test report
pytest tests/ --html=report.html --self-contained-html
```

## Success Criteria
- [ ] All tests pass (100%)
- [ ] Code coverage > 90%
- [ ] No type errors
- [ ] Performance benchmarks met
- [ ] No critical bugs
- [ ] Smooth user experience

## Next Phase
Once testing and polish complete, proceed to Phase 10: Documentation.
