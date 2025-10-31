# Implementation Guide - Option 1: Pure Textual Canvas

## Step-by-Step Implementation

### Phase 1: Core Canvas Widget (Day 1)

#### Step 1.1: Create Sprite Data Structures

```python
# src/idle_game/rendering/sprites.py
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from textual.color import Color

@dataclass
class Sprite:
    """Base sprite with position and rendering."""
    x: float
    y: float
    char: str = "█"
    color: Color = Color(255, 255, 255)
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    
    def update(self, dt: float) -> None:
        """Update sprite physics."""
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
    
    @property
    def grid_x(self) -> int:
        """Get integer grid position."""
        return int(round(self.x))
    
    @property
    def grid_y(self) -> int:
        """Get integer grid position."""
        return int(round(self.y))

@dataclass
class FloatingText(Sprite):
    """Floating text that rises and fades."""
    text: str = ""
    lifetime: float = 2.0
    age: float = 0.0
    initial_y: float = 0.0
    
    def __post_init__(self):
        if not self.char:
            self.char = self.text
        self.initial_y = self.y
    
    def update(self, dt: float) -> None:
        """Rise up and fade out."""
        self.age += dt
        self.y = self.initial_y - (self.age * 5)  # Rise at 5 cells/sec
        
        # Fade alpha based on lifetime
        alpha = 1.0 - (self.age / self.lifetime)
        self.color = Color(0, 255, 0, alpha=alpha)
    
    @property
    def is_dead(self) -> bool:
        return self.age >= self.lifetime

@dataclass 
class BouncingNumber(Sprite):
    """Number that bounces with gravity."""
    value: Decimal = Decimal(0)
    lifetime: float = 2.5
    age: float = 0.0
    bounce_energy: float = 0.6
    gravity: float = 30.0
    ground_y: float = 25.0
    
    def update(self, dt: float) -> None:
        """Update with gravity and bouncing."""
        self.age += dt
        
        # Apply gravity
        self.velocity_y += self.gravity * dt
        
        # Update position
        super().update(dt)
        
        # Bounce off ground
        if self.y >= self.ground_y and self.velocity_y > 0:
            self.velocity_y *= -self.bounce_energy
            self.y = self.ground_y
            
            # Stop bouncing if energy too low
            if abs(self.velocity_y) < 0.5:
                self.velocity_y = 0
    
    @property
    def is_dead(self) -> bool:
        return self.age >= self.lifetime
```

#### Step 1.2: Create GameCanvas Widget

```python
# src/idle_game/widgets/game_canvas.py
from textual.widget import Widget
from textual.strip import Strip
from textual.segment import Segment
from textual.reactive import reactive
from typing import TYPE_CHECKING
import random

if TYPE_CHECKING:
    from ..models import GameState, GameNumber

from ..rendering.sprites import Sprite, BouncingNumber, FloatingText

class GameCanvas(Widget):
    """60fps game rendering canvas using Textual line API."""
    
    DEFAULT_CSS = """
    GameCanvas {
        width: 100%;
        height: 100%;
        background: $surface;
        border: solid $primary;
    }
    """
    
    frame_count: reactive[int] = reactive(0)
    
    def __init__(self, game_state: "GameState", **kwargs):
        super().__init__(**kwargs)
        self.game_state = game_state
        self.sprites: list[Sprite] = []
        self.dt = 1/60  # Target 60fps
        
    def on_mount(self) -> None:
        """Start 60fps render loop."""
        self.update_timer = self.set_interval(self.dt, self.update_frame)
    
    def update_frame(self) -> None:
        """Update all sprites and trigger refresh."""
        # Update sprites
        dead_sprites = []
        for sprite in self.sprites:
            sprite.update(self.dt)
            
            if hasattr(sprite, 'is_dead') and sprite.is_dead:
                dead_sprites.append(sprite)
        
        # Remove dead sprites
        for sprite in dead_sprites:
            self.sprites.remove(sprite)
        
        # Increment frame counter (triggers reactive refresh)
        self.frame_count += 1
    
    def render_line(self, y: int) -> Strip:
        """Render a single line of the canvas.
        
        Called by Textual for each visible line at 60fps.
        """
        width = self.size.width
        
        # Create empty line buffer
        chars = [' '] * width
        
        # Render sprites on this line
        for sprite in self.sprites:
            if sprite.grid_y == y:
                x = sprite.grid_x
                if 0 <= x < width:
                    # Handle multi-character sprites (text)
                    text = sprite.char if sprite.char else str(sprite)
                    for i, char in enumerate(text):
                        if 0 <= x + i < width:
                            chars[x + i] = char
        
        # Convert to Strip with segments
        segments = [Segment(''.join(chars))]
        return Strip(segments, width)
    
    def spawn_bouncing_number(self, increment: "GameNumber") -> None:
        """Spawn a bouncing number animation."""
        center_x = self.size.width // 2
        center_y = self.size.height // 2
        
        number = BouncingNumber(
            x=center_x,
            y=center_y,
            char=f"+{increment.format()}",
            value=increment.value,
            velocity_x=random.uniform(-3, 3),
            velocity_y=-15.0,  # Launch upward
            ground_y=center_y + 10
        )
        self.sprites.append(number)
    
    def spawn_floating_text(self, text: str, x: float, y: float) -> None:
        """Spawn floating text that rises."""
        sprite = FloatingText(
            x=x,
            y=y,
            text=text,
            char=text
        )
        self.sprites.append(sprite)
```

