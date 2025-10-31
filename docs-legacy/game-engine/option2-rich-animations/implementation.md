# Implementation Guide - Option 2: Rich Animations

## Step-by-Step Implementation

### Phase 1: Animated Widget Foundation (Day 1)

#### Step 1.1: Create Base Animated Number Widget

```python
# src/idle_game/widgets/animated_number.py
from textual.widgets import Static
from textual.reactive import reactive
from textual.app import ComposeResult
from decimal import Decimal
from typing import Callable, Optional

class AnimatedNumber(Static):
    """Floating number with Textual animations."""
    
    DEFAULT_CSS = """
    AnimatedNumber {
        width: auto;
        height: auto;
        color: $success;
        text-style: bold;
        offset-y: 0;
        opacity: 1.0;
    }
    """
    
    opacity: reactive[float] = reactive(1.0)
    offset_y: reactive[int] = reactive(0)
    
    def __init__(
        self, 
        value: Decimal, 
        x: int = 0, 
        y: int = 0,
        on_complete: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.value = value
        self.display_text = f"+{self._format_value(value)}"
        self.on_complete = on_complete
        
        # Set initial position
        self.styles.offset = (x, y)
    
    def _format_value(self, value: Decimal) -> str:
        """Format value for display."""
        if value < 1000:
            return f"{value:.0f}"
        
        suffixes = ['', 'K', 'M', 'B', 'T']
        magnitude = 0
        num = float(value)
        
        while abs(num) >= 1000 and magnitude < len(suffixes) - 1:
            magnitude += 1
            num /= 1000.0
        
        return f"{num:.2f}{suffixes[magnitude]}"
    
    def render(self) -> str:
        return self.display_text
    
    def on_mount(self) -> None:
        """Start animations when mounted."""
        self.animate_float_up()
    
    def animate_float_up(self) -> None:
        """Animate floating up and fading."""
        # Float upward
        self.styles.animate(
            "offset_y",
            value=-15,
            duration=2.0,
            easing="out_cubic"
        )
        
        # Fade out
        self.styles.animate(
            "opacity",
            value=0.0,
            duration=2.0,
            easing="linear",
            on_complete=self._on_animation_complete
        )
    
    def _on_animation_complete(self) -> None:
        """Called when animation finishes."""
        if self.on_complete:
            self.on_complete()
        self.remove()
```

#### Step 1.2: Create Bouncing Number Variant

```python
# src/idle_game/widgets/bouncing_number.py
from textual.widgets import Static
from textual.reactive import reactive
from decimal import Decimal
from typing import Optional, Callable

class BouncingNumber(Static):
    """Number that bounces with elastic effect."""
    
    DEFAULT_CSS = """
    BouncingNumber {
        width: auto;
        height: auto;
        color: $warning;
        text-style: bold;
        offset-y: 0;
        opacity: 1.0;
    }
    """
    
    offset_y: reactive[int] = reactive(-5)  # Start above
    
    def __init__(
        self,
        value: Decimal,
        x: int = 0,
        y: int = 0,
        on_complete: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.value = value
        self.display_text = f"+{value}"
        self.on_complete = on_complete
        self.styles.offset = (x, y)
    
    def render(self) -> str:
        return self.display_text
    
    def on_mount(self) -> None:
        """Animate bounce sequence."""
        self.animate_bounce_sequence()
    
    async def animate_bounce_sequence(self) -> None:
        """Chain bounce animations."""
        # Bounce down
        await self.styles.animate(
            "offset_y",
            value=0,
            duration=0.6,
            easing="in_out_bounce"
        )
        
        # Hold
        await asyncio.sleep(0.5)
        
        # Float up and fade
        self.styles.animate(
            "offset_y",
            value=-10,
            duration=1.0,
            easing="out_cubic"
        )
        
        await self.styles.animate(
            "opacity",
            value=0.0,
            duration=1.0,
            on_complete=self._cleanup
        )
    
    def _cleanup(self) -> None:
        if self.on_complete:
            self.on_complete()
        self.remove()
```

### Phase 2: Rich Game View (Day 1-2)

#### Step 2.1: Create Game View Widget

