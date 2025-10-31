# Phase 3: Animation Engine

## Objective
Build a flexible animation system that can handle sprites, movement, and timing for visual effects in the terminal.

## Prerequisites
- Phase 2 complete with working passive income system

## Tasks

### 3.1 Create Base Animation Classes
```python
# src/idle_game/engine/animation.py
from dataclasses import dataclass
from typing import Optional, Tuple, List, Callable
from abc import ABC, abstractmethod
import time

@dataclass
class Vector2:
    """2D vector for positions and velocities."""
    x: float
    y: float
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __mul__(self, scalar: float):
        return Vector2(self.x * scalar, self.y * scalar)

class Animation(ABC):
    """Base class for all animations."""
    
    def __init__(self, duration: float = 1.0):
        self.duration = duration
        self.elapsed = 0.0
        self.active = True
        self.on_complete: Optional[Callable] = None
    
    @abstractmethod
    def update(self, dt: float) -> None:
        """Update animation state."""
        pass
    
    @abstractmethod
    def render(self) -> str:
        """Return current animation frame as string."""
        pass
    
    def is_complete(self) -> bool:
        """Check if animation is complete."""
        return self.elapsed >= self.duration
    
    def reset(self) -> None:
        """Reset animation to start."""
        self.elapsed = 0.0
        self.active = True

class Sprite(Animation):
    """Animated sprite that moves across the screen."""
    
    def __init__(self, 
                 position: Vector2,
                 velocity: Vector2,
                 symbol: str = "O",
                 duration: float = 2.0,
                 gravity: float = 0.0):
        super().__init__(duration)
        self.start_position = position
        self.position = Vector2(position.x, position.y)
        self.velocity = velocity
        self.symbol = symbol
        self.gravity = gravity
        
    def update(self, dt: float) -> None:
        """Update sprite position with physics."""
        if not self.active:
            return
            
        self.elapsed += dt
        
        # Apply velocity
        self.position = self.position + (self.velocity * dt)
        
        # Apply gravity to velocity
        if self.gravity != 0:
            self.velocity.y += self.gravity * dt
        
        # Mark complete when duration elapsed
        if self.is_complete():
            self.active = False
            if self.on_complete:
                self.on_complete()
    
    def render(self) -> str:
        """Render sprite at current position."""
        if not self.active:
            return ""
        return self.symbol
    
    def get_position(self) -> Tuple[int, int]:
        """Get integer screen position."""
        return (int(self.position.x), int(self.position.y))
```

### 3.2 Create Animation Manager
```python
# src/idle_game/engine/animation_manager.py
from typing import List, Dict, Tuple
import asyncio
from .animation import Animation, Sprite, Vector2

class AnimationManager:
    """Manages all active animations in the game."""
    
    def __init__(self, width: int = 80, height: int = 24):
        self.animations: List[Animation] = []
        self.width = width
        self.height = height
        self.running = False
        
    def add_animation(self, animation: Animation) -> None:
        """Add an animation to be managed."""
        self.animations.append(animation)
        
    def remove_animation(self, animation: Animation) -> None:
        """Remove an animation from management."""
        if animation in self.animations:
            self.animations.remove(animation)
    
    def update(self, dt: float) -> None:
        """Update all animations."""
        # Update each animation
        for anim in self.animations[:]:  # Copy list to allow removal during iteration
            anim.update(dt)
            
            # Remove completed animations
            if not anim.active:
                self.animations.remove(anim)
    
    def render_to_grid(self) -> List[List[str]]:
        """Render all animations to a 2D grid."""
        # Create empty grid
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]
        
        # Render each sprite
        for anim in self.animations:
            if isinstance(anim, Sprite) and anim.active:
                x, y = anim.get_position()
                # Bounds check
                if 0 <= x < self.width and 0 <= y < self.height:
                    symbol = anim.render()
                    if symbol:
                        grid[y][x] = symbol
        
        return grid
    
    def render_to_string(self) -> str:
        """Render all animations to a string."""
        grid = self.render_to_grid()
        return "\n".join("".join(row) for row in grid)
    
    async def run_async(self, fps: int = 60) -> None:
        """Run animation loop asynchronously."""
        self.running = True
        frame_time = 1.0 / fps
        
        while self.running:
            start = asyncio.get_event_loop().time()
            
            # Update all animations
            self.update(frame_time)
            
            # Calculate sleep time to maintain FPS
            elapsed = asyncio.get_event_loop().time() - start
            sleep_time = max(0, frame_time - elapsed)
            await asyncio.sleep(sleep_time)
    
    def stop(self) -> None:
        """Stop the animation loop."""
        self.running = False
    
    def clear(self) -> None:
        """Remove all animations."""
        self.animations.clear()
```

