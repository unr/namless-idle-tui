# Strategy 1: Sprite Sheet Animation System

## Overview

Frame-based sprite animation using sprite sheets, similar to classic 8-bit games. Each sprite is defined as an array of frames (multi-line ASCII/Unicode art), and the animation system cycles through frames at a configurable rate.

This is the **recommended approach** for most incremental games with sprite-based visuals.

## Architecture

```
┌────────────────────────────────────────────────────────┐
│                    IdleGame (App)                      │
│  ┌──────────────────────────────────────────────────┐ │
│  │         Horizontal Container (70/30)             │ │
│  │  ┌──────────────────┐  ┌────────────────────┐   │ │
│  │  │  SpriteCanvas    │  │  ActionsPanel      │   │ │
│  │  │  (70% width)     │  │  (30% width)       │   │ │
│  │  │                  │  │                    │   │ │
│  │  │ ┌──────────────┐ │  │  - Stats           │   │ │
│  │  │ │ Sprite       │ │  │  - Buttons         │   │ │
│  │  │ │ Manager      │ │  │  - Upgrades        │   │ │
│  │  │ │              │ │  │                    │   │ │
│  │  │ │ [Sprite 1]   │ │  │                    │   │ │
│  │  │ │ [Sprite 2]   │ │  │                    │   │ │
│  │  │ │ [Sprite 3]   │ │  │                    │   │ │
│  │  │ └──────────────┘ │  │                    │   │ │
│  │  │                  │  │                    │   │ │
│  │  │  @ 15fps update  │  │                    │   │ │
│  │  └──────────────────┘  └────────────────────┘   │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

## Key Concepts

### 1. Sprite Sheet Definition

A sprite sheet is a collection of animation frames:

```python
# ASCII Art Sprite
COIN_SPIN = [
    "O",      # Frame 0
    "()",     # Frame 1
    "||",     # Frame 2
    "()",     # Frame 3
    "O"       # Frame 4
]

# Multi-line ASCII Sprite
CHARACTER_IDLE = [
    # Frame 0
    """
  O
 /|\\
 / \\
""",
    # Frame 1
    """
  O
 \\|/
 / \\
"""
]

# Unicode Block Sprite (Pixel Art)
MAGE_IDLE = [
    # Frame 0
    """
  ▄█▄
  █▀█
  ▀ ▀
""",
    # Frame 1
    """
  ▄█▄
  █▀█
  ▀ ▀
"""
]
```

### 2. Animated Sprite Class

```python
from dataclasses import dataclass
from typing import List
from decimal import Decimal

@dataclass
class AnimatedSprite:
    """A sprite with frame-based animation."""
    
    frames: List[str]              # Animation frames
    x: int                         # Screen position X
    y: int                         # Screen position Y
    fps: int = 10                  # Animation speed
    loop: bool = True              # Loop animation?
    current_frame: int = 0         # Current frame index
    time_accumulator: float = 0.0  # Time tracking
    is_playing: bool = True        # Animation state
    on_complete: callable = None   # Callback when done
    
    @property
    def frame_duration(self) -> float:
        """Duration of each frame in seconds."""
        return 1.0 / self.fps
    
    @property
    def current_image(self) -> str:
        """Get current frame's image."""
        return self.frames[self.current_frame]
    
    @property
    def width(self) -> int:
        """Calculate sprite width."""
        lines = self.current_image.split('\n')
        return max(len(line) for line in lines)
    
    @property
    def height(self) -> int:
        """Calculate sprite height."""
        return len(self.current_image.split('\n'))
    
    def update(self, dt: float) -> None:
        """Update animation state."""
        if not self.is_playing:
            return
        
        self.time_accumulator += dt
        
        # Advance frame when enough time has passed
        while self.time_accumulator >= self.frame_duration:
            self.time_accumulator -= self.frame_duration
            self.current_frame += 1
            
            # Handle end of animation
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.is_playing = False
                    if self.on_complete:
                        self.on_complete(self)
    
    def play(self, from_start: bool = True) -> None:
        """Start playing animation."""
        if from_start:
            self.current_frame = 0
            self.time_accumulator = 0.0
        self.is_playing = True
    
    def pause(self) -> None:
        """Pause animation."""
        self.is_playing = False
    
    def reset(self) -> None:
        """Reset to first frame."""
        self.current_frame = 0
        self.time_accumulator = 0.0
```

### 3. Sprite Canvas Widget

```python
from textual.widget import Widget
from textual.strip import Strip
from textual.segment import Segment
from typing import List, Dict