```python
# src/idle_game/widgets/rich_game_view.py
from textual.widget import Widget
from textual.reactive import reactive
from textual.containers import Container
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import GameState, GameNumber

from .animated_number import AnimatedNumber
from .bouncing_number import BouncingNumber

class RichGameView(Container):
    """Game view using Rich renderables."""
    
    DEFAULT_CSS = """
    RichGameView {
        width: 100%;
        height: 100%;
        background: $surface;
        border: solid $primary;
        padding: 1;
        layers: base overlay;
    }
    
    RichGameView > Static {
        layer: base;
    }
    
    RichGameView > AnimatedNumber,
    RichGameView > BouncingNumber {
        layer: overlay;
    }
    
    #main-counter {
        width: 100%;
        height: 100%;
        content-align: center middle;
    }
    """
    
    counter_value: reactive[str] = reactive("0")
    
    def __init__(self, game_state: "GameState", **kwargs):
        super().__init__(**kwargs)
        self.game_state = game_state
        self.animation_count = 0
        self.max_animations = 20  # Limit concurrent animations
    
    def compose(self):
        """Compose the game view."""
        from textual.widgets import Static
        
        # Main counter display
        yield Static(id="main-counter")
    
    def on_mount(self) -> None:
        """Update counter display on mount."""
        self.update_counter_display()
    
    def update_counter_display(self) -> None:
        """Update the main counter display."""
        from textual.widgets import Static
        
        counter = self.query_one("#main-counter", Static)
        
        # Create Rich panel with counter
        panel = Panel(
            Align.center(
                Text(
                    self.game_state.counter.format(),
                    style="bold yellow",
                    justify="center"
                ),
                vertical="middle"
            ),
            title="Resources",
            border_style="green",
            padding=(1, 2)
        )
        
        counter.update(panel)
    
    def spawn_animated_number(self, increment: "GameNumber") -> None:
        """Spawn a floating animated number."""
        if self.animation_count >= self.max_animations:
            return  # Skip if too many animations
        
        # Calculate center position
        center_x = self.size.width // 2
        center_y = self.size.height // 2
        
        # Create animated number
        anim = AnimatedNumber(
            value=increment.value,
            x=center_x - 5,  # Offset left
            y=center_y,
            on_complete=self._on_animation_complete
        )
        
        self.animation_count += 1
        self.mount(anim)
    
    def spawn_bouncing_number(self, increment: "GameNumber") -> None:
        """Spawn a bouncing number."""
        if self.animation_count >= self.max_animations:
            return
        
        center_x = self.size.width // 2
        center_y = self.size.height // 2
        
        bounce = BouncingNumber(
            value=increment.value,
            x=center_x - 5,
            y=center_y - 5,
            on_complete=self._on_animation_complete
        )
        
        self.animation_count += 1
        self.mount(bounce)
    
    def _on_animation_complete(self) -> None:
        """Track animation cleanup."""
        self.animation_count = max(0, self.animation_count - 1)
```

### Phase 3: Layout Integration (Day 2)

#### Step 3.1: Update Main App

```python
# src/idle_game/app.py - Updated imports and compose

from .widgets.rich_game_view import RichGameView
from .widgets.actions_panel import ActionsPanel  # From Option 1

def compose(self) -> ComposeResult:
    yield Header()
    
    with Horizontal(id="main-layout"):
        yield RichGameView(self.game_state, id="game-view")
        yield ActionsPanel(self.game_state, id="actions-panel")
    
    yield Footer()
```

#### Step 3.2: Connect Game Events

```python
# src/idle_game/app.py - Updated game_tick

def game_tick(self):
    """Main game loop tick."""
    now = datetime.now()
    increment = self.game_state.update(now)
    
    # Update game view counter
    game_view = self.query_one("#game-view", RichGameView)
    game_view.update_counter_display()
    
    # Update actions panel
    actions_panel = self.query_one("#actions-panel", ActionsPanel)
    actions_panel.update_display(self.game_state.counter.format())
    
    # Spawn animation for significant increments
    if increment.value >= Decimal("0.1"):
        game_view.spawn_animated_number(increment)

async def on_actions_panel_click_requested(self, event):
    """Handle manual click."""
    increment = self.game_state.click()
    
    # Update displays
    game_view = self.query_one("#game-view", RichGameView)
    game_view.update_counter_display()
    
    actions_panel = self.query_one("#actions-panel", ActionsPanel)
    actions_panel.update_display(self.game_state.counter.format())
    
    # Use bouncing animation for clicks
    game_view.spawn_bouncing_number(increment)
```

### Phase 4: Advanced Effects (Day 3)

#### Step 4.1: Particle System

```python
# src/idle_game/widgets/particles.py
from textual.widgets import Static
from textual.reactive import reactive
import random

class ParticleEffect(Static):
    """Simple particle burst effect."""
    
    DEFAULT_CSS = """
    ParticleEffect {
        width: auto;
        height: auto;
        opacity: 1.0;
        color: $accent;
    }
    """
    
    def __init__(self, x: int, y: int, count: int = 5, **kwargs):
        super().__init__(**kwargs)
        self.particle_chars = ['*', '+', '·', '○', '×']
        self.particle_display = ''.join(
            random.choice(self.particle_chars) 
            for _ in range(count)
        )
        self.styles.offset = (x, y)
    
    def render(self) -> str:
        return self.particle_display
    
    def on_mount(self) -> None:
        """Animate particles."""
        # Spread outward
        self.styles.animate(
            "offset_x",
            value=self.styles.offset.x + random.randint(-3, 3),
            duration=0.5,
            easing="out_cubic"
        )
        
        # Float up and fade
        self.styles.animate(
            "offset_y",
            value=self.styles.offset.y - random.randint(3, 8),
            duration=1.0,
            easing="out_cubic"
        )
        
        self.styles.animate(
            "opacity",
            value=0.0,
            duration=0.8,
            on_complete=self.remove
        )
```

