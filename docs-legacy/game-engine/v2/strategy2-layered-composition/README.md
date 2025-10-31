# Strategy 2: Layered Composition System

## Overview

A multi-layer rendering system where sprites and effects are organized into distinct layers (background, midground, foreground, UI). Each layer can have its own update logic, blend modes, and parallax scrolling. Think of it like transparent sheets stacked on top of each other, each containing different visual elements.

This approach is ideal for games with **complex scenes**, **depth perception**, and **environmental effects**.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    IdleGame (App)                        │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Horizontal Container (70/30)               │ │
│  │  ┌──────────────────┐  ┌──────────────────────┐   │ │
│  │  │ LayeredCanvas    │  │  ActionsPanel        │   │ │
│  │  │  (70% width)     │  │  (30% width)         │   │ │
│  │  │                  │  │                      │   │ │
│  │  │ ┌──────────────┐ │  │  - Stats             │   │ │
│  │  │ │Layer 3 (UI)  │ │  │  - Actions           │   │ │
│  │  │ │  [Score]     │ │  │  - Upgrades          │   │ │
│  │  │ ├──────────────┤ │  │                      │   │ │
│  │  │ │Layer 2 (FG)  │ │  │                      │   │ │
│  │  │ │  🧙 (char)   │ │  │                      │   │ │
│  │  │ ├──────────────┤ │  │                      │   │ │
│  │  │ │Layer 1 (MG)  │ │  │                      │   │ │
│  │  │ │  ✨ effects  │ │  │                      │   │ │
│  │  │ ├──────────────┤ │  │                      │   │ │
│  │  │ │Layer 0 (BG)  │ │  │                      │   │ │
│  │  │ │  ▓▓ terrain  │ │  │                      │   │ │
│  │  │ └──────────────┘ │  │                      │   │ │
│  │  │                  │  │                      │   │ │
│  │  │  Composite @15fps│  │                      │   │ │
│  │  └──────────────────┘  └──────────────────────┘   │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## Key Concepts

### 1. Layer System

Each layer has a z-order and independent rendering:

```python
from dataclasses import dataclass, field
from typing import List, Dict
from enum import IntEnum

class LayerID(IntEnum):
    """Pre-defined layer IDs."""
    BACKGROUND = 0
    MIDGROUND = 1
    FOREGROUND = 2
    UI = 3

@dataclass
class Layer:
    """A rendering layer."""
    
    id: LayerID
    name: str
    z_order: int
    visible: bool = True
    opacity: float = 1.0
    parallax_factor: float = 1.0  # For scrolling
    sprites: List["AnimatedSprite"] = field(default_factory=list)
    
    def update(self, dt: float) -> None:
        """Update all sprites in this layer."""
        dead_sprites = []
        for sprite in self.sprites:
            sprite.update(dt)
            if hasattr(sprite, 'is_complete') and sprite.is_complete:
                dead_sprites.append(sprite)
        
        for sprite in dead_sprites:
            self.sprites.remove(sprite)
    
    def render_to_buffer(self, buffer: List[List[str]]) -> None:
        """Render layer sprites to a buffer."""
        for sprite in self.sprites:
            self._draw_sprite(buffer, sprite)
    
    def _draw_sprite(self, buffer: List[List[str]], sprite) -> None:
        """Draw a single sprite to buffer."""
        lines = sprite.current_image.strip().split('\n')
        
        for y_offset, line in enumerate(lines):
            y = sprite.y + y_offset
            if 0 <= y < len(buffer):
                for x_offset, char in enumerate(line):
                    x = sprite.x + x_offset
                    if 0 <= x < len(buffer[0]) and char != ' ':
                        buffer[y][x] = char
```

### 2. Layer Composition

Layers are composited together with blending:

```python
class LayerCompositor:
    """Composites multiple layers into final image."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.layers: Dict[LayerID, Layer] = {}
        
        # Initialize default layers
        for layer_id in LayerID:
            self.layers[layer_id] = Layer(
                id=layer_id,
                name=layer_id.name,
                z_order=layer_id.value
            )
    
    def composite(self) -> List[List[str]]:
        """Composite all layers into final image."""
        # Create final buffer
        final = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # Render layers in z-order
        for layer in sorted(self.layers.values(), key=lambda l: l.z_order):
            if not layer.visible:
                continue
            
            # Create layer buffer
            layer_buffer = [[' ' for _ in range(self.width)] for _ in range(self.height)]
            
            # Render layer
            layer.render_to_buffer(layer_buffer)
            
            # Blend onto final
            self._blend(final, layer_buffer, layer.opacity)
        
        return final
    
    def _blend(
        self, 
        dest: List[List[str]], 
        src: List[List[str]], 
        opacity: float
    ) -> None:
        """Blend source layer onto destination."""
        for y in range(len(dest)):
            for x in range(len(dest[0])):
                src_char = src[y][x]
                
                # Simple alpha blend (non-space overwrites)
                if src_char != ' ':
                    if opacity >= 1.0 or dest[y][x] == ' ':
                        dest[y][x] = src_char
                    # Could add partial opacity blending here
```

