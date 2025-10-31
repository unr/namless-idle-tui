# Python Libraries Exploration Summary

## Overview
This document summarizes the exploration of Python libraries that could assist with our game engine implementation for the Textual-based idle game.

## Top Recommendations

### 1. **Rich (Built-in with Textual) ⭐⭐⭐⭐⭐**
- **Why**: Already integrated, excellent performance
- **Use for**: Text animations, renderables, live updates
- **Integration**: Zero - it's already there!

### 2. **Asyncio (Python stdlib) ⭐⭐⭐⭐⭐**
- **Why**: Native to Textual, precise timing control
- **Use for**: Animation loops, concurrent animations
- **Integration**: Very easy - Textual is built on asyncio

### 3. **NumPy ⭐⭐⭐⭐**
- **Why**: Vectorized physics for many objects
- **Use for**: Particle systems, physics simulations
- **Integration**: Easy - works alongside Textual

### 4. **Pillow (PIL) ⭐⭐⭐⭐**
- **Why**: Image to ASCII/Unicode conversion
- **Use for**: Loading sprite sheets, image processing
- **Integration**: Easy - preprocessing tool

## Libraries to Study (Not Direct Use)

### 5. **Asciimatics ⭐⭐⭐**
- **Study**: Animation timing, sprite systems
- **Don't use directly**: Conflicts with Textual

### 6. **Pyxel ⭐⭐⭐**
- **Study**: Sprite management, game loop patterns
- **Don't use directly**: Creates its own window

### 7. **TCOD ⭐⭐**
- **Study**: Entity management systems
- **Don't use directly**: Incompatible rendering

## Not Recommended

### 8. **Pygame**
- Requires graphical window, not terminal-compatible

### 9. **Urwid / Prompt Toolkit**
- Complete TUI frameworks that compete with Textual

### 10. **BearLibTerminal**
- Creates pseudo-terminal window, not true terminal

### 11. **Blessed**
- Lower-level than Textual, would cause conflicts

### 12. **TCOD**
- Roguelike-specific, creates own rendering context

## Recommended Architecture

Based on this exploration, here's the recommended approach:

```python
# Core components using recommended libraries

1. Animation Engine (asyncio)
   - Main game loop at 60fps
   - Task-based animation management
   - Precise timing with perf_counter

2. Rendering System (Rich + Textual)
   - Rich renderables for text effects
   - Custom Textual widgets for game canvas
   - Live updates with set_interval

3. Physics System (NumPy - optional)
   - For particle effects (coins, sparkles)
   - Vectorized calculations for performance
   - Only if >50 simultaneous objects

4. Sprite System (Pillow - optional)
   - Convert image sprites to Unicode art
   - Load and process sprite sheets
   - Cache converted frames
```

## Implementation Priority

1. **Start with**: Pure Textual + Rich + asyncio
2. **Add if needed**: NumPy for particle systems
3. **Add if wanted**: Pillow for image sprite support

## Performance Considerations

- Rich + Textual can easily handle 60fps text rendering
- Asyncio provides microsecond-precision timing
- NumPy only needed for 100+ simultaneous physics objects
- Pillow preprocessing keeps runtime performance high

## Example Integration

```python
from textual.app import App
from textual.widgets import Static
from rich.text import Text
import asyncio
import numpy as np  # Only if needed
from PIL import Image  # Only if using image sprites

class GameEngine:
    """Combines all recommended approaches"""
    
    def __init__(self):
        # Core (always needed)
        self.animations = []  # Asyncio-managed
        
        # Optional based on requirements
        self.particle_system = ParticleSystem()  # NumPy
        self.sprite_cache = {}  # Pillow-processed
        
    async def run(self):
        """Main 60fps game loop using asyncio"""
        while True:
            # Update all systems
            await self.update_frame()
            await asyncio.sleep(1/60)
```

## Conclusion

The best approach is to leverage what Textual already provides (Rich, asyncio) and only add specialized libraries (NumPy, Pillow) when specific features require them. This keeps dependencies minimal while maximizing performance and maintainability.
