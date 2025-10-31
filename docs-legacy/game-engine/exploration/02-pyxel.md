# Pyxel - Retro Game Engine

## Overview
Pyxel is a retro game engine for Python inspired by PICO-8 and other fantasy consoles. It provides pixel art tools, sound generation, and a complete game development environment.

## Relevance to Our Goals
- **Sprite system**: Built-in sprite and tilemap support
- **Animation**: Frame-based animation with sprite sheets
- **Performance**: Optimized for retro-style games
- **Resource management**: Built-in resource editor for sprites

## Key Features
- 16-color palette (customizable)
- 256x256 pixel art editor
- 4-channel sound support
- Tilemap system for backgrounds
- Built-in sprite sheet support

## Code Example
```python
import pyxel

class Game:
    def __init__(self):
        pyxel.init(160, 120, title="Idle Game")
        pyxel.load("assets.pyxres")
        self.x = 80
        self.y = 60
        pyxel.run(self.update, self.draw)
    
    def update(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.spawn_number()
    
    def draw(self):
        pyxel.cls(0)
        pyxel.spr(0, self.x, self.y, 8, 8)  # Draw sprite
        pyxel.text(5, 5, f"Score: {self.score}", 7)

Game()
```

## Pros
- Complete game engine with all tools included
- Excellent sprite and animation support
- Fast performance for pixel art games
- Active community and good documentation

## Cons
- Opens its own window - not compatible with terminal/TUI
- Fixed resolution and color palette
- Designed for standalone games, not TUI integration

## Integration Difficulty
**Very High** - Pyxel is designed to create its own window and cannot render to a terminal.

## Alternative Use
We could study Pyxel's sprite management and animation systems to implement similar patterns in our TUI environment.

## Verdict
Not directly usable for our TUI game, but excellent reference for sprite animation patterns and game loop design.
