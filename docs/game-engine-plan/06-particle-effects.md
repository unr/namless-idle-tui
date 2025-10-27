# Phase 6: Particle Effects

## Objective
Add particle effects system for visual feedback when coins are earned or treasures appear, enhancing the game feel.

## Prerequisites
- Phase 5 complete with working click system

## Tasks

### 6.1 Create Particle System
```python
# src/idle_game/engine/particles.py
import random
import math
from typing import List, Tuple
from dataclasses import dataclass
from .animation import Vector2, Animation

@dataclass
class Particle:
    """Individual particle in a particle system."""
    position: Vector2
    velocity: Vector2
    lifetime: float
    max_lifetime: float
    symbol: str
    color: str = "white"
    gravity: float = 0.0
    fade: bool = True
    
    def update(self, dt: float) -> None:
        """Update particle physics."""
        self.lifetime += dt
        
        # Apply velocity
        self.position = self.position + (self.velocity * dt)
        
        # Apply gravity
        if self.gravity != 0:
            self.velocity.y += self.gravity * dt
    
    def is_alive(self) -> bool:
        """Check if particle is still active."""
        return self.lifetime < self.max_lifetime
    
    def get_symbol(self) -> str:
        """Get current symbol with fading."""
        if not self.fade:
            return self.symbol
            
        # Fade effect based on lifetime
        fade_ratio = self.lifetime / self.max_lifetime
        if fade_ratio > 0.8:
            return "·"
        elif fade_ratio > 0.6:
            return "°"
        return self.symbol

class ParticleEmitter:
    """Emits particles with configurable properties."""
    
    def __init__(self, 
                 position: Vector2,
                 emission_rate: float = 10.0,
                 max_particles: int = 100):
        self.position = position
        self.emission_rate = emission_rate
        self.max_particles = max_particles
        self.particles: List[Particle] = []
        
        # Emission properties
        self.speed_min = 5.0
        self.speed_max = 10.0
        self.angle_min = -math.pi
        self.angle_max = math.pi
        self.lifetime_min = 0.5
        self.lifetime_max = 1.5
        self.symbols = ["✨", "·", "°", "*"]
        self.gravity = 0.0
        
        # Timing
        self.emission_accumulator = 0.0
        self.active = True
    
    def emit_particle(self) -> None:
        """Emit a single particle."""
        if len(self.particles) >= self.max_particles:
            return
            
        # Random properties
        angle = random.uniform(self.angle_min, self.angle_max)
        speed = random.uniform(self.speed_min, self.speed_max)
        
        velocity = Vector2(
            math.cos(angle) * speed,
            math.sin(angle) * speed
        )
        
        particle = Particle(
            position=Vector2(self.position.x, self.position.y),
            velocity=velocity,
            lifetime=0.0,
            max_lifetime=random.uniform(self.lifetime_min, self.lifetime_max),
            symbol=random.choice(self.symbols),
            gravity=self.gravity
        )
        
        self.particles.append(particle)
    
    def burst(self, count: int) -> None:
        """Emit a burst of particles."""
        for _ in range(min(count, self.max_particles - len(self.particles))):
            self.emit_particle()
    
    def update(self, dt: float) -> None:
        """Update emitter and all particles."""
        if self.active:
            # Handle continuous emission
            self.emission_accumulator += dt * self.emission_rate
            
            while self.emission_accumulator >= 1.0:
                self.emit_particle()
                self.emission_accumulator -= 1.0
        
        # Update all particles
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.particles.remove(particle)
    
    def render_to_grid(self, grid: List[List[str]], 
                      width: int, height: int) -> None:
        """Render particles to a character grid."""
        for particle in self.particles:
            x = int(particle.position.x)
            y = int(particle.position.y)
            
            if 0 <= x < width and 0 <= y < height:
                grid[y][x] = particle.get_symbol()

class ParticleEffects:
    """Predefined particle effects."""
    
    @staticmethod
    def sparkle_burst(x: int, y: int) -> ParticleEmitter:
        """Create a sparkle burst effect."""
        emitter = ParticleEmitter(Vector2(x, y))
        emitter.symbols = ["✨", "✦", "✧", "⋆"]
        emitter.speed_min = 3
        emitter.speed_max = 8
        emitter.lifetime_min = 0.3
        emitter.lifetime_max = 0.8
        emitter.active = False  # One-shot burst
        emitter.burst(15)
        return emitter
    
    @staticmethod
    def gold_fountain(x: int, y: int) -> ParticleEmitter:
        """Create a gold fountain effect."""
        emitter = ParticleEmitter(Vector2(x, y))
        emitter.symbols = ["💰", "¢", "°", "·"]
        emitter.angle_min = -math.pi * 0.75  # Upward cone
        emitter.angle_max = -math.pi * 0.25
        emitter.speed_min = 8
        emitter.speed_max = 12
        emitter.gravity = 15
        emitter.emission_rate = 5
        return emitter
    
    @staticmethod
    def treasure_sparkles(x: int, y: int) -> ParticleEmitter:
        """Create treasure chest sparkle effect."""
        emitter = ParticleEmitter(Vector2(x, y))
        emitter.symbols = ["⋆", "★", "☆", "✦"]
        emitter.speed_min = 1
        emitter.speed_max = 3
        emitter.lifetime_min = 1.0
        emitter.lifetime_max = 2.0
        emitter.emission_rate = 2
        return emitter
```

