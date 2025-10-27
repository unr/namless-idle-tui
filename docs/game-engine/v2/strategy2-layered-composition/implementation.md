# Implementation Guide - Strategy 2: Layered Composition

## Overview

Implementing a layered rendering system with parallax, state management, and compositin. Time: 3-4 days.

## Phase 1: Core Layer System (Day 1-2)

### Step 1: Layer Data Structures

```python
# src/idle_game/rendering/layer.py
from dataclasses import dataclass, field
from typing import List, Callable, Optional
from enum import IntEnum

class LayerID(IntEnum):
    """Standard layer IDs."""
    BACKGROUND = 0
    MIDGROUND = 1  
    FOREGROUND = 2
    UI = 3

@dataclass
class Layer:
    """Rendering layer."""
    
    id: LayerID
    name: str
    z_order: int
    visible: bool = True
    opacity: float = 1.0
    parallax_factor: float = 1.0
    sprites: List = field(default_factory=list)
    
    def update(self, dt: float) -> None:
        dead = []
        for sprite in self.sprites:
            sprite.update(dt)
            if hasattr(sprite, 'is_complete') and sprite.is_complete:
                dead.append(sprite)
        
        for s in dead:
            self.sprites.remove(s)
    
    def clear(self) -> None:
        self.sprites.clear()
    
    def add_sprite(self, sprite) -> None:
        self.sprites.append(sprite)
```

### Step 2: Compositor

```python
# src/idle_game/rendering/compositor.py
from typing import Dict, List
from .layer import Layer, LayerID

class LayerCompositor:
    """Composites multiple layers."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.layers: Dict[LayerID, Layer] = {}
        self._init_layers()
    
    def _init_layers(self) -> None:
        for layer_id in LayerID:
            self.layers[layer_id] = Layer(
                id=layer_id,
                name=layer_id.name,
                z_order=layer_id.value
            )
    
    def composite(self) -> List[List[str]]:
        """Composite all layers into final image."""
        final = [[' ' for _ in range(self.width)] 
                 for _ in range(self.height)]
        
        # Render in z-order
        for layer in sorted(self.layers.values(), 
                           key=lambda l: l.z_order):
            if not layer.visible:
                continue
            
            self._render_layer(final, layer)
        
        return final
    
    def _render_layer(self, buffer: List[List[str]], layer: Layer) -> None:
        """Render layer onto buffer."""
        for sprite in layer.sprites:
            self._draw_sprite(buffer, sprite, layer.opacity)
    
    def _draw_sprite(
        self, 
        buffer: List[List[str]], 
        sprite, 
        opacity: float
    ) -> None:
        """Draw sprite to buffer."""
        lines = sprite.current_image.strip().split('\n')
        
        for y_off, line in enumerate(lines):
            y = sprite.y + y_off
            if not (0 <= y < len(buffer)):
                continue
            
            for x_off, char in enumerate(line):
                x = sprite.x + x_off
                if not (0 <= x < len(buffer[0])):
                    continue
                
                # Simple transparency - space is transparent
                if char != ' ':
                    buffer[y][x] = char
```

## Phase 2: Canvas Implementation (Day 2-3)

### Step 1: Layered Canvas Widget

```python
# src/idle_game/widgets/layered_canvas.py
from textual.widget import Widget
from textual.strip import Strip
from textual.segment import Segment
from ..rendering.compositor import LayerCompositor, LayerID
from ..sprites.animated_sprite import AnimatedSprite

class LayeredCanvas(Widget):
    """Multi-layer sprite canvas."""
    
    DEFAULT_CSS = """
    LayeredCanvas {
        width: 100%;
        height: 100%;
        background: $surface;
        border: solid $primary;
    }
    """
    
    def __init__(self, game_state, **kwargs):
        super().__init__(**kwargs)
        self.game_state = game_state
        self.compositor = None
        self.update_rate = 15
    
    def on_mount(self) -> None:
        self.compositor = LayerCompositor(
            width=self.size.width,
            height=self.size.height
        )
        
        self.setup_layers()
        self.set_interval(1.0 / self.update_rate, self.update_all)
    
    def setup_layers(self) -> None:
        """Configure layer properties."""
        # Background - slow parallax
        self.compositor.layers[LayerID.BACKGROUND].parallax_factor = 0.3
        
        # Midground - medium parallax
        self.compositor.layers[LayerID.MIDGROUND].parallax_factor = 0.6
        
        # Foreground - full speed
        self.compositor.layers[LayerID.FOREGROUND].parallax_factor = 1.0
        
        # UI - no parallax
        self.compositor.layers[LayerID.UI].parallax_factor = 0.0
        
        # Populate initial sprites
        self.populate_scene()
    
    def populate_scene(self) -> None:
        """Add initial sprites to layers."""
        # Background terrain
        bg = self.compositor.layers[LayerID.BACKGROUND]
        terrain = AnimatedSprite(
            frames=["▓" * self.size.width],
            x=0,
            y=self.size.height - 1,
            fps=1,
            loop=True
        )
        bg.add_sprite(terrain)
        
        # Foreground character
        fg = self.compositor.layers[LayerID.FOREGROUND]
        char = AnimatedSprite(
            frames=CHARACTER_FRAMES,
            x=self.size.width // 2,
            y=self.size.height // 2,
            fps=4,
            loop=True
        )
        fg.add_sprite(char)
    
    def update_all(self) -> None:
        """Update all layers."""
        dt = 1.0 / self.update_rate
        
        for layer in self.compositor.layers.values():
            layer.update(dt)
        
        self.refresh()
    
    def render_line(self, y: int) -> Strip:
        """Render composited line."""
        comp = self.compositor.composite()
        
        if 0 <= y < len(comp):
            line = ''.join(comp[y])
            return Strip([Segment(line)], len(line))
        
        return Strip([Segment(' ' * self.size.width)])
    
    def spawn_on_layer(
        self, 
        layer_id: LayerID,
        template: str,
        x: int,
        y: int,
        **kwargs
    ) -> None:
        """Spawn sprite on specific layer."""
        sprite = AnimatedSprite(
            frames=SPRITE_TEMPLATES[template],
            x=x,
            y=y,
            **kwargs
        )
        self.compositor.layers[layer_id].add_sprite(sprite)
```

