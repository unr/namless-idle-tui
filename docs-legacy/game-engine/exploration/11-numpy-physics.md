# NumPy for Physics Simulations

## Overview
NumPy can be used to create efficient physics simulations for multiple sprites simultaneously using vectorized operations. This approach is particularly effective for particle systems and large numbers of animated elements.

## Relevance to Our Goals
- **Performance**: Vectorized operations for many sprites
- **Physics**: Efficient physics calculations
- **Particle systems**: Perfect for effects like sparkles, coins
- **Already available**: NumPy is commonly installed

## Key Features
- Vectorized math operations
- Efficient array operations
- Broadcasting for applying forces
- Memory-efficient for large sprite counts

## Code Example
```python
import numpy as np
from textual.widgets import Static
from textual.app import App, ComposeResult

class ParticleSystem:
    def __init__(self, max_particles=1000):
        self.max_particles = max_particles
        self.count = 0
        
        # Pre-allocate arrays for efficiency
        self.positions = np.zeros((max_particles, 2), dtype=np.float32)
        self.velocities = np.zeros((max_particles, 2), dtype=np.float32)
        self.lifetimes = np.zeros(max_particles, dtype=np.float32)
        self.active = np.zeros(max_particles, dtype=bool)
        
    def spawn_burst(self, x, y, count=10):
        """Spawn a burst of particles at position"""
        # Find inactive slots
        inactive = np.where(~self.active)[0]
        if len(inactive) < count:
            count = len(inactive)
        
        if count == 0:
            return
            
        # Assign to inactive slots
        indices = inactive[:count]
        
        # Initialize positions
        self.positions[indices] = [x, y]
        
        # Random velocities in a cone
        angles = np.random.uniform(-np.pi/4, np.pi/4, count)
        speeds = np.random.uniform(5, 15, count)
        self.velocities[indices, 0] = np.cos(angles) * speeds
        self.velocities[indices, 1] = np.sin(angles) * speeds - 10  # Upward bias
        
        # Random lifetimes
        self.lifetimes[indices] = np.random.uniform(1.0, 2.0, count)
        
        # Activate particles
        self.active[indices] = True
        self.count += count
    
    def update(self, dt):
        if self.count == 0:
            return
            
        # Only update active particles
        active_mask = self.active
        
        # Apply gravity (vectorized)
        gravity = np.array([0, 20], dtype=np.float32)
        self.velocities[active_mask] += gravity * dt
        
        # Update positions (vectorized)
        self.positions[active_mask] += self.velocities[active_mask] * dt
        
        # Update lifetimes
        self.lifetimes[active_mask] -= dt
        
        # Deactivate dead particles
        dead = active_mask & (self.lifetimes <= 0)
        self.active[dead] = False
        self.count = np.sum(self.active)
        
        # Bounce off ground
        ground_level = 20
        below_ground = active_mask & (self.positions[:, 1] > ground_level)
        self.positions[below_ground, 1] = ground_level
        self.velocities[below_ground, 1] *= -0.7  # Energy loss
        
    def get_render_positions(self):
        """Get positions of active particles for rendering"""
        if self.count == 0:
            return []
        
        active_positions = self.positions[self.active]
        # Convert to integer screen coordinates
        return np.round(active_positions).astype(int)

class ParticleCanvas(Static):
    def __init__(self):
        super().__init__()
        self.particles = ParticleSystem()
        
    def on_mount(self):
        self.set_interval(1/60, self.update_particles)
        
    def update_particles(self):
        self.particles.update(1/60)
        self.refresh()
    
    def spawn_effect(self, x, y):
        self.particles.spawn_burst(x, y, count=20)
    
    def render(self):
        # Create a text buffer
        width, height = 80, 24
        buffer = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Render particles
        positions = self.particles.get_render_positions()
        for x, y in positions:
            if 0 <= x < width and 0 <= y < height:
                buffer[y][x] = '✨'
        
        # Convert to string
        return '\n'.join(''.join(row) for row in buffer)

class ParticleDemo(App):
    def compose(self) -> ComposeResult:
        yield ParticleCanvas()
    
    def on_key(self, event):
        if event.key == "space":
            canvas = self.query_one(ParticleCanvas)
            canvas.spawn_effect(40, 5)

if __name__ == "__main__":
    app = ParticleDemo()
    app.run()
```

## Pros
- Extremely fast for large numbers of objects
- Vectorized physics calculations
- Memory efficient
- Great for particle effects
- Scientific computing capabilities

## Cons
- Requires NumPy dependency
- Overkill for small sprite counts
- Need to manage memory allocation

## Integration Difficulty
**Low** - NumPy integrates well with any Python application and doesn't interfere with Textual.

## Verdict
**Recommended** for particle systems and scenarios with many animated objects. The performance benefits of vectorization make it ideal for effects.
