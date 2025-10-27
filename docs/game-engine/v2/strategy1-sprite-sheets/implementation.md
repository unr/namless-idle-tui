# Implementation Guide - Strategy 1: Sprite Sheet Animation

## Overview

This guide walks through implementing a sprite sheet animation system from scratch. Total time: 2-3 days.

## Phase 1: Core Sprite System (Day 1)

### Step 1.1: Create Sprite Data Structures

```python
# src/idle_game/sprites/animated_sprite.py
from dataclasses import dataclass, field
from typing import List, Callable, Optional

@dataclass
class AnimatedSprite:
    """Frame-based animated sprite."""
    
    frames: List[str]
    x: int
    y: int
    fps: int = 10
    loop: bool = True
    current_frame: int = 0
    time_accumulator: float = 0.0
    is_playing: bool = True
    on_complete: Optional[Callable] = None
    tags: List[str] = field(default_factory=list)  # For filtering/querying
    
    @property
    def frame_duration(self) -> float:
        return 1.0 / self.fps
    
    @property
    def current_image(self) -> str:
        return self.frames[self.current_frame]
    
    @property
    def width(self) -> int:
        lines = self.current_image.strip().split('\n')
        return max(len(line) for line in lines) if lines else 0
    
    @property
    def height(self) -> int:
        return len(self.current_image.strip().split('\n'))
    
    @property
    def is_complete(self) -> bool:
        return not self.loop and not self.is_playing
    
    def update(self, dt: float) -> None:
        """Update animation state."""
        if not self.is_playing:
            return
        
        self.time_accumulator += dt
        
        while self.time_accumulator >= self.frame_duration:
            self.time_accumulator -= self.frame_duration
            self.current_frame += 1
            
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.is_playing = False
                    if self.on_complete:
                        self.on_complete(self)
    
    def play(self, from_start: bool = True) -> None:
        if from_start:
            self.current_frame = 0
            self.time_accumulator = 0.0
        self.is_playing = True
    
    def pause(self) -> None:
        self.is_playing = False
    
    def stop(self) -> None:
        self.is_playing = False
        self.current_frame = 0
        self.time_accumulator = 0.0
    
    def has_tag(self, tag: str) -> bool:
        return tag in self.tags
```

### Step 1.2: Create Sprite Library

```python
# src/idle_game/sprites/sprite_library.py
from typing import Dict, List
from pathlib import Path

class SpriteLibrary:
    """Central repository for sprite templates."""
    
    def __init__(self):
        self.templates: Dict[str, dict] = {}
    
    def register(
        self, 
        name: str, 
        frames: List[str],
        fps: int = 10,
        loop: bool = True,
        tags: List[str] = None
    ) -> None:
        """Register a sprite template."""
        self.templates[name] = {
            'frames': frames,
            'fps': fps,
            'loop': loop,
            'tags': tags or []
        }
    
    def load_from_file(self, filepath: str) -> None:
        """Load sprite from file."""
        path = Path(filepath)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frames = []
        current_frame = []
        metadata = {
            'fps': 10,
            'loop': True,
            'tags': []
        }
        
        for line in content.split('\n'):
            if line.startswith('# FPS:'):
                metadata['fps'] = int(line.split(':')[1].strip())
            elif line.startswith('# Loop:'):
                metadata['loop'] = line.split(':')[1].strip().lower() == 'true'
            elif line.startswith('# Tags:'):
                tags = line.split(':')[1].strip()
                metadata['tags'] = [t.strip() for t in tags.split(',')]
            elif line == '---FRAME---':
                if current_frame:
                    frames.append('\n'.join(current_frame))
                    current_frame = []
            elif not line.startswith('#'):
                current_frame.append(line)
        
        # Add last frame
        if current_frame:
            frames.append('\n'.join(current_frame))
        
        # Register sprite
        sprite_name = path.stem
        self.register(
            sprite_name,
            frames,
            metadata['fps'],
            metadata['loop'],
            metadata['tags']
        )
    
    def load_directory(self, dir_path: str) -> None:
        """Load all sprites from directory."""
        directory = Path(dir_path)
        for file in directory.glob('*.txt'):
            self.load_from_file(str(file))
    
    def get_template(self, name: str) -> dict:
        """Get sprite template by name."""
        if name not in self.templates:
            raise ValueError(f"Sprite template '{name}' not found")
        return self.templates[name]
    
    def list_sprites(self, tag: str = None) -> List[str]:
        """List available sprites, optionally filtered by tag."""
        if tag is None:
            return list(self.templates.keys())
        
        return [
            name for name, template in self.templates.items()
            if tag in template['tags']
        ]
```