### 3. Parallax Scrolling

Background layers move slower than foreground for depth:

```python
class ParallaxCamera:
    """Camera with parallax scrolling support."""
    
    def __init__(self):
        self.x = 0
        self.y = 0
        self.scroll_speed = 1.0
    
    def scroll(self, dx: float, dy: float) -> None:
        """Scroll camera."""
        self.x += dx * self.scroll_speed
        self.y += dy * self.scroll_speed
    
    def apply_to_layer(self, layer: Layer, sprite_x: int) -> int:
        """Apply parallax effect to sprite position."""
        # Background layers move slower (parallax_factor < 1.0)
        offset = self.x * layer.parallax_factor
        return int(sprite_x - offset)
```

### 4. Layer States and Transitions

State machine for layer animations:

```python
from enum import Enum

class LayerState(Enum):
    """Layer animation states."""
    IDLE = "idle"
    ACTIVE = "active"
    TRANSITION = "transition"

class StatefulLayer(Layer):
    """Layer with state machine."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = LayerState.IDLE
        self.state_time = 0.0
        self.sprite_sets: Dict[LayerState, List] = {
            LayerState.IDLE: [],
            LayerState.ACTIVE: [],
        }
    
    def change_state(self, new_state: LayerState) -> None:
        """Transition to new state."""
        if self.state == new_state:
            return
        
        self.state = new_state
        self.state_time = 0.0
        
        # Swap sprite set
        self.sprites = self.sprite_sets.get(new_state, [])
    
    def update(self, dt: float) -> None:
        """Update with state tracking."""
        super().update(dt)
        self.state_time += dt
```

## Layered Canvas Widget

```python
from textual.widget import Widget
from textual.strip import Strip
from textual.segment import Segment

class LayeredCanvas(Widget):
    """Canvas with multi-layer rendering."""
    
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
        self.camera = ParallaxCamera()
        self.update_rate = 15  # FPS
    
    def on_mount(self) -> None:
        """Initialize canvas."""
        # Create compositor
        self.compositor = LayerCompositor(
            width=self.size.width,
            height=self.size.height
        )
        
        # Set up layers
        self.setup_layers()
        
        # Start update loop
        self.set_interval(1.0 / self.update_rate, self.update_layers)
    
    def setup_layers(self) -> None:
        """Configure layers."""
        # Background layer - slow parallax
        bg_layer = self.compositor.layers[LayerID.BACKGROUND]
        bg_layer.parallax_factor = 0.3
        
        # Midground layer - medium parallax  
        mg_layer = self.compositor.layers[LayerID.MIDGROUND]
        mg_layer.parallax_factor = 0.6
        
        # Foreground layer - full speed
        fg_layer = self.compositor.layers[LayerID.FOREGROUND]
        fg_layer.parallax_factor = 1.0
        
        # UI layer - no parallax
        ui_layer = self.compositor.layers[LayerID.UI]
        ui_layer.parallax_factor = 0.0
        
        # Add initial sprites to layers
        self.populate_background()
        self.spawn_character()
    
    def populate_background(self) -> None:
        """Add background sprites."""
        bg_layer = self.compositor.layers[LayerID.BACKGROUND]
        
        # Example: Add terrain
        terrain_sprite = AnimatedSprite(
            frames=["▓▓▓▓▓▓▓▓▓▓"],
            x=0,
            y=self.size.height - 1,
            fps=1,
            loop=True
        )
        bg_layer.sprites.append(terrain_sprite)
    
    def spawn_character(self) -> None:
        """Spawn main character on foreground layer."""
        fg_layer = self.compositor.layers[LayerID.FOREGROUND]
        
        from ..sprites.sprite_library import SpriteLibrary
        library = SpriteLibrary()
        # ... load character sprite
        
        char_sprite = AnimatedSprite(
            frames=CHARACTER_IDLE,
            x=self.size.width // 2,
            y=self.size.height // 2,
            fps=4,
            loop=True
        )
        fg_layer.sprites.append(char_sprite)
    
    def update_layers(self) -> None:
        """Update all layers."""
        dt = 1.0 / self.update_rate
        
        for layer in self.compositor.layers.values():
            layer.update(dt)
        
        self.refresh()
    
    def render_line(self, y: int) -> Strip:
        """Render composited line."""
        # Composite all layers
        composited = self.compositor.composite()
        
        # Get line
        if 0 <= y < len(composited):
            line = ''.join(composited[y])
            return Strip([Segment(line)], len(line))
        
        return Strip([Segment(' ' * self.size.width)], self.size.width)
    
    def spawn_effect(self, effect_name: str, x: int, y: int) -> None:
        """Spawn effect on midground layer."""
        mg_layer = self.compositor.layers[LayerID.MIDGROUND]
        
        # Create effect sprite
        effect = AnimatedSprite(
            frames=SPARKLE,  # From sprite library
            x=x,
            y=y,
            fps=15,
            loop=False
        )
        mg_layer.sprites.append(effect)
    
    def add_ui_element(self, sprite: AnimatedSprite) -> None:
        """Add UI element to UI layer."""
        ui_layer = self.compositor.layers[LayerID.UI]
        ui_layer.sprites.append(sprite)
```