### 3.3 Create Specific Animation Types
```python
# src/idle_game/engine/effects.py
from .animation import Sprite, Vector2
import random
import math

class FloatingText(Sprite):
    """Text that floats up and fades out."""
    
    def __init__(self, text: str, x: int, y: int):
        # Float upward with slight random horizontal drift
        velocity = Vector2(
            random.uniform(-2, 2),  # Slight horizontal drift
            -10  # Upward velocity
        )
        
        super().__init__(
            position=Vector2(x, y),
            velocity=velocity,
            symbol=text,
            duration=1.5,
            gravity=5  # Slow down as it rises
        )
        
        self.fade_start = 0.7  # Start fading at 70% of duration
        self.original_symbol = text
    
    def render(self) -> str:
        """Render with fading effect."""
        if not self.active:
            return ""
            
        # Fade out in the last 30% of animation
        if self.elapsed > self.fade_start * self.duration:
            fade_progress = (self.elapsed - self.fade_start * self.duration) / (0.3 * self.duration)
            if fade_progress > 0.5:
                return "·"  # Faded symbol
        
        return self.original_symbol

class BouncingCoin(Sprite):
    """Coin that bounces with physics."""
    
    def __init__(self, x: int, y: int):
        super().__init__(
            position=Vector2(x, y),
            velocity=Vector2(random.uniform(-5, 5), -15),
            symbol="¢",
            duration=3.0,
            gravity=30
        )
        
        self.bounce_damping = 0.7
        self.ground_level = 20
        
    def update(self, dt: float) -> None:
        """Update with bounce physics."""
        super().update(dt)
        
        # Bounce off ground
        if self.position.y >= self.ground_level and self.velocity.y > 0:
            self.position.y = self.ground_level
            self.velocity.y *= -self.bounce_damping
            
            # Stop bouncing if velocity is too small
            if abs(self.velocity.y) < 1:
                self.velocity.y = 0
                self.velocity.x *= 0.9  # Friction

class SpinningCoin(Sprite):
    """Coin that spins in place."""
    
    FRAMES = ["O", "0", "o", "·", "o", "0"]
    
    def __init__(self, x: int, y: int):
        super().__init__(
            position=Vector2(x, y),
            velocity=Vector2(0, 0),
            symbol=self.FRAMES[0],
            duration=1.0
        )
        self.frame_index = 0
        self.frame_time = 0.0
        self.frame_duration = self.duration / len(self.FRAMES)
    
    def update(self, dt: float) -> None:
        """Update animation frame."""
        super().update(dt)
        
        if not self.active:
            return
            
        self.frame_time += dt
        
        if self.frame_time >= self.frame_duration:
            self.frame_time -= self.frame_duration
            self.frame_index = (self.frame_index + 1) % len(self.FRAMES)
            self.symbol = self.FRAMES[self.frame_index]
```