### Step 1.3: Define Initial Sprite Assets

```python
# src/idle_game/sprites/default_sprites.py
"""Default sprite definitions."""

# Coin animation
COIN_SPIN = [
    "💰",
    "🪙",
    "│",
    "🪙",
    "💰"
]

# Simple character idle
CHARACTER_IDLE = [
    """
  O
 /|\\
 / \\
""",
    """
  O
 \\|/
 / \\
"""
]

# Sparkle effect
SPARKLE = [
    "·",
    "✦",
    "✨",
    "✦",
    "·"
]

# Plus number (for increments)
def create_plus_number(value: str) -> List[str]:
    """Create a single-frame sprite for a number."""
    return [f"+{value}"]

def register_default_sprites(library: SpriteLibrary) -> None:
    """Register all default sprites."""
    library.register('coin_spin', COIN_SPIN, fps=12, loop=False, tags=['effect', 'coin'])
    library.register('character_idle', CHARACTER_IDLE, fps=4, loop=True, tags=['character'])
    library.register('sparkle', SPARKLE, fps=15, loop=False, tags=['effect'])
```

## Phase 2: Canvas Implementation (Day 1-2)

### Step 2.1: Create Sprite Canvas Widget

```python
# src/idle_game/widgets/sprite_canvas.py
from textual.widget import Widget
from textual.strip import Strip
from textual.segment import Segment
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import GameState

from ..sprites.animated_sprite import AnimatedSprite
from ..sprites.sprite_library import SpriteLibrary
from ..sprites.default_sprites import register_default_sprites

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
    
    def __init__(self, game_state: "GameState", **kwargs):
        super().__init__(**kwargs)
        self.game_state = game_state
        self.sprites: List[AnimatedSprite] = []
        self.library = SpriteLibrary()
        self.update_rate = 15  # 15 FPS
        
    def on_mount(self) -> None:
        """Initialize canvas."""
        # Load sprite library
        register_default_sprites(self.library)
        
        # Try to load custom sprites from assets
        try:
            self.library.load_directory('src/idle_game/sprites/assets')
        except FileNotFoundError:
            pass  # No custom sprites yet
        
        # Start update loop
        self.set_interval(1.0 / self.update_rate, self.update_sprites)
        
        # Spawn initial sprites
        self.spawn_idle_character()
    
    def spawn_idle_character(self) -> None:
        """Spawn the main idle character."""
        center_x = self.size.width // 2
        center_y = self.size.height // 2
        
        self.spawn_sprite(
            'character_idle',
            x=center_x - 2,
            y=center_y,
            z_order=10
        )
    
    def update_sprites(self) -> None:
        """Update all sprite animations."""
        dt = 1.0 / self.update_rate
        
        # Update sprites
        dead_sprites = []
        for sprite in self.sprites:
            sprite.update(dt)
            
            # Mark completed non-looping sprites
            if sprite.is_complete:
                dead_sprites.append(sprite)
        
        # Remove dead sprites
        for sprite in dead_sprites:
            self.sprites.remove(sprite)
        
        # Refresh display
        self.refresh()
    
    def render_line(self, y: int) -> Strip:
        """Render a single line of the canvas."""
        width = self.size.width
        
        # Create empty line
        line_chars = [' '] * width
        
        # Sort sprites by z_order (if available)
        sorted_sprites = sorted(
            self.sprites,
            key=lambda s: getattr(s, 'z_order', 0)
        )
        
        # Render sprites
        for sprite in sorted_sprites:
            sprite_lines = sprite.current_image.strip().split('\n')
            
            # Check if sprite overlaps this line
            if sprite.y <= y < sprite.y + len(sprite_lines):
                line_index = y - sprite.y
                sprite_line = sprite_lines[line_index]
                
                # Draw sprite line
                for i, char in enumerate(sprite_line):
                    x_pos = sprite.x + i
                    if 0 <= x_pos < width:
                        # Only draw non-space characters (transparency)
                        if char != ' ':
                            line_chars[x_pos] = char
        
        return Strip([Segment(''.join(line_chars))], width)
    
    def spawn_sprite(
        self,
        template_name: str,
        x: int,
        y: int,
        fps: Optional[int] = None,
        loop: Optional[bool] = None,
        on_complete = None,
        z_order: int = 0,
        tags: List[str] = None
    ) -> AnimatedSprite:
        """Spawn a sprite from template."""
        template = self.library.get_template(template_name)
        
        sprite = AnimatedSprite(
            frames=template['frames'],
            x=x,
            y=y,
            fps=fps or template['fps'],
            loop=loop if loop is not None else template['loop'],
            on_complete=on_complete,
            tags=(tags or []) + template['tags']
        )
        
        # Add z_order as attribute
        sprite.z_order = z_order
        
        self.sprites.append(sprite)
        return sprite
    
    def clear_sprites(self, tag: Optional[str] = None) -> None:
        """Clear sprites, optionally filtered by tag."""
        if tag is None:
            self.sprites.clear()
        else:
            self.sprites = [s for s in self.sprites if not s.has_tag(tag)]
    
    def get_sprites_by_tag(self, tag: str) -> List[AnimatedSprite]:
        """Get all sprites with a specific tag."""
        return [s for s in self.sprites if s.has_tag(tag)]
```