## Example Use Cases

### 1. Parallax Scrolling Background

```python
# Setup background with parallax
bg_layer = compositor.layers[LayerID.BACKGROUND]
bg_layer.parallax_factor = 0.2  # Moves 20% of camera speed

# Add distant mountains
mountains = AnimatedSprite(
    frames=["  /\\    /\\  /\\  "],
    x=0,
    y=5,
    fps=1,
    loop=True
)
bg_layer.sprites.append(mountains)

# Camera scrolls, background moves slower
camera.scroll(dx=10, dy=0)
```

### 2. Weather Effects Overlay

```python
# Rain on foreground layer
rain_layer = compositor.layers[LayerID.FOREGROUND]

for i in range(20):
    raindrop = AnimatedSprite(
        frames=["|", "|", "|"],
        x=random.randint(0, width),
        y=random.randint(0, height // 2),
        fps=30,
        loop=True
    )
    rain_layer.sprites.append(raindrop)
```

### 3. UI Layer (Always On Top)

```python
# Score display on UI layer
ui_layer = compositor.layers[LayerID.UI]

score_display = AnimatedSprite(
    frames=[f"Score: {game_state.counter.format()}"],
    x=2,
    y=1,
    fps=1,
    loop=True
)
ui_layer.sprites.append(score_display)
```

### 4. Layer Fading Transitions

```python
# Fade out background layer
async def fade_out_background():
    bg_layer = compositor.layers[LayerID.BACKGROUND]
    
    for opacity in range(100, -1, -5):
        bg_layer.opacity = opacity / 100.0
        await asyncio.sleep(0.05)
    
    bg_layer.visible = False
```

## Performance Characteristics

### Complexity
- **Update:** O(n) where n = total sprites across all layers
- **Render:** O(layers × width × height)
- **Composite:** O(layers × visible_pixels)

### Frame Budget (15 FPS = 66ms)
```
Layer updates:     10ms (4 layers × 10 sprites)
Composition:       20ms (4 layers × buffer size)
Rendering:         15ms (final composite)
Buffer:             5ms
---
Total:            ~50ms ✅ (75% of budget)
```

### Optimization Tips
1. Only composite visible layers
2. Cache static layers (background)
3. Use dirty rectangle tracking
4. Limit sprites per layer to 20-30
5. Pre-render static content

## Pros and Cons

### Pros ✅
- Natural depth perception with layers
- Parallax scrolling for visual depth
- Easy to organize complex scenes
- Layer-level effects (fade, opacity)
- Clean separation of concerns
- Independent layer update rates possible
- Easy to toggle layers on/off

### Cons ❌
- More complex than single-canvas approach
- Higher memory usage (multiple buffers)
- Composition overhead
- Can be overkill for simple scenes
- Requires planning layer organization
- Debugging multi-layer interactions harder

## When to Use

Choose this strategy if:
- ✅ Complex scenes with depth
- ✅ Parallax scrolling needed
- ✅ Many environmental effects
- ✅ UI elements separate from game world
- ✅ Weather/particle overlays
- ✅ Scene transitions and fades
- ✅ Good organization is priority

## Next Steps

See [implementation.md](./implementation.md) for step-by-step implementation guide.
See [examples/](./examples/) for working code samples.
