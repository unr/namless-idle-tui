# Game Engine Architecture Documentation

## Overview

This directory contains comprehensive documentation for three different approaches to implementing a 60fps game rendering engine within your Textual-based incremental game.

## Quick Navigation

- **[COMPARISON.md](./COMPARISON.md)** - Detailed comparison matrix and recommendation ⭐ START HERE
- **[option1-textual-canvas/](./option1-textual-canvas/)** - Pure Textual line API approach (RECOMMENDED)
- **[option2-rich-animations/](./option2-rich-animations/)** - Rich renderables with Textual animations
- **[option3-async-gameloop/](./option3-async-gameloop/)** - Custom async game loop with physics

## TL;DR

**Use Option 1** - Pure Textual Canvas Widget with `render_line()` API.

It provides:
- 60fps stable rendering
- Handles 1000+ sprites
- Native Textual integration
- Future-proof architecture
- 4-day implementation

## Requirements

Your game needs:
- ✅ 60fps rendering in TUI app
- ✅ Bouncing number animations when counter increments
- ✅ 70/30 split layout (game screen 70%, actions panel 30%)
- ✅ ASCII/Unicode visual elements
- ✅ Integration with existing GameState
- ✅ Scalable for future sprite/particle systems

## The Three Options

### Option 1: Pure Textual Canvas Widget ⭐ RECOMMENDED

Uses Textual's `render_line()` API for high-performance sprite rendering.

**Pros:** Best performance, native integration, full control  
**Cons:** Manual sprite system implementation  
**Time:** 4 days  
**Best for:** Your exact use case

[Read full documentation →](./option1-textual-canvas/README.md)

### Option 2: Textual + Rich Animations

Uses Textual's animation system with Rich renderables.

**Pros:** Easiest to implement, built-in easing  
**Cons:** Performance degrades with 50+ animations  
**Time:** 1.5 days  
**Best for:** Quick prototypes, simple UI animations

[Read full documentation →](./option2-rich-animations/README.md)

### Option 3: Async Game Loop

Professional game engine with fixed timestep and double buffering.

**Pros:** Maximum control, complex physics support  
**Cons:** Overkill for incremental game  
**Time:** 2 weeks  
**Best for:** Complex physics-based games

[Read full documentation →](./option3-async-gameloop/README.md)

## Comparison at a Glance

| Metric | Option 1 | Option 2 | Option 3 |
|--------|----------|----------|----------|
| Performance | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Simplicity | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Time to implement | 4 days | 1.5 days | 2 weeks |
| Max sprites @ 60fps | 1000+ | ~100 | 800+ |
| Native integration | Yes | Yes | Partial |

[See detailed comparison →](./COMPARISON.md)

## Getting Started

### Step 1: Read the Comparison

Start with [COMPARISON.md](./COMPARISON.md) to understand the trade-offs.

### Step 2: Choose Your Option

Based on your needs:
- **Performance + scalability** → Option 1
- **Quick prototype** → Option 2  
- **Complex physics game** → Option 3

### Step 3: Follow Implementation Guide

Each option has a detailed implementation guide:
- [Option 1 Implementation](./option1-textual-canvas/implementation.md)
- [Option 2 Implementation](./option2-rich-animations/implementation.md)
- [Option 3 Implementation](./option3-async-gameloop/implementation.md)

## Architecture Preview

### 70/30 Split Layout

All options use the same layout structure:

```python
from textual.app import App, ComposeResult
from textual.containers import Horizontal

class IdleGame(App):
    def compose(self) -> ComposeResult:
        with Horizontal():
            # 70% - Game rendering area
            yield GameCanvas(self.game_state)  # or RichGameView, or GameEngineView
            
            # 30% - Actions panel
            yield ActionsPanel(self.game_state)
```

### Game State Integration

All options integrate with your existing `GameState`:

```python
def game_tick(self):
    """Main game loop tick."""
    now = datetime.now()
    increment = self.game_state.update(now)
    
    # Update game view
    game_view = self.query_one(GameCanvas)  # or RichGameView, etc.
    game_view.update_counter_display()
    
    # Spawn animation on increment
    if increment.value >= Decimal("0.1"):
        game_view.spawn_bouncing_number(increment)
```

## Common Patterns

### Bouncing Number Animation

All three options implement this core feature:

**Option 1:**
```python
class BouncingNumber(Sprite):
    def update(self, dt: float):
        self.velocity_y += gravity * dt
        self.y += self.velocity_y * dt
        if self.y >= ground:
            self.velocity_y *= -bounce_factor
```

**Option 2:**
```python
class BouncingNumber(Static):
    def on_mount(self):
        self.styles.animate("offset_y", value=0, easing="in_out_bounce")
```

**Option 3:**
```python
class BouncingNumber(Entity):
    def __init__(self):
        self.transform = Transform(y=0, vy=-15)
        self.use_gravity = True
```

## Performance Targets

All implementations target:
- **Frame rate:** 60fps (16.67ms per frame)
- **Sprites:** 500+ simultaneous
- **Memory:** < 50MB
- **CPU:** < 30% on modern hardware

## Testing Strategy

Each option includes:
- Unit tests for sprite/entity systems
- Performance benchmarks
- Integration tests with GameState
- Visual regression tests

## Migration Between Options

If you need to switch:
- Option 2 → Option 1: 2 days
- Option 1 → Option 3: 3 days
- Option 2 → Option 3: 1 week

## Technology Stack

All options use:
- Python 3.11+
- Textual 0.89+
- Type hints throughout
- Async/await patterns
- Decimal for game numbers

No additional dependencies required.

## Questions?

Check the detailed docs for each option:
1. [Pure Textual Canvas](./option1-textual-canvas/) - Full control, best performance
2. [Rich Animations](./option2-rich-animations/) - Quick and easy
3. [Async Game Loop](./option3-async-gameloop/) - Professional game engine

## Next Steps

1. ✅ Read [COMPARISON.md](./COMPARISON.md)
2. ✅ Choose your option
3. ✅ Follow the implementation guide
4. ✅ Start with basic bouncing number
5. ✅ Expand to particles and effects
6. ✅ Optimize and polish

**Recommended path:** Start with Option 1 for the best balance of performance and maintainability.