class SpriteCanvas(Widget):
    """Canvas for rendering animated sprites."""
    
    DEFAULT_CSS = """
    SpriteCanvas {
        width: 100%;
        height: 100%;
        background: $surface;
        border: solid $primary;
    }
    """
    
    def __init__(self, game_state, **kwargs):
        super().__init__(**kwargs)
        self.game_state = game_state
        self.sprites: List[AnimatedSprite] = []
        self.sprite_templates: Dict[str, List[str]] = {}
        self.update_interval = 1.0 / 15  # 15 FPS
        
    def on_mount(self) -> None:
        """Start animation loop."""
        self.load_sprite_assets()
        self.set_interval(self.update_interval, self.update_sprites)
    
    def load_sprite_assets(self) -> None:
        """Load sprite definitions from assets."""
        # Load from files or define inline
        self.sprite_templates = {
            'coin_spin': COIN_SPIN,
            'character_idle': CHARACTER_IDLE,
            'mage_idle': MAGE_IDLE
        }
    
    def update_sprites(self) -> None:
        """Update all sprite animations."""
        dt = self.update_interval
        
        # Update each sprite
        dead_sprites = []
        for sprite in self.sprites:
            sprite.update(dt)
            
            # Mark non-looping completed sprites for removal
            if not sprite.loop and not sprite.is_playing:
                dead_sprites.append(sprite)
        
        # Remove completed sprites
        for sprite in dead_sprites:
            self.sprites.remove(sprite)
        
        # Trigger re-render
        self.refresh()
    
    def render_line(self, y: int) -> Strip:
        """Render a single line of the canvas."""
        width = self.size.width
        
        # Create blank line
        line_chars = [' '] * width
        
        # Render sprites that overlap this line
        for sprite in sorted(self.sprites, key=lambda s: s.y):
            sprite_lines = sprite.current_image.split('\n')
            
            # Check if this y coordinate is within sprite bounds
            if sprite.y <= y < sprite.y + len(sprite_lines):
                sprite_line_index = y - sprite.y
                sprite_line = sprite_lines[sprite_line_index]
                
                # Draw sprite line onto canvas line
                for i, char in enumerate(sprite_line):
                    x_pos = sprite.x + i
                    if 0 <= x_pos < width and char != ' ':
                        line_chars[x_pos] = char
        
        # Convert to Strip
        return Strip([Segment(''.join(line_chars))], width)
    
    def spawn_sprite(
        self, 
        template_name: str, 
        x: int, 
        y: int,
        fps: int = 10,
        loop: bool = True,
        on_complete = None
    ) -> AnimatedSprite:
        """Spawn a new sprite from template."""
        if template_name not in self.sprite_templates:
            raise ValueError(f"Unknown sprite template: {template_name}")
        
        sprite = AnimatedSprite(
            frames=self.sprite_templates[template_name],
            x=x,
            y=y,
            fps=fps,
            loop=loop,
            on_complete=on_complete
        )
        
        self.sprites.append(sprite)
        return sprite
    
    def play_animation(self, animation_name: str) -> None:
        """Trigger a named animation."""
        # Example: Play coin collection animation
        if animation_name == "coin_collect":
            center_x = self.size.width // 2
            center_y = self.size.height // 2
            
            self.spawn_sprite(
                'coin_spin',
                x=center_x,
                y=center_y,
                fps=15,
                loop=False,
                on_complete=lambda s: None  # Will be auto-removed
            )
```

### 4. Sprite Asset Format

Sprites can be stored in text files:

```
# assets/sprites/coin.txt
# Sprite: Coin Spin
# FPS: 15
# Loop: true
---FRAME---
O
---FRAME---
()
---FRAME---
||
---FRAME---
()
---FRAME---
O
```

Loading sprite files:

```python
def load_sprite_from_file(filepath: str) -> dict:
    """Load sprite definition from file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    frames = []
    current_frame = []
    metadata = {}
    
    for line in content.split('\n'):
        if line.startswith('#'):
            # Parse metadata
            if 'FPS:' in line:
                metadata['fps'] = int(line.split(':')[1].strip())
            elif 'Loop:' in line:
                metadata['loop'] = line.split(':')[1].strip().lower() == 'true'
        elif line == '---FRAME---':
            # Save current frame
            if current_frame:
                frames.append('\n'.join(current_frame))
                current_frame = []
        else:
            current_frame.append(line)
    
    # Save last frame
    if current_frame:
        frames.append('\n'.join(current_frame))
    
    return {
        'frames': frames,
        'fps': metadata.get('fps', 10),
        'loop': metadata.get('loop', True)
    }
```

## Example Sprite Definitions

### 1. Coin Collection

```python
COIN_COLLECT = [
    # Frame 0 - whole coin
    "💰",
    # Frame 1 - spinning
    "🪙",
    # Frame 2 - side view
    "│",
    # Frame 3 - spinning back
    "🪙",
    # Frame 4 - whole coin
    "💰"
]
```

### 2. Character Idle (ASCII)

```python
CHARACTER_IDLE = [
    # Frame 0
    """
  O
 /|\\
 / \\