### 6.2 Integrate Particles with Game Canvas
```python
# Update src/idle_game/widgets/game_canvas.py to include particles
from ..engine.particles import ParticleEmitter, ParticleEffects

class GameCanvas(Static):
    """Main game display area with particles."""
    
    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
        self.animation_manager = AnimationManager(60, 20)
        self.particle_emitters: List[ParticleEmitter] = []
        
        # Previous initialization...
    
    def spawn_particle_effect(self, effect_type: str, x: int, y: int) -> None:
        """Spawn a particle effect."""
        if effect_type == "sparkle":
            emitter = ParticleEffects.sparkle_burst(x, y)
        elif effect_type == "fountain":
            emitter = ParticleEffects.gold_fountain(x, y)
        elif effect_type == "treasure":
            emitter = ParticleEffects.treasure_sparkles(x, y)
        else:
            return
            
        self.particle_emitters.append(emitter)
        
        # Auto-remove after duration
        if not emitter.active:  # One-shot effects
            self.set_timer(2.0, lambda: self.remove_emitter(emitter))
    
    def remove_emitter(self, emitter: ParticleEmitter) -> None:
        """Remove an emitter."""
        if emitter in self.particle_emitters:
            self.particle_emitters.remove(emitter)
    
    def on_gold_earned(self, amount: Decimal, source: str) -> None:
        """Handle gold earned with particles."""
        x = random.randint(20, 40)
        y = random.randint(3, 8)
        
        # Existing coin animation
        effect = CoinWithValue(int(amount), x, y, source)
        for anim in effect.get_animations():
            self.animation_manager.add_animation(anim)
        
        # Add particle effects based on source
        if source == "passive":
            self.spawn_particle_effect("sparkle", x, y)
        elif source == "click":
            self.spawn_particle_effect("sparkle", x, y)
            if amount >= 50:
                self.spawn_particle_effect("fountain", x, y + 2)
        elif source == "bonus":
            self.spawn_particle_effect("fountain", x, y)
    
    def update_frame(self) -> None:
        """Update all visual elements."""
        # Update animations
        self.animation_manager.update(1/60)
        
        # Update particle systems
        for emitter in self.particle_emitters[:]:
            emitter.update(1/60)
            if not emitter.active and len(emitter.particles) == 0:
                self.particle_emitters.remove(emitter)
        
        self.update_display()
    
    def update_display(self) -> None:
        """Render everything including particles."""
        width, height = 60, 20
        
        # Create base grid
        grid = [[" " for _ in range(width)] for _ in range(height)]
        
        # Render animations first
        anim_grid = self.animation_manager.render_to_grid()
        for y in range(min(height, len(anim_grid))):
            for x in range(min(width, len(anim_grid[y]))):
                if anim_grid[y][x] != " ":
                    grid[y][x] = anim_grid[y][x]
        
        # Render particles on top
        for emitter in self.particle_emitters:
            emitter.render_to_grid(grid, width, height)
        
        # Convert grid to lines
        lines = ["".join(row) for row in grid[:10]]
        
        # Add gold counter
        lines.append("─" * width)
        lines.append(f"💰 Gold: {int(self.gold)}".center(width))
        lines.append(f"📈 Rate: {self.game_state.passive_rate}/sec".center(width))
        lines.append("─" * width)
        
        # Add bottom area
        for row in grid[14:]:
            lines.append("".join(row))
        
        # Create display
        display = Text("\n".join(lines))
        panel = Panel(display, title="💎 Gold Mine 💎", border_style="yellow")
        
        self.update(panel)
```

