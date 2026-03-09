# Emotion Merchant - Implementation Plan

## Research Summary

### Idle Game Design Principles (2025)
- **Balance**: 60% idle progression / 40% active engagement
- **Growth**: Exponential growth with exponential costs to balance
- **Loops**: Hook (0-30min), Habit (1-7 days), Hobby (weeks-months)
- **Prestige**: Reset when progress slows to 10-20% of peak speed
- **Progression**: Multiple layers with "bumpy" pacing (fast/slow periods)

### Textual Framework Best Practices
- **State**: Reactive attributes for all UI-driving state
- **Architecture**: Separate models (logic), widgets (UI), app (orchestration)
- **Performance**: Multiple timer rates (60 FPS render, 10 FPS logic, 1 FPS save)
- **Data Flow**: Data binding for parent-child synchronization
- **Navigation**: Screen/mode system for different game sections
- **Persistence**: JSON saves with offline progression calculation
- **Async**: Worker threads for expensive I/O operations

## Game Requirements (from docs/game-design/*)

### Core Systems
1. **Resource System**: 10-tier emotion hierarchy (Smiles → Singularity)
2. **Generation**: Click harvesting + passive production
3. **Storage**: Capacity limits with overflow consequences
4. **Purity**: Quality system with degradation over time
5. **Customers**: Tutorial (event-triggered) + queue system
6. **Alchemy**: Recipe mixing with success rates
7. **Shop**: Upgrades and buildings
8. **Prestige**: Emotional Depth currency with meta-upgrades

### Gameplay Phases
- **Tutorial** (0-10min): Event-triggered customers unlock emotions
- **Early Game** (10-30min): Core emotions, basic recipes, storage management
- **Mid Game** (30min-2hr): Customer queue, complex recipes, market
- **Late Game** (2-8hr): Transcendent emotions, prestige preparation

## Architecture

```
src/idle_game/
├── app.py                      # Main Textual App
├── models/
│   ├── game_state.py           # Core state with reactive attributes
│   ├── resources.py            # Resource types & calculations
│   ├── customer.py             # Customer generation & logic
│   ├── recipe.py               # Alchemy recipes & mixing
│   └── prestige.py             # Prestige calculations
├── screens/
│   ├── game_screen.py          # Main gameplay view
│   ├── alchemy_screen.py       # Recipe mixing interface
│   ├── customer_screen.py      # Customer queue & service
│   └── prestige_screen.py      # Prestige menu
├── widgets/
│   ├── resource_panel.py       # Resource display
│   ├── customer_queue.py       # Queue widget
│   ├── alchemy_mixer.py        # Mixing interface
│   ├── action_buttons.py       # Click & actions
│   └── stat_display.py         # Stats & meters
├── engine/
│   ├── game_loop.py            # Update tick logic
│   ├── save_manager.py         # Save/load with offline
│   └── calculator.py           # Math helpers
└── data/
    ├── emotions.py             # Emotion definitions
    ├── recipes.py              # Recipe data
    └── customer_templates.py   # Customer types
```

## Implementation Phases

### Phase 1: Core Foundation
**Agent 1: Core Game Engine**
- Game state model with reactive attributes
- Resource system (10 tiers of emotions)
- Production calculation logic
- Save/load manager with offline progression
- Basic game loop with delta-time

**Agent 2: TUI Layout & Screens**
- Main app structure with Textual
- Screen navigation system
- Basic layout (header, main area, footer)
- Resource display widget
- Action button widget
- CSS styling

### Phase 2: Customer System
**Agent 3: Customer System**
- Customer data model
- Tutorial customer events (triggered at resource thresholds)
- Customer generation for queue
- Satisfaction calculation
- Service interface widget

### Phase 3: Advanced Features
**Agent 4: Alchemy System**
- Recipe data structure
- Recipe discovery system
- Mixing interface
- Success/failure calculation
- Crafting widget

**Agent 5: Integration & Testing**
- Integrate all systems
- Storage capacity system
- Purity tracking & degradation
- Shop/upgrade system
- Prestige mechanics
- End-to-end testing
- Bug fixes

## Key Technical Decisions

### State Management
- Use Textual's reactive attributes for all game state
- Centralized GameState model that all widgets observe
- Data binding for automatic UI updates

### Update Loop
- 60 FPS visual updates (animations, progress bars)
- 10 FPS game logic (resource generation, purity decay)
- 1 FPS autosave
- Delta-time calculations for frame-rate independence

### Save Format
```json
{
  "version": 1,
  "timestamp": "2026-01-09T12:00:00",
  "resources": {
    "smiles": {"amount": 1000, "purity": 95.0},
    "joy": {"amount": 100, "purity": 90.0}
  },
  "buildings": {"joy_factory": 5},
  "customers_served": 42,
  "recipes_discovered": ["bittersweet", "courage"],
  "prestige_count": 0,
  "emotional_depth": 0
}
```

### Performance Targets
- Startup time: < 1 second
- UI responsiveness: 60 FPS
- Save time: < 100ms
- Memory usage: < 50MB

## Testing Strategy

1. **Unit Tests**: Models and calculation logic
2. **Widget Tests**: Individual UI components
3. **Integration Tests**: Full gameplay flows
4. **Manual Testing**: Play through tutorial and early game
5. **Verify**: All features from game design docs are present

## Success Criteria

- [ ] All 10 emotion tiers implemented
- [ ] Click and passive generation working
- [ ] Storage capacity with purity system
- [ ] Tutorial customers trigger correctly
- [ ] Customer queue generates and services customers
- [ ] At least 10 recipes working
- [ ] Shop with upgrades functional
- [ ] Prestige system resets and grants ED
- [ ] Save/load with offline progression
- [ ] Game is playable and fun for 30+ minutes
- [ ] No critical bugs or crashes
