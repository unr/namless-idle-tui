# Idle Game Implementation Plan - Overview

## Project Goal
Build a fully functional idle game with animations, particle effects, and progressive gameplay using Textual and Rich.

## Core Requirements
- Passive income: 1 gold coin per second
- Visual feedback: Animated gold coins when earning
- Manual clicking: Button for +10 gold (always visible)
- Progressive unlocks: +50 gold button at 500 coins
- Treasure chests: Display one for every 100 gold
- Particle effects: Visual feedback for all coin gains
- 70/30 layout: Game area (left) and sidebar (right)

## Technical Stack
- **Framework**: Textual (TUI framework)
- **Rendering**: Rich (text rendering, already in Textual)
- **Animations**: Asyncio (timing and concurrency)
- **Optional**: NumPy (if particle count > 50)

## Project Phases

### Phase 1: Core Infrastructure (Day 1)
- Basic app structure with 70/30 layout
- Game state management system
- Basic counter display
- File: `01-core-infrastructure.md`

### Phase 2: Passive Income System (Day 1)
- Implement 1 gold/second mechanic
- Update counter display
- Add game tick system
- File: `02-passive-income.md`

### Phase 3: Animation Engine (Day 2)
- Create animation framework
- Implement timing system
- Add sprite management
- File: `03-animation-engine.md`

### Phase 4: Gold Coin Animation (Day 2)
- Create gold coin sprite
- Implement floating animation
- Add to passive income events
- File: `04-gold-coin-animation.md`

### Phase 5: Manual Click System (Day 3)
- Add +10 gold button
- Implement click handlers
- Add button animations
- File: `05-manual-click.md`

### Phase 6: Particle Effects (Day 3)
- Create particle system
- Add sparkle effects
- Integrate with coin events
- File: `06-particle-effects.md`

### Phase 7: Treasure System (Day 4)
- Implement treasure chest display
- Add chest spawn animations
- Calculate chest count from gold
- File: `07-treasure-system.md`

### Phase 8: Progressive Features (Day 4)
- Add +50 gold button at 500 coins
- Implement unlock animations
- Add progression feedback
- File: `08-progressive-features.md`

### Phase 9: Testing & Polish (Day 5)
- Complete test suite
- Performance optimization
- Bug fixes and polish
- File: `09-testing-polish.md`

### Phase 10: Documentation (Day 5)
- API documentation
- User guide
- Architecture overview
- File: `10-documentation.md`

## Success Metrics
- [ ] App runs at stable 60fps
- [ ] All animations smooth and responsive
- [ ] Zero crashes during normal gameplay
- [ ] All tests passing (>90% coverage)
- [ ] Clear documentation for all systems

## File Structure After Completion
```
idle-tui/
├── src/
│   └── idle_game/
│       ├── core/
│       │   ├── __init__.py
│       │   ├── game_state.py    # Game state management
│       │   └── events.py         # Event system
│       ├── engine/
│       │   ├── __init__.py
│       │   ├── animation.py      # Animation system
│       │   ├── particles.py      # Particle effects
│       │   └── timing.py         # Frame timing
│       ├── widgets/
│       │   ├── __init__.py
│       │   ├── game_canvas.py    # Main game area
│       │   ├── sidebar.py        # Action buttons
│       │   └── effects.py        # Visual effects
│       └── app.py                # Main application
├── tests/
│   ├── test_game_state.py
│   ├── test_animation.py
│   ├── test_particles.py
│   └── test_integration.py
└── docs/
    └── game-engine-plan/
        └── [implementation plans]
```

## Development Notes for AI Agent

1. **Start each phase fresh**: Each phase should be independently executable
2. **Test continuously**: Run tests after each major addition
3. **Commit often**: Make atomic commits for easy rollback
4. **Profile performance**: Monitor FPS and CPU usage
5. **Document as you go**: Update docstrings and comments

## Dependencies to Install
```bash
pip install textual rich pytest pytest-asyncio
```

## How to Run After Each Phase
```bash
# Run the app
python -m src.idle_game.app

# Run tests
pytest tests/ -v

# Check performance
python -m cProfile -s cumulative src/idle_game/app.py
```