""",
    # Frame 1 - breathing
    """
  O
 /|\\
 / \\
""",
    # Frame 2
    """
  O
 \\|/
 / \\
""",
    # Frame 3 - breathing
    """
  O
 \\|/
 / \\
"""
]
```

### 3. Mage Character (Unicode Blocks)

```python
MAGE_IDLE = [
    # Frame 0
    """
 🧙
▄█▄
█▀█
▀ ▀
""",
    # Frame 1 - staff glowing
    """
 🧙✨
▄█▄
█▀█
▀ ▀
""",
    # Frame 2
    """
 🧙
▄█▄
█▀█
▀ ▀
""",
    # Frame 3 - staff glowing
    """
 🧙✨
▄█▄
█▀█
▀ ▀
"""
]
```

### 4. Fire Animation

```python
FIRE_LOOP = [
    # Frame 0
    """
 🔥
▓▓▓
""",
    # Frame 1
    """
🔥 
▓▓▓
""",
    # Frame 2
    """
 🔥
▓▓▓
""",
    # Frame 3
    """
  🔥
▓▓▓
"""
]
```

## Integration with Game State

```python
class IdleGame(App):
    """Main game app with sprite animations."""
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Horizontal(id="main-layout"):
            yield SpriteCanvas(self.game_state, id="sprite-canvas")
            yield ActionsPanel(self.game_state, id="actions-panel")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize game."""
        # Spawn idle character
        canvas = self.query_one("#sprite-canvas", SpriteCanvas)
        canvas.spawn_sprite(
            'mage_idle',
            x=canvas.size.width // 2 - 2,
            y=canvas.size.height // 2,
            fps=8,
            loop=True
        )
    
    def on_counter_increment(self, increment: GameNumber) -> None:
        """Handle counter increment with animation."""
        canvas = self.query_one("#sprite-canvas", SpriteCanvas)
        
        # Play coin collection animation
        canvas.play_animation("coin_collect")
        
        # Spawn floating number
        center_x = canvas.size.width // 2
        center_y = canvas.size.height // 2 - 5
        
        floating_num = AnimatedSprite(
            frames=[f"+{increment.format()}"],  # Single frame
            x=center_x,
            y=center_y,
            fps=1,
            loop=False
        )
        
        canvas.sprites.append(floating_num)
```

## Performance Characteristics

### Frame Rate Guidelines
- **8-10 FPS** - Good for idle animations (breathing, swaying)
- **12-15 FPS** - Standard for most sprite animations
- **20-30 FPS** - Smooth action animations (if needed)

### Sprite Limits
- **Active sprites:** 50+ simultaneous sprites
- **Total sprite templates:** 100+ different sprites
- **Frame count per sprite:** 4-12 frames typical
- **Canvas update rate:** 15 FPS recommended

### Memory Usage
- **Single ASCII sprite:** ~1KB
- **Complex Unicode sprite:** ~5KB
- **100 sprite templates:** ~500KB
- **50 active sprites:** ~50KB runtime

## Pros and Cons

### Pros ✅
- Simple to understand and implement
- Easy to create content (just draw ASCII art)
- Flexible - supports ASCII and Unicode
- Good performance (15fps is plenty)
- Familiar to classic game developers
- Clear separation between art and code
- Easy to preview and edit sprites

### Cons ❌
- Manual frame creation (no interpolation)
- Limited to grid-based positioning
- No built-in sprite effects (rotation, scaling)
- Requires artistic skill for good sprites
- Can be tedious for complex animations

## When to Use

Choose this strategy if:
- ✅ You want retro/classic game aesthetic
- ✅ Content creation is important
- ✅ You need simple, clear animations
- ✅ Performance isn't critical (10-15fps is fine)
- ✅ You want full control over sprite appearance
- ✅ Team can create ASCII/pixel art

## Next Steps

See [implementation.md](./implementation.md) for step-by-step implementation guide.
See [BEST_PRACTICES.md](./BEST_PRACTICES.md) for sprite creation tips.
See [examples/](./examples/) for working code samples and sprite assets.