### 3.4 Integrate with Game Canvas
```python
# Update src/idle_game/widgets/game_canvas.py
from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
from rich.align import Align
from rich.panel import Panel
from decimal import Decimal
import time
from ..engine.animation_manager import AnimationManager
from ..engine.effects import FloatingText, SpinningCoin

class GameCanvas(Static):
    """Main game display area with animations."""
    
    gold = reactive(Decimal("0"))
    
    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
        self.animation_manager = AnimationManager(70, 20)  # Canvas size
        
        # Register for gold earned events
        game_state.on_gold_earned.append(self.on_gold_earned)
    
    def on_mount(self) -> None:
        """Set up the game canvas when mounted."""
        self.update_display()
        # Start update timers
        self.set_interval(1/60, self.update_frame)
        self.set_interval(1.0, self.check_passive_income)
    
    def update_frame(self) -> None:
        """Update animation frame."""
        self.animation_manager.update(1/60)
        self.update_display()
    
    def check_passive_income(self) -> None:
        """Check for passive income updates."""
        current_time = time.perf_counter()
        gold_earned = self.game_state.update(current_time)
        
        if gold_earned > 0:
            self.gold = self.game_state.gold
    
    def on_gold_earned(self, amount: Decimal, source: str) -> None:
        """Handle gold earned event with animation."""
        # Spawn floating text
        text_anim = FloatingText(f"+{int(amount)}", 35, 10)
        self.animation_manager.add_animation(text_anim)
        
        # Spawn spinning coin
        coin_anim = SpinningCoin(35, 8)
        self.animation_manager.add_animation(coin_anim)
    
    def watch_gold(self, old_value: Decimal, new_value: Decimal) -> None:
        """React to gold changes."""
        # Animation is triggered by event, just update display
        pass
    
    def update_display(self) -> None:
        """Update the canvas display with animations."""
        # Get animation grid
        anim_lines = self.animation_manager.render_to_string().split('\n')
        
        # Overlay gold counter in center
        gold_text = f"💰 Gold: {int(self.gold)}"
        rate_text = f"📈 Rate: {self.game_state.passive_rate}/sec"
        
        # Create display with animations
        display = Text()
        
        # Add animation lines
        for i, line in enumerate(anim_lines[:10]):  # Top half
            display.append(line + "\n")
        
        # Add gold counter in middle
        display.append(Text(gold_text.center(70), style="bold yellow"))
        display.append("\n")
        display.append(Text(rate_text.center(70), style="dim cyan"))
        display.append("\n")
        
        # Add remaining animation lines
        for line in anim_lines[13:]:  # Bottom half
            display.append(line + "\n")
        
        self.update(display)
    
    def add_gold(self, amount: Decimal) -> None:
        """Add gold with visual feedback."""
        self.gold = self.game_state.add_gold(amount)
        # Trigger animation through event
        for callback in self.game_state.on_gold_earned:
            callback(amount, "click")
```

## Tests to Write

### Test Animation System
```python
# tests/test_animation.py
import pytest
from src.idle_game.engine.animation import Vector2, Sprite
from src.idle_game.engine.animation_manager import AnimationManager

def test_vector2_operations():
    v1 = Vector2(1, 2)
    v2 = Vector2(3, 4)
    
    # Test addition
    v3 = v1 + v2
    assert v3.x == 4
    assert v3.y == 6
    
    # Test scalar multiplication
    v4 = v1 * 2
    assert v4.x == 2
    assert v4.y == 4

def test_sprite_physics():
    sprite = Sprite(
        position=Vector2(10, 10),
        velocity=Vector2(5, -10),
        gravity=20
    )
    
    # Update for 0.1 seconds
    sprite.update(0.1)
    
    # Check position updated
    assert sprite.position.x == pytest.approx(10.5, rel=1e-3)
    assert sprite.position.y == pytest.approx(9.0, rel=1e-3)
    
    # Check gravity applied
    assert sprite.velocity.y == pytest.approx(-8.0, rel=1e-3)

def test_animation_manager():
    manager = AnimationManager(80, 24)
    
    # Add some sprites
    sprite1 = Sprite(Vector2(10, 10), Vector2(0, 0), "X")
    sprite2 = Sprite(Vector2(20, 20), Vector2(0, 0), "O")
    
    manager.add_animation(sprite1)
    manager.add_animation(sprite2)
    
    assert len(manager.animations) == 2
    
    # Update and check grid rendering
    manager.update(0.1)
    grid = manager.render_to_grid()
    
    assert grid[10][10] == "X"
    assert grid[20][20] == "O"

def test_animation_completion():
    sprite = Sprite(Vector2(0, 0), Vector2(0, 0), duration=1.0)
    
    # Update past duration
    sprite.update(1.5)
    
    assert sprite.is_complete()
    assert not sprite.active
```

## Success Criteria
- [ ] Animations update at 60fps smoothly
- [ ] Floating text appears when gold is earned
- [ ] Coins spin during animation
- [ ] Animations don't interfere with game state
- [ ] Memory usage stays stable (no leaks)
- [ ] All animation tests pass

## Commands to Run
```bash
# Run the app
python -m src.idle_game.app

# Run tests
pytest tests/test_animation.py -v

# Check for memory leaks
python -m tracemalloc src/idle_game/app.py
```

## Next Phase
Once animations are working, proceed to Phase 4: Gold Coin Animation.
