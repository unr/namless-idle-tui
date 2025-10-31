# Asyncio-based Animation System

## Overview
Python's built-in asyncio library can be leveraged to create sophisticated animation systems that work well with Textual's async architecture. This approach uses coroutines and tasks for animation timing.

## Relevance to Our Goals
- **Native to Textual**: Textual is built on asyncio
- **Precise timing**: High-resolution timing with asyncio
- **Concurrent animations**: Multiple animations running independently
- **No external dependencies**: Uses Python standard library

## Key Features
- Async/await pattern for animations
- Task-based animation management
- Precise frame timing
- Easy integration with Textual's event system

## Code Example
```python
import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.reactive import reactive
import time

class AnimationEngine:
    def __init__(self):
        self.animations = []
        self.running = False
        
    async def run(self):
        """Main animation loop running at 60fps"""
        self.running = True
        last_time = time.perf_counter()
        
        while self.running:
            current_time = time.perf_counter()
            dt = current_time - last_time
            last_time = current_time
            
            # Update all animations
            for anim in self.animations:
                anim.update(dt)
            
            # Target 60fps (16.67ms per frame)
            frame_time = 1/60
            elapsed = time.perf_counter() - current_time
            if elapsed < frame_time:
                await asyncio.sleep(frame_time - elapsed)
    
    def add_animation(self, animation):
        self.animations.append(animation)
    
    def remove_animation(self, animation):
        if animation in self.animations:
            self.animations.remove(animation)

class BouncingNumber:
    def __init__(self, x, y, value, callback):
        self.x = x
        self.y = y
        self.value = value
        self.velocity_y = -10
        self.callback = callback
        self.alive = True
        
    def update(self, dt):
        if not self.alive:
            return
            
        # Physics update
        gravity = 30
        self.velocity_y += gravity * dt
        self.y += self.velocity_y * dt
        
        # Bounce when hitting ground
        if self.y > 20:
            self.y = 20
            self.velocity_y *= -0.7
            
            # Remove when bounce is too small
            if abs(self.velocity_y) < 1:
                self.alive = False
        
        # Notify widget of update
        self.callback(self)

class GameCanvas(Static):
    def __init__(self):
        super().__init__()
        self.engine = AnimationEngine()
        self.numbers = []
        
    async def on_mount(self):
        # Start animation engine
        asyncio.create_task(self.engine.run())
        
    def spawn_number(self, value):
        number = BouncingNumber(10, 0, value, self.on_animation_update)
        self.numbers.append(number)
        self.engine.add_animation(number)
        
    def on_animation_update(self, animation):
        # Trigger Textual refresh
        self.refresh()
        
        # Remove dead animations
        if not animation.alive:
            self.engine.remove_animation(animation)
            self.numbers.remove(animation)
    
    def render(self):
        # Render current animation state
        output = []
        for number in self.numbers:
            # Position number in text grid
            y_pos = int(number.y)
            x_pos = int(number.x)
            output.append(f"\033[{y_pos};{x_pos}H{number.value}")
        
        return "".join(output)

class IdleGame(App):
    def compose(self) -> ComposeResult:
        yield GameCanvas()
    
    def on_key(self, event):
        if event.key == "space":
            canvas = self.query_one(GameCanvas)
            canvas.spawn_number("100")

if __name__ == "__main__":
    app = IdleGame()
    app.run()
```

## Pros
- Native to Python and Textual
- No external dependencies
- Precise timing control
- Can handle many concurrent animations
- Integrates perfectly with Textual's async architecture

## Cons
- Need to build animation primitives from scratch
- No built-in sprite or physics systems
- Requires understanding of async programming

## Integration Difficulty
**Very Low** - This is the native approach for Textual applications.

## Verdict
**Highly Recommended** - This is the most natural way to add animations to a Textual application. While it requires more manual implementation, it provides the best integration and control.