#### Step 4.2: Combo System

```python
# src/idle_game/widgets/combo_display.py
from textual.widgets import Static
from decimal import Decimal

class ComboDisplay(Static):
    """Shows combo multiplier with scaling effect."""
    
    DEFAULT_CSS = """
    ComboDisplay {
        width: auto;
        height: auto;
        color: $warning;
        text-style: bold;
    }
    """
    
    def __init__(self, combo: int, x: int, y: int, **kwargs):
        super().__init__(**kwargs)
        self.combo = combo
        self.display_text = f"x{combo} COMBO!"
        self.styles.offset = (x, y)
    
    def render(self) -> str:
        return self.display_text
    
    def on_mount(self) -> None:
        """Pulse animation."""
        self.animate_pulse()
    
    async def animate_pulse(self) -> None:
        """Pulse in and out."""
        # Scale up
        await self.styles.animate(
            "text_opacity",
            value=1.0,
            duration=0.2,
            easing="elastic_out"
        )
        
        # Hold
        await asyncio.sleep(1.0)
        
        # Fade out
        await self.styles.animate(
            "opacity",
            value=0.0,
            duration=0.5,
            on_complete=self.remove
        )
```

### Phase 5: Performance Optimization (Day 4)

#### Step 5.1: Animation Pooling

```python
# src/idle_game/rendering/animation_pool.py
from typing import List, Type, TypeVar
from textual.widgets import Static

T = TypeVar('T', bound=Static)

class AnimationPool:
    """Pool of reusable animation widgets."""
    
    def __init__(self, widget_class: Type[T], pool_size: int = 20):
        self.widget_class = widget_class
        self.pool: List[T] = []
        self.active: List[T] = []
        self.pool_size = pool_size
    
    def acquire(self, *args, **kwargs) -> T:
        """Get a widget from pool or create new."""
        if self.pool:
            widget = self.pool.pop()
            widget.reset(*args, **kwargs)
            self.active.append(widget)
            return widget
        
        if len(self.active) < self.pool_size:
            widget = self.widget_class(*args, **kwargs)
            self.active.append(widget)
            return widget
        
        return None  # Pool exhausted
    
    def release(self, widget: T) -> None:
        """Return widget to pool."""
        if widget in self.active:
            self.active.remove(widget)
            self.pool.append(widget)
```

#### Step 5.2: Batched Updates

```python
# src/idle_game/widgets/rich_game_view.py - Add batching

class RichGameView(Container):
    """Game view with batched animations."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pending_animations = []
        self.batch_timer = None
    
    def spawn_animated_number(self, increment: GameNumber) -> None:
        """Queue animation for batching."""
        self.pending_animations.append(increment)
        
        if not self.batch_timer:
            self.batch_timer = self.set_timer(0.1, self._process_batch)
    
    def _process_batch(self) -> None:
        """Process queued animations."""
        # Take up to 5 animations at a time
        batch = self.pending_animations[:5]
        self.pending_animations = self.pending_animations[5:]
        
        for i, increment in enumerate(batch):
            # Offset each animation slightly
            anim = AnimatedNumber(
                value=increment.value,
                x=self.size.width // 2 + (i * 3),
                y=self.size.height // 2
            )
            self.mount(anim)
        
        # Schedule next batch if needed
        if self.pending_animations:
            self.batch_timer = self.set_timer(0.1, self._process_batch)
        else:
            self.batch_timer = None
```

## Testing

```python
# tests/test_rich_animations.py
import pytest
from textual.pilot import Pilot
from src.idle_game.app import IdleGame

async def test_animated_number_spawns():
    """Test that animations spawn on increment."""
    async with IdleGame().run_test() as pilot:
        # Trigger click
        await pilot.click("#click-btn")
        
        # Wait for animation
        await pilot.pause(0.1)
        
        # Check animation was spawned
        game_view = pilot.app.query_one(RichGameView)
        assert game_view.animation_count > 0

async def test_animation_cleanup():
    """Test animations are cleaned up."""
    async with IdleGame().run_test() as pilot:
        game_view = pilot.app.query_one(RichGameView)
        
        # Spawn animation
        game_view.spawn_animated_number(GameNumber(Decimal(10)))
        
        # Wait for completion
        await pilot.pause(3.0)
        
        # Should be cleaned up
        assert game_view.animation_count == 0
```

## Performance Tips

1. Limit concurrent animations to 10-20
2. Use `on_complete` callbacks for cleanup
3. Batch similar animations together
4. Prefer CSS animations over Python updates
5. Use layers to avoid full redraws
6. Profile with `textual run --dev` to see repaints

## Directory Structure

```
src/idle_game/
├── widgets/
│   ├── animated_number.py
│   ├── bouncing_number.py
│   ├── particles.py
│   ├── combo_display.py
│   └── rich_game_view.py
├── rendering/
│   └── animation_pool.py
└── app.py
```
