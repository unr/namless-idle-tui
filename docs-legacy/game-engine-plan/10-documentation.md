# Phase 10: Documentation

## Objective
Create comprehensive documentation covering architecture, API reference, user guide, and development notes.

## Prerequisites
- Phase 9 complete with polished, tested application

## Tasks

### 10.1 Create README.md
```markdown
# Idle Gold Mine - Terminal Game

A modern idle/incremental game built with Python and Textual, featuring smooth animations, particle effects, and progressive gameplay.

## Features

- 🪙 **Passive Income**: Earn 1 gold per second automatically
- 🖱️ **Active Clicking**: Click buttons for instant gold
- ✨ **Smooth Animations**: 60fps animations and particle effects
- 📦 **Treasure System**: Collect treasure chests as you progress
- 🎯 **Progressive Unlocks**: New features unlock as you earn more gold
- 💾 **Auto-save**: Your progress is saved automatically

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/idle-tui.git
cd idle-tui

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

```bash
# Run the game
python -m src.idle_game.app

# Run tests
pytest tests/

# Run with web interface (optional)
textual serve --port 8080 "python -m src.idle_game.app"
```

## How to Play

1. **Wait**: Gold accumulates automatically at 1 per second
2. **Click**: Use the "+10 Gold" button for active income
3. **Progress**: Unlock new features at milestone amounts
4. **Collect**: Treasure chests appear every 100 gold

## Controls

- `Tab` - Navigate between buttons
- `Enter/Space` - Click selected button
- `q` - Quit game (progress is saved)
- `Mouse` - Click buttons directly

## Unlocks

| Gold | Unlock | Description |
|------|--------|-------------|
| 100 | First Treasure | Visual feedback milestone |
| 500 | Mega Click | +50 gold button |
| 1000 | Auto Clicker | Automatic clicking |
| 1500 | Golden Touch | Double passive rate |
| 2000 | Ultra Click | +100 gold button |

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - See [LICENSE](LICENSE) for details.
```

### 10.2 Create Architecture Documentation
```markdown
# docs/ARCHITECTURE.md

# Architecture Overview

## System Design

The Idle Gold Mine uses a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────┐
│           Textual App               │
│  ┌─────────────┬─────────────────┐  │
│  │  GameCanvas │    Sidebar      │  │
│  │    (70%)    │     (30%)       │  │
│  └─────────────┴─────────────────┘  │
└─────────────────────────────────────┘
           ↑               ↑
           │               │
    ┌──────┴───────┬───────┴────────┐
    │   Animation  │    Game State   │
    │    Engine    │     Manager     │
    └──────────────┴────────────────┘
           ↑               ↑
           │               │
    ┌──────┴───────┬───────┴────────┐
    │   Particle   │     Unlock      │
    │    System    │     System      │
    └──────────────┴────────────────┘
```

## Core Components

### Game State (`src/idle_game/core/game_state.py`)
- Manages all game data (gold, unlocks, etc.)
- Handles passive income calculation
- Provides event callbacks for state changes

### Animation Engine (`src/idle_game/engine/`)
- **AnimationManager**: Coordinates all animations
- **Sprite**: Base class for animated objects
- **Effects**: Specific animation implementations

### Particle System (`src/idle_game/engine/particles.py`)
- **ParticleEmitter**: Spawns and manages particles
- **Particle**: Individual particle with physics
- **ParticleEffects**: Preset effect configurations

### UI Widgets (`src/idle_game/widgets/`)
- **GameCanvas**: Main game display area
- **Sidebar**: Action buttons and stats
- **AnimatedButton**: Buttons with visual feedback

## Data Flow

1. **User Input** → Textual Events → Event Handlers
2. **Game Logic** → State Updates → UI Updates
3. **Animations** → 60fps Timer → Render Updates

## Performance Considerations

- **Frame Budget**: 16.67ms per frame (60fps)
- **Animation Pooling**: Reuse completed animations
- **Dirty Rectangle**: Only update changed regions
- **Async Operations**: Non-blocking save/load

## Extension Points

- **New Unlocks**: Add to `UnlockManager.initialize_unlocks()`
- **New Effects**: Inherit from `Animation` or `Sprite`
- **New Buttons**: Add to `Sidebar` with unique ID
- **Save Data**: Extend `SaveSystem` with new fields
```

### 10.3 Create API Documentation
```python
# docs/api_reference.py
"""
API Reference for Idle Gold Mine

This module provides detailed documentation for all public APIs.
"""