### Phase 2: Layout Integration (Day 1-2)

#### Step 2.1: Create Actions Panel

```python
# src/idle_game/widgets/actions_panel.py
from textual.containers import Vertical
from textual.widgets import Static, Button, Label
from textual.reactive import reactive
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import GameState

class ActionsPanel(Vertical):
    """Right panel showing stats and actions."""
    
    DEFAULT_CSS = """
    ActionsPanel {
        width: 100%;
        height: 100%;
        background: $panel;
        border: solid $accent;
        padding: 1;
    }
    
    ActionsPanel .stat-display {
        margin: 1 0;
        text-align: center;
    }
    
    ActionsPanel Button {
        width: 100%;
        margin: 1 0;
    }
    """
    
    counter_display: reactive[str] = reactive("0")
    
    def __init__(self, game_state: "GameState", **kwargs):
        super().__init__(**kwargs)
        self.game_state = game_state
    
    def compose(self):
        yield Static("[bold]Resources[/bold]", classes="stat-display")
        yield Static(self.counter_display, id="counter-value", classes="stat-display")
        yield Button("Click (+10)", id="click-btn", variant="success")
        yield Static("[dim]Auto: +1/sec[/dim]", id="rate-display")
        yield Static("", id="stats-display")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "click-btn":
            self.post_message(self.ClickRequested())
    
    def update_display(self, counter: str) -> None:
        """Update counter display."""
        self.counter_display = counter
        counter_widget = self.query_one("#counter-value", Static)
        counter_widget.update(f"[bold yellow]{counter}[/bold yellow]")
    
    class ClickRequested(Button.Pressed):
        """Message posted when click button pressed."""
        pass
```

#### Step 2.2: Update Main App Layout

```python
# src/idle_game/app.py - Updated compose method
def compose(self) -> ComposeResult:
    yield Header()
    
    # 70/30 split: Canvas on left, Actions on right
    with Horizontal(id="main-layout"):
        yield GameCanvas(self.game_state, id="game-canvas")
        yield ActionsPanel(self.game_state, id="actions-panel")
    
    yield Footer()
```

#### Step 2.3: Add CSS for Layout

```css
/* src/idle_game/styles/main.tcss - Add these rules */

#main-layout {
    width: 100%;
    height: 100%;
}

#game-canvas {
    width: 70%;
}

#actions-panel {
    width: 30%;
}
```

### Phase 3: Game State Integration (Day 2)

#### Step 3.1: Connect Canvas to Game Events

```python
# src/idle_game/app.py - Updated methods

def game_tick(self):
    """Main game loop tick."""
    now = datetime.now()
    increment = self.game_state.update(now)
    
    # Update actions panel
    actions_panel = self.query_one("#actions-panel", ActionsPanel)
    actions_panel.update_display(self.game_state.counter.format())
    
    # Show increment animation on canvas
    if increment.value >= Decimal("0.1"):
        canvas = self.query_one("#game-canvas", GameCanvas)
        canvas.spawn_bouncing_number(increment)

async def on_actions_panel_click_requested(self, event: ActionsPanel.ClickRequested):
    """Handle click from actions panel."""
    increment = self.game_state.click()
    
    # Update display
    actions_panel = self.query_one("#actions-panel", ActionsPanel)
    actions_panel.update_display(self.game_state.counter.format())
    
    # Spawn animation
    canvas = self.query_one("#game-canvas", GameCanvas)
    canvas.spawn_bouncing_number(increment)
```