### Step 2: Integrate with Game

```python
# src/idle_game/app.py additions

def compose(self) -> ComposeResult:
    yield Header()
    
    with Horizontal(id="main-layout"):
        yield LayeredCanvas(self.game_state, id="layered-canvas")
        yield ActionsPanel(self.game_state, id="actions-panel")
    
    yield Footer()

def on_counter_increment(self, increment):
    """Spawn layered effects."""
    canvas = self.query_one("#layered-canvas", LayeredCanvas)
    
    # Effect on midground
    canvas.spawn_on_layer(
        LayerID.MIDGROUND,
        'sparkle',
        x=canvas.size.width // 2,
        y=canvas.size.height // 2,
        fps=15,
        loop=False
    )
    
    # Number on UI layer
    canvas.spawn_on_layer(
        LayerID.UI,
        f'+{increment.format()}',
        x=canvas.size.width // 2 + 5,
        y=5,
        fps=1,
        loop=False
    )
```

## Phase 3: Advanced Features (Day 3-4)

### Parallax Camera

```python
# src/idle_game/rendering/camera.py

class ParallaxCamera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
    
    def scroll(self, dx: float, dy: float) -> None:
        self.x += dx
        self.y += dy
    
    def apply_parallax(
        self, 
        sprite_x: int, 
        parallax_factor: float
    ) -> int:
        """Apply parallax offset to sprite position."""
        return int(sprite_x - (self.x * parallax_factor))

# In LayeredCanvas:
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.camera = ParallaxCamera()

def _draw_with_parallax(self, sprite, layer):
    """Draw sprite with parallax applied."""
    parallax_x = self.camera.apply_parallax(
        sprite.x, 
        layer.parallax_factor
    )
    # Use parallax_x instead of sprite.x for rendering
```

### Layer Transitions

```python
# src/idle_game/rendering/transitions.py

class LayerTransition:
    """Animate layer properties."""
    
    @staticmethod
    async def fade_out(layer: Layer, duration: float = 1.0):
        """Fade layer out."""
        steps = int(duration * 20)  # 20 steps per second
        
        for i in range(steps, -1, -1):
            layer.opacity = i / steps
            await asyncio.sleep(duration / steps)
        
        layer.visible = False
    
    @staticmethod  
    async def fade_in(layer: Layer, duration: float = 1.0):
        """Fade layer in."""
        layer.visible = True
        steps = int(duration * 20)
        
        for i in range(steps + 1):
            layer.opacity = i / steps
            await asyncio.sleep(duration / steps)
```

## Testing

```python
# tests/test_layered_canvas.py

def test_layer_z_order():
    """Test layers render in correct order."""
    compositor = LayerCompositor(10, 10)
    
    # Add sprite to background
    bg_sprite = AnimatedSprite(frames=["B"], x=0, y=0)
    compositor.layers[LayerID.BACKGROUND].add_sprite(bg_sprite)
    
    # Add sprite to foreground at same position
    fg_sprite = AnimatedSprite(frames=["F"], x=0, y=0)
    compositor.layers[LayerID.FOREGROUND].add_sprite(fg_sprite)
    
    # Composite
    result = compositor.composite()
    
    # Foreground should be on top
    assert result[0][0] == "F"

def test_layer_visibility():
    """Test hiding layers."""
    compositor = LayerCompositor(10, 10)
    
    layer = compositor.layers[LayerID.BACKGROUND]
    sprite = AnimatedSprite(frames=["X"], x=0, y=0)
    layer.add_sprite(sprite)
    
    # Visible
    result = compositor.composite()
    assert result[0][0] == "X"
    
    # Hidden
    layer.visible = False
    result = compositor.composite()
    assert result[0][0] == " "
```

## Directory Structure

```
src/idle_game/
├── rendering/
│   ├── __init__.py
│   ├── layer.py
│   ├── compositor.py
│   ├── camera.py
│   └── transitions.py
├── widgets/
│   └── layered_canvas.py
└── ...
```

## Best Practices

1. Use BACKGROUND for static scenery
2. Use MIDGROUND for effects/particles  
3. Use FOREGROUND for characters/entities
4. Use UI for HUD elements
5. Limit sprites per layer to 20-30
6. Cache background layers when static
7. Use layer opacity for fade effects
8. Test layer order carefully