### Step 2.2: Integrate with Game State

```python
# src/idle_game/app.py - Updated methods

def compose(self) -> ComposeResult:
    yield Header()
    
    with Horizontal(id="main-layout"):
        # 70% sprite canvas
        yield SpriteCanvas(self.game_state, id="sprite-canvas")
        
        # 30% actions panel
        yield ActionsPanel(self.game_state, id="actions-panel")
    
    yield Footer()

def game_tick(self):
    """Main game loop tick."""
    now = datetime.now()
    increment = self.game_state.update(now)
    
    # Update actions panel
    actions_panel = self.query_one("#actions-panel", ActionsPanel)
    actions_panel.update_display(self.game_state.counter.format())
    
    # Spawn animation for increments
    if increment.value >= Decimal("0.1"):
        self.spawn_increment_animation(increment)

def spawn_increment_animation(self, increment: GameNumber) -> None:
    """Spawn animation for counter increment."""
    canvas = self.query_one("#sprite-canvas", SpriteCanvas)
    center_x = canvas.size.width // 2
    center_y = canvas.size.height // 2
    
    # Spawn coin spin effect
    canvas.spawn_sprite(
        'coin_spin',
        x=center_x,
        y=center_y - 3,
        z_order=20,
        tags=['effect']
    )
    
    # Spawn floating number
    from ..sprites.animated_sprite import AnimatedSprite
    floating_text = AnimatedSprite(
        frames=[f"+{increment.format()}"],
        x=center_x + 3,
        y=center_y - 2,
        fps=1,
        loop=False
    )
    floating_text.z_order = 25
    canvas.sprites.append(floating_text)

async def on_actions_panel_click_requested(self, event):
    """Handle manual click."""
    increment = self.game_state.click()
    
    # Update display
    actions_panel = self.query_one("#actions-panel", ActionsPanel)
    actions_panel.update_display(self.game_state.counter.format())
    
    # Spawn click animation
    self.spawn_increment_animation(increment)
```

## Phase 3: Asset Creation (Day 2)

### Step 3.1: Create Sprite Asset Files

```
# src/idle_game/sprites/assets/coin.txt
# FPS: 12
# Loop: false
# Tags: effect, coin
---FRAME---
💰
---FRAME---
🪙
---FRAME---
│
---FRAME---
🪙
---FRAME---
💰
```

```
# src/idle_game/sprites/assets/mage.txt
# FPS: 4
# Loop: true
# Tags: character, player
---FRAME---
  🧙
 ▄█▄
 █▀█
 ▀ ▀
---FRAME---
  🧙✨
 ▄█▄
 █▀█
 ▀ ▀
---FRAME---
  🧙
 ▄█▄
 █▀█
 ▀ ▀
---FRAME---
  🧙
 ▄█▄
 █▀█
 ▀ ▀
```

### Step 3.2: Create Sprite Editor Helper

