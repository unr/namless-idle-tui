# Implementation Guide - Option 3: Async Game Loop

## Overview

This is the most complex but most powerful option. Only choose this if you need professional-grade game engine capabilities.

## Phase 1: Core Engine (Week 1)

### Step 1: Entity Component System

```python
# src/idle_game/engine/components.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Transform:
    """Position and velocity component."""
    x: float = 0.0
    y: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    ax: float = 0.0
    ay: float = 0.0
    prev_x: float = 0.0
    prev_y: float = 0.0
    
    def update(self, dt: float) -> None:
        self.prev_x = self.x
        self.prev_y = self.y
        self.vx += self.ax * dt
        self.vy += self.ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
    
    def lerp_pos(self, alpha: float) -> tuple[float, float]:
        """Linear interpolation between frames."""
        x = self.prev_x + (self.x - self.prev_x) * alpha
        y = self.prev_y + (self.y - self.prev_y) * alpha
        return (x, y)

# More components in the same file...
```

### Step 2: Game Loop

```python
# src/idle_game/engine/game_loop.py
import asyncio
from time import perf_counter
from typing import List, Optional
from .entities import Entity
from .renderer import DoubleBuffer

class GameLoop:
    """Fixed timestep game loop."""
    
    def __init__(self, fps: int = 60):
        self.fps = fps
        self.dt = 1.0 / fps
        self.entities: List[Entity] = []
        self.renderer = DoubleBuffer()
        self.running = False
        
    async def run(self) -> None:
        """Main game loop."""
        self.running = True
        last_time = perf_counter()
        accumulator = 0.0
        
        while self.running:
            current = perf_counter()
            frame_time = min(current - last_time, 0.25)
            last_time = current
            accumulator += frame_time
            
            # Fixed timestep updates
            while accumulator >= self.dt:
                self.update(self.dt)
                accumulator -= self.dt
            
            # Render with interpolation
            alpha = accumulator / self.dt
            self.render(alpha)
            
            await asyncio.sleep(0.001)
    
    def update(self, dt: float) -> None:
        """Update all entities."""
        for entity in self.entities[:]:
            entity.update(dt)
            if entity.is_dead:
                self.entities.remove(entity)
    
    def render(self, alpha: float) -> None:
        """Render to buffer."""
        self.renderer.clear()
        for entity in self.entities:
            entity.render(self.renderer, alpha)
        self.renderer.swap()
```

## Phase 2: Rendering (Week 2)

### Step 1: Double Buffer

```python
# src/idle_game/engine/renderer.py
from typing import List

class DoubleBuffer:
    """ASCII double buffer."""
    
    def __init__(self, width: int = 80, height: int = 40):
        self.width = width
        self.height = height
        self.front = [[' '] * width for _ in range(height)]
        self.back = [[' '] * width for _ in range(height)]
    
    def clear(self) -> None:
        for y in range(self.height):
            for x in range(self.width):
                self.back[y][x] = ' '
    
    def set(self, x: int, y: int, char: str) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.back[int(y)][int(x)] = char
    
    def text(self, x: int, y: int, text: str) -> None:
        for i, c in enumerate(text):
            self.set(x + i, y, c)
    
    def swap(self) -> None:
        self.front, self.back = self.back, self.front
    
    def get_line(self, y: int) -> str:
        return ''.join(self.front[y]) if 0 <= y < self.height else ''
```

## Phase 3: Integration (Week 2-3)

### Widget Integration

```python
# src/idle_game/widgets/game_engine_view.py
from textual.widget import Widget
from textual.strip import Strip
from textual.segment import Segment
from ..engine.game_loop import GameLoop
import asyncio

class GameEngineView(Widget):
    """Game engine display widget."""
    
    def __init__(self, game_state, **kwargs):
        super().__init__(**kwargs)
        self.game_state = game_state
        self.engine = GameLoop()
        self.task = None
    
    async def on_mount(self) -> None:
        self.engine.renderer.width = self.size.width
        self.engine.renderer.height = self.size.height
        self.task = asyncio.create_task(self.engine.run())
        self.set_interval(1/60, self.refresh)
    
    async def on_unmount(self) -> None:
        self.engine.running = False
        if self.task:
            await self.task
    
    def render_line(self, y: int) -> Strip:
        line = self.engine.renderer.get_line(y)
        return Strip([Segment(line)], len(line))
```

## Performance Optimization

### Frame Time Budget

```
Total: 16.67ms (60fps)
├─ Update: 5ms
├─ Physics: 3ms
├─ Render: 5ms
└─ Buffer: 2ms
```

### Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Run game loop
engine.update(dt)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

## Testing

```python
# tests/test_game_loop.py
import pytest
from src.idle_game.engine.game_loop import GameLoop

def test_fixed_timestep():
    """Test loop maintains fixed timestep."""
    loop = GameLoop(fps=60)
    assert loop.dt == pytest.approx(1/60)

@pytest.mark.asyncio
async def test_entity_cleanup():
    """Test dead entities are removed."""
    loop = GameLoop()
    
    # Add entity with 0.1s lifetime
    entity = FloatingNumber(...)
    entity.lifetime.duration = 0.1
    loop.entities.append(entity)
    
    # Run for 0.2s
    for _ in range(12):  # 60fps * 0.2s
        loop.update(loop.dt)
    
    assert len(loop.entities) == 0
```

## Directory Structure

```
src/idle_game/
├── engine/
│   ├── __init__.py
│   ├── game_loop.py
│   ├── components.py
│   ├── entities.py
│   ├── physics.py
│   └── renderer.py
├── widgets/
│   └── game_engine_view.py
└── app.py
```

## When NOT to Use This

This approach is overkill if:
- You only need simple floating text
- No complex physics required
- Team unfamiliar with game engines
- Tight deadlines
- Simple incremental game mechanics

Consider Option 1 or 2 for simpler use cases.