### 6.3 Add Treasure Particle Effects
```python
# src/idle_game/engine/treasure_effects.py
from .particles import ParticleEmitter, Vector2
import math
import random

class TreasureGlow:
    """Glowing effect for treasure chests."""
    
    def __init__(self, x: int, y: int):
        self.emitters = []
        
        # Create ring of sparkles
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            offset_x = math.cos(rad) * 3
            offset_y = math.sin(rad) * 2
            
            emitter = ParticleEmitter(
                Vector2(x + offset_x, y + offset_y)
            )
            emitter.symbols = ["·", "°", "∘"]
            emitter.speed_min = 0.5
            emitter.speed_max = 1.5
            emitter.emission_rate = 0.5
            emitter.lifetime_min = 0.5
            emitter.lifetime_max = 1.0
            
            self.emitters.append(emitter)
    
    def update(self, dt: float) -> None:
        for emitter in self.emitters:
            emitter.update(dt)
    
    def get_particles(self):
        particles = []
        for emitter in self.emitters:
            particles.extend(emitter.particles)
        return particles
```

## Tests to Write

### Test Particle System
```python
# tests/test_particles.py
import pytest
from src.idle_game.engine.particles import (
    Particle, ParticleEmitter, ParticleEffects, Vector2
)

def test_particle_lifetime():
    particle = Particle(
        position=Vector2(0, 0),
        velocity=Vector2(1, 1),
        lifetime=0,
        max_lifetime=1.0,
        symbol="*"
    )
    
    assert particle.is_alive()
    
    particle.update(0.5)
    assert particle.is_alive()
    assert particle.position.x == pytest.approx(0.5)
    
    particle.update(0.6)
    assert not particle.is_alive()

def test_particle_gravity():
    particle = Particle(
        position=Vector2(0, 0),
        velocity=Vector2(0, 0),
        lifetime=0,
        max_lifetime=10,
        symbol="*",
        gravity=10
    )
    
    particle.update(1.0)
    assert particle.velocity.y == 10
    assert particle.position.y == 10

def test_emitter_burst():
    emitter = ParticleEmitter(Vector2(10, 10))
    emitter.burst(20)
    
    assert len(emitter.particles) == 20
    
    # Update and check particles move
    initial_positions = [(p.position.x, p.position.y) for p in emitter.particles]
    emitter.update(0.1)
    
    moved = False
    for i, particle in enumerate(emitter.particles):
        if (particle.position.x, particle.position.y) != initial_positions[i]:
            moved = True
            break
    
    assert moved

def test_particle_effects_presets():
    # Test sparkle burst
    sparkles = ParticleEffects.sparkle_burst(10, 10)
    assert len(sparkles.particles) > 0
    assert not sparkles.active  # Should be one-shot
    
    # Test fountain
    fountain = ParticleEffects.gold_fountain(10, 10)
    assert fountain.active  # Should be continuous
    assert fountain.gravity > 0  # Should have gravity

def test_particle_rendering():
    emitter = ParticleEmitter(Vector2(5, 5))
    emitter.emit_particle()
    
    grid = [[" " for _ in range(10)] for _ in range(10)]
    emitter.render_to_grid(grid, 10, 10)
    
    # Should have rendered something
    rendered = False
    for row in grid:
        if any(cell != " " for cell in row):
            rendered = True
            break
    
    assert rendered
```

## Success Criteria
- [ ] Sparkle effects on gold earn
- [ ] Fountain effect for large rewards
- [ ] Particles render correctly
- [ ] Performance stays good with many particles
- [ ] Old particles cleaned up properly
- [ ] Visual effects enhance gameplay

## Commands to Run
```bash
# Run the app
python -m src.idle_game.app

# Run tests
pytest tests/test_particles.py -v

# Performance test with many particles
python -c "
from src.idle_game.engine.particles import ParticleEmitter, Vector2
import time

emitters = [ParticleEmitter(Vector2(i*10, j*10)) 
            for i in range(5) for j in range(5)]

start = time.perf_counter()
for _ in range(600):  # 10 seconds at 60fps
    for e in emitters:
        e.update(1/60)
elapsed = time.perf_counter() - start
print(f'Processed 25 emitters for 10s in {elapsed:.2f}s')
"
```

## Next Phase
Once particle effects are working, proceed to Phase 7: Treasure System.