```python
# tools/sprite_editor.py
"""Simple CLI tool for creating sprite sheets."""

def create_sprite_file():
    """Interactive sprite file creator."""
    print("=== Sprite Sheet Creator ===\n")
    
    name = input("Sprite name: ")
    fps = int(input("FPS (default 10): ") or "10")
    loop = input("Loop? (y/n, default y): ").lower() != 'n'
    tags = input("Tags (comma-separated): ")
    
    frames = []
    frame_num = 1
    
    print("\nEnter frames (type 'DONE' on empty line when finished):")
    print("(Multi-line frames supported - empty line ends frame)\n")
    
    while True:
        print(f"--- Frame {frame_num} ---")
        frame_lines = []
        
        while True:
            line = input()
            if line == "DONE":
                break
            if line == "" and frame_lines:
                # Empty line after content = end of frame
                break
            frame_lines.append(line)
        
        if not frame_lines:
            break
        
        frames.append('\n'.join(frame_lines))
        frame_num += 1
    
    # Write file
    filepath = f"src/idle_game/sprites/assets/{name}.txt"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# FPS: {fps}\n")
        f.write(f"# Loop: {str(loop).lower()}\n")
        f.write(f"# Tags: {tags}\n")
        
        for frame in frames:
            f.write("---FRAME---\n")
            f.write(frame + "\n")
    
    print(f"\nSprite saved to: {filepath}")

if __name__ == "__main__":
    create_sprite_file()
```

## Phase 4: Testing & Polish (Day 3)

### Step 4.1: Unit Tests

```python
# tests/test_animated_sprite.py
import pytest
from src.idle_game.sprites.animated_sprite import AnimatedSprite

def test_sprite_animation_advances():
    """Test sprite advances through frames."""
    sprite = AnimatedSprite(
        frames=["A", "B", "C"],
        x=0,
        y=0,
        fps=10
    )
    
    assert sprite.current_frame == 0
    assert sprite.current_image == "A"
    
    # Update for one frame duration
    sprite.update(0.1)
    assert sprite.current_frame == 1
    assert sprite.current_image == "B"

def test_sprite_loops():
    """Test sprite loops correctly."""
    sprite = AnimatedSprite(
        frames=["A", "B"],
        x=0,
        y=0,
        fps=10,
        loop=True
    )
    
    sprite.update(0.1)  # Frame 1
    sprite.update(0.1)  # Should loop to frame 0
    assert sprite.current_frame == 0

def test_sprite_completes():
    """Test non-looping sprite completes."""
    completed = False
    
    def on_complete(s):
        nonlocal completed
        completed = True
    
    sprite = AnimatedSprite(
        frames=["A", "B"],
        x=0,
        y=0,
        fps=10,
        loop=False,
        on_complete=on_complete
    )
    
    sprite.update(0.1)  # Frame 1
    sprite.update(0.1)  # Complete
    
    assert sprite.is_complete
    assert completed
```

### Step 4.2: Performance Test

```python
# tests/test_sprite_performance.py
import pytest
from time import perf_counter
from src.idle_game.widgets.sprite_canvas import SpriteCanvas
from src.idle_game.models import GameState

def test_many_sprites_performance():
    """Test canvas can handle many sprites."""
    canvas = SpriteCanvas(GameState())
    canvas.size = (80, 40)
    
    # Spawn 50 sprites
    for i in range(50):
        canvas.spawn_sprite(
            'sparkle',
            x=i % 80,
            y=i % 40
        )
    
    # Measure update time
    start = perf_counter()
    iterations = 100
    
    for _ in range(iterations):
        canvas.update_sprites()
    
    elapsed = perf_counter() - start
    avg_time = elapsed / iterations
    
    # Should be fast (< 10ms at 15fps = 66ms budget)
    assert avg_time < 0.01, f"Too slow: {avg_time*1000:.2f}ms"
```

## Directory Structure

```
src/idle_game/
├── sprites/
│   ├── __init__.py
│   ├── animated_sprite.py        # Core sprite class
│   ├── sprite_library.py         # Asset management
│   ├── default_sprites.py        # Built-in sprites
│   └── assets/
│       ├── coin.txt
│       ├── mage.txt
│       ├── sparkle.txt
│       └── ...
├── widgets/
│   ├── sprite_canvas.py          # Main canvas widget
│   └── actions_panel.py
├── app.py
└── models.py

tools/
└── sprite_editor.py              # Helper tool

tests/
├── test_animated_sprite.py
└── test_sprite_performance.py
```

## Next Steps

1. ✅ Implement core sprite classes
2. ✅ Create sprite canvas widget
3. ✅ Design initial sprite assets
4. ✅ Integrate with game state
5. Create more sprite variations
6. Add advanced effects (fading, movement)
7. Optimize rendering
8. Polish and playtest

## Tips

- Start with simple 2-3 frame animations
- Test sprites at different FPS values
- Use tags to organize sprite collections
- Keep sprites small (< 10 lines tall)
- Use Unicode sparingly (compatibility)
- Profile with many sprites active