def generate_api_docs():
    """Generate API documentation from docstrings."""
    
    api_docs = """
# API Reference

## Core Module

### GameState

```python
class GameState:
    '''Manages game state and progression.'''
    
    gold: Decimal
        # Current gold amount
        
    total_earned: Decimal
        # Total gold earned all time
        
    passive_rate: Decimal
        # Gold earned per second
        
    def add_gold(amount: Decimal) -> Decimal:
        '''Add gold and return amount added.'''
        
    def update(current_time: float) -> Decimal:
        '''Update state and return passive income earned.'''
        
    def get_chest_count() -> int:
        '''Calculate number of treasure chests.'''
```

## Animation Module

### Animation

```python
class Animation(ABC):
    '''Base class for all animations.'''
    
    duration: float
        # Total animation duration in seconds
        
    elapsed: float
        # Time elapsed since start
        
    active: bool
        # Whether animation is still running
        
    @abstractmethod
    def update(dt: float) -> None:
        '''Update animation by delta time.'''
        
    @abstractmethod
    def render() -> str:
        '''Return current frame as string.'''
```

### Sprite

```python
class Sprite(Animation):
    '''Animated sprite with position and velocity.'''
    
    position: Vector2
        # Current position
        
    velocity: Vector2
        # Current velocity
        
    symbol: str
        # Character(s) to display
        
    gravity: float
        # Gravity force applied
```

## Particle Module

### ParticleEmitter

```python
class ParticleEmitter:
    '''Emits particles with configurable properties.'''
    
    position: Vector2
        # Emitter position
        
    emission_rate: float
        # Particles per second
        
    def burst(count: int) -> None:
        '''Emit burst of particles.'''
        
    def update(dt: float) -> None:
        '''Update emitter and particles.'''
```

## UI Module

### GameCanvas

```python
class GameCanvas(Static):
    '''Main game display widget.'''
    
    game_state: GameState
        # Reference to game state
        
    animation_manager: AnimationManager
        # Manages all animations
        
    def spawn_particle_effect(effect_type: str, x: int, y: int) -> None:
        '''Spawn a particle effect at position.'''
        
    def trigger_unlock_effect(unlock: Unlock) -> None:
        '''Trigger special effect for unlock.'''
```
"""
    return api_docs

# Generate and save documentation
if __name__ == "__main__":
    docs = generate_api_docs()
    with open("docs/API_REFERENCE.md", "w") as f:
        f.write(docs)
```

### 10.4 Create User Guide
```markdown
# docs/USER_GUIDE.md

# User Guide

## Getting Started

Welcome to Idle Gold Mine! This guide will help you master the game.

## Basic Gameplay

### Passive Income
- You automatically earn 1 gold per second
- This happens even when you're not clicking
- Watch for the floating "+1" animations

### Active Clicking
- Click the "Click for Gold" button for instant gold
- Each click gives you +10 gold initially
- Combine clicking with passive income for faster progress

### Visual Feedback
- **Floating Numbers**: Show gold earned
- **Spinning Coins**: Appear with each earn event
- **Particle Effects**: Sparkles and bursts for special events

## Progression System

### Treasures
- Every 100 gold earned spawns a treasure chest
- Chests appear at the bottom of the game area
- They're purely visual but show your progress

### Unlocks

#### 500 Gold - Mega Click
- Unlocks the "+50 Gold" button
- Dramatic unlock animation plays
- Much faster gold generation

#### 1000 Gold - Auto Clicker
- Automatically clicks once per second
- Stacks with manual clicking
- Great for idle gameplay

#### 1500 Gold - Golden Touch
- Doubles your passive income rate
- Changes from 1/sec to 2/sec
- Exponential growth begins

#### 2000 Gold - Ultra Click
- Unlocks the "+100 Gold" button
- Massive gold gains per click
- End-game power level

## Tips & Strategies

### Early Game (0-500 gold)
1. Click actively to speed up initial progress
2. Watch for passive income between clicks
3. First treasure at 100 gold is a milestone

### Mid Game (500-2000 gold)
1. Use Mega Click button when available
2. Balance active and passive play
3. Save for important upgrades

### Late Game (2000+ gold)
1. Ultra Click dominates active play
2. Multiple income sources stack
3. Treasures accumulate rapidly

## Keyboard Shortcuts

- `Tab` - Cycle through buttons
- `Space/Enter` - Activate selected button
- `Escape` - Open menu (if implemented)
- `Q` - Quit game (saves automatically)

## Visual Effects Guide

### Particle Types
- ✨ **Sparkles**: Standard earn effect
- 💰 **Coins**: Money-related events
- ✦ **Bursts**: Special unlocks
- ⋆ **Stars**: Treasure spawns

### Animation Types
- **Floating Text**: Shows earned amounts
- **Spinning Coins**: Rotational animations
- **Particle Fountains**: Large rewards
- **Flash Effects**: Major unlocks

## Troubleshooting

### Game Won't Start
- Check Python version (3.8+ required)
- Verify all dependencies installed
- Try running in different terminal

### Animations Stuttering
- Check CPU usage
- Close other applications
- Reduce terminal size

### Progress Not Saving
- Check file permissions
- Verify save directory exists
- Look for error messages