### Phase 4: Testing and Optimization (Day 3)

#### Step 4.1: Performance Testing

```python
# tests/test_canvas_performance.py
import pytest
from time import perf_counter
from src.idle_game.widgets.game_canvas import GameCanvas
from src.idle_game.models import GameState

def test_render_performance():
    """Test that canvas can render at 60fps."""
    game_state = GameState()
    canvas = GameCanvas(game_state)
    canvas.size = (80, 40)  # Typical terminal size
    
    # Add 100 sprites
    for i in range(100):
        canvas.spawn_bouncing_number(GameNumber(Decimal(i)))
    
    # Measure render time
    start = perf_counter()
    iterations = 1000
    
    for y in range(canvas.size.height):
        for _ in range(iterations):
            canvas.render_line(y)
    
    elapsed = perf_counter() - start
    avg_frame_time = elapsed / iterations
    
    # Should be well under 16.67ms for 60fps
    assert avg_frame_time < 0.01, f"Too slow: {avg_frame_time*1000:.2f}ms per frame"

def test_sprite_cleanup():
    """Test that dead sprites are removed."""
    canvas = GameCanvas(GameState())
    
    # Add sprites with short lifetime
    for _ in range(10):
        sprite = FloatingText(x=0, y=0, text="test", lifetime=0.1)
        canvas.sprites.append(sprite)
    
    assert len(canvas.sprites) == 10
    
    # Update for longer than lifetime
    for _ in range(20):
        canvas.update_frame()
    
    # All sprites should be dead
    assert len(canvas.sprites) == 0
```

#### Step 4.2: Optimization Checklist

- ✅ Use `render_line()` instead of `render()` for line-by-line optimization
- ✅ Cache sprite positions in grid coordinates
- ✅ Remove dead sprites immediately
- ✅ Only render sprites within visible bounds
- ✅ Use reactive variables to trigger minimal refreshes
- ✅ Profile with `py-spy` or `cProfile` to find bottlenecks

### Phase 5: Enhanced Features (Day 4+)

#### Particle System

```python
@dataclass
class Particle(Sprite):
    """Simple particle for effects."""
    lifetime: float = 1.0
    age: float = 0.0
    
    def update(self, dt: float) -> None:
        super().update(dt)
        self.age += dt
        
        # Apply drag
        self.velocity_x *= 0.98
        self.velocity_y *= 0.98
    
    @property
    def is_dead(self) -> bool:
        return self.age >= self.lifetime
```

#### Sprite Animations

```python
from typing import List

@dataclass
class AnimatedSprite(Sprite):
    """Sprite with frame-based animation."""
    frames: List[str] = None
    frame_duration: float = 0.1
    current_frame: int = 0
    frame_timer: float = 0.0
    
    def update(self, dt: float) -> None:
        super().update(dt)
        
        self.frame_timer += dt
        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.char = self.frames[self.current_frame]
```

## Directory Structure

```
src/idle_game/
├── rendering/
│   ├── __init__.py
│   ├── sprites.py          # Sprite data structures
│   └── particles.py        # Particle system
├── widgets/
│   ├── __init__.py
│   ├── game_canvas.py      # Main canvas widget
│   ├── actions_panel.py    # Actions panel widget
│   ├── counter.py          # (existing)
│   └── clicker.py          # (existing)
├── app.py                  # Main app
└── models.py               # (existing)
```

## Testing Strategy

1. Unit tests for sprite physics
2. Performance benchmarks for render_line()
3. Integration tests for game state → canvas events
4. Visual regression tests (screenshot comparison)
5. Memory leak tests (long-running sprite cleanup)

## Performance Targets

- Frame time: < 10ms (60fps = 16.67ms budget)
- Sprite capacity: 500+ simultaneous sprites
- Memory: < 50MB for typical game session
- CPU: < 30% on modern hardware

## Rollout Plan

1. **Week 1**: Core canvas + basic sprites
2. **Week 2**: Layout integration + game state connection
3. **Week 3**: Particle system + advanced animations
4. **Week 4**: Polish, optimization, testing