## Advanced Features

### Save System
- Game auto-saves every 30 seconds
- Manual save with Ctrl+S (if implemented)
- Save file location: `~/.idle_game/save.json`

### Statistics Tracking
- Total gold earned lifetime
- Treasures collected
- Time played
- Clicks performed

## Community

Join our community:
- GitHub Issues for bug reports
- Discussions for strategies
- Wiki for detailed information
```

### 10.5 Create Developer Documentation
```markdown
# docs/DEVELOPMENT.md

# Development Guide

## Setting Up Development Environment

```bash
# Clone and setup
git clone https://github.com/yourusername/idle-tui.git
cd idle-tui

# Virtual environment
python -m venv venv
source venv/bin/activate

# Development dependencies
pip install -r requirements-dev.txt
```

## Project Structure

```
idle-tui/
├── src/
│   └── idle_game/
│       ├── core/          # Game logic
│       ├── engine/        # Animation/particles
│       ├── widgets/       # UI components
│       └── app.py         # Main application
├── tests/                 # Test suite
├── docs/                  # Documentation
└── requirements.txt       # Dependencies
```

## Adding New Features

### 1. New Animation Type

```python
# src/idle_game/engine/my_effect.py
from .animation import Sprite, Vector2

class MyEffect(Sprite):
    def __init__(self, x: int, y: int):
        super().__init__(
            position=Vector2(x, y),
            velocity=Vector2(0, -5),
            symbol="★",
            duration=2.0
        )
    
    def update(self, dt: float) -> None:
        super().update(dt)
        # Custom behavior here
```

### 2. New Unlock

```python
# In UnlockManager.initialize_unlocks()
self.unlocks.append(
    Unlock(
        id="my_feature",
        name="My Feature",
        description="Does something cool",
        unlock_type=UnlockType.FEATURE,
        requirement=Decimal("5000")
    )
)
```

### 3. New Button

```python
# In Sidebar
self.add_button(
    "my-button",
    "My Button",
    reward=200
)
```

## Testing Guidelines

### Unit Tests
```python
def test_my_feature():
    # Arrange
    state = GameState()
    
    # Act
    result = state.my_method()
    
    # Assert
    assert result == expected
```

### Integration Tests
```python
@pytest.mark.asyncio
async def test_integration():
    app = IdleGameApp()
    async with app.run_test() as pilot:
        # Test interactions
        await pilot.click("#my-button")
```

## Performance Optimization

### Profiling
```bash
# CPU profiling
python -m cProfile -o profile.stats src/idle_game/app.py

# Memory profiling
mprof run python -m src.idle_game.app
mprof plot
```

### Optimization Tips
1. Pool animations instead of creating new
2. Use dirty rectangle rendering
3. Batch particle updates
4. Cache computed values

## Code Style

### Standards
- PEP 8 compliance
- Type hints for all functions
- Docstrings for public APIs
- 100 character line limit

### Tools
```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

## Debugging

### Logging
```python
import logging

logging.debug("Variable state: %s", var)
logging.info("Action performed")
logging.error("Error occurred: %s", error)
```

### Textual DevTools
```bash
# Run with dev tools
textual run --dev src.idle_game.app
```

## Release Process

1. Update version in `__init__.py`
2. Run full test suite
3. Update CHANGELOG.md
4. Create git tag
5. Build distribution
6. Upload to PyPI (if applicable)

## Contributing

1. Fork the repository
2. Create feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit pull request

## Resources

- [Textual Documentation](https://textual.textualize.io/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Python Asyncio](https://docs.python.org/3/library/asyncio.html)
```

## Documentation Checklist

- [ ] README.md with quick start
- [ ] Architecture overview
- [ ] API reference
- [ ] User guide
- [ ] Developer documentation
- [ ] Inline code comments
- [ ] Docstrings for all public methods
- [ ] Type hints throughout
- [ ] Example code snippets
- [ ] Troubleshooting guide

## Commands to Generate Docs

```bash
# Generate API docs from docstrings
python -m pydoc -w src.idle_game

# Generate Sphinx documentation
sphinx-quickstart docs
sphinx-apidoc -o docs/source src/idle_game
make -C docs html

# Generate coverage report
pytest --cov=src/idle_game --cov-report=html

# Generate dependency graph
pydeps src/idle_game --only idle_game -o deps.svg
```

## Success Criteria
- [ ] All components documented
- [ ] Examples for common tasks
- [ ] Clear installation instructions
- [ ] API reference complete
- [ ] Architecture explained
- [ ] Contributing guidelines

## Project Complete!

Congratulations! The Idle Gold Mine game is now:
- ✅ Fully functional
- ✅ Well-tested  
- ✅ Performant
- ✅ Documented
- ✅ Ready for release

The game can now be:
1. Published to GitHub
2. Shared with the community
3. Extended with new features
4. Used as a learning resource
