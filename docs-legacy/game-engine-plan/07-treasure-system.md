# Phase 7: Treasure System  

## Objective
Implement treasure chest display system that shows one chest for every 100 gold, with spawn animations and persistent display.

## Prerequisites
- Phase 6 complete with particle effects

## Tasks

### 7.1 Create Treasure Chest Sprite
```python
# src/idle_game/engine/treasure.py
from dataclasses import dataclass
from typing import List, Tuple
from .animation import Sprite, Vector2
from .particles import ParticleEmitter
import random
import math

@dataclass
class TreasureChest:
    """A treasure chest with position and animation state."""
    
    position: Vector2
    index: int  # Which chest number this is
    spawn_time: float = 0.0
    
    # ASCII art for chest
    CHEST_CLOSED = ["╔═══╗", "║▓▓▓║", "╚═══╝"]
    CHEST_OPEN = ["╔═══╗", "║ ✦ ║", "╚═══╝"]
    CHEST_MINI = "📦"
    
    def __init__(self, index: int, x: int, y: int):
        self.position = Vector2(x, y)
        self.index = index
        self.spawn_time = 0.0
        self.is_new = True
        self.sparkle_emitter = None
        
    def update(self, dt: float) -> None:
        """Update chest animation."""
        self.spawn_time += dt
        
        # New chest animation phase
        if self.is_new and self.spawn_time > 1.0:
            self.is_new = False
    
    def get_display(self) -> List[str]:
        """Get current chest display."""
        if self.spawn_time < 0.5:
            # Spawning animation
            progress = self.spawn_time / 0.5
            if progress < 0.33:
                return ["···", "···", "···"]
            elif progress < 0.66:
                return ["┌─┐", "│ │", "└─┘"]
            else:
                return self.CHEST_CLOSED
        else:
            return self.CHEST_CLOSED if not self.is_new else self.CHEST_OPEN
    
    def get_mini_display(self) -> str:
        """Get compact display for many chests."""
        return self.CHEST_MINI

class TreasureManager:
    """Manages all treasure chests in the game."""
    
    def __init__(self, width: int = 60, height: int = 20):
        self.chests: List[TreasureChest] = []
        self.width = width
        self.height = height
        self.last_chest_count = 0
        self.spawn_animations = []
        
        # Layout configuration
        self.chest_rows = 3
        self.chest_cols = 10
        self.chest_spacing = 6
        self.chest_start_x = 5
        self.chest_start_y = 15
        
    def update_chest_count(self, target_count: int) -> List[TreasureChest]:
        """Update number of chests, returning newly spawned ones."""
        new_chests = []
        
        if target_count > self.last_chest_count:
            # Spawn new chests
            for i in range(self.last_chest_count, target_count):
                chest = self.spawn_chest(i)
                new_chests.append(chest)
                
            self.last_chest_count = target_count
            
        elif target_count < self.last_chest_count:
            # Remove chests (shouldn't happen in normal gameplay)
            self.chests = self.chests[:target_count]
            self.last_chest_count = target_count
            
        return new_chests
    
    def spawn_chest(self, index: int) -> TreasureChest:
        """Spawn a new chest with animation."""
        # Calculate position in grid
        row = index // self.chest_cols
        col = index % self.chest_cols
        
        x = self.chest_start_x + (col * self.chest_spacing)
        y = self.chest_start_y + (row * 4)  # 4 lines per chest row
        
        # Wrap around if too many chests
        if y >= self.height - 3:
            y = self.chest_start_y
            x = (x + 2) % (self.width - 5)
        
        chest = TreasureChest(index, x, y)
        self.chests.append(chest)
        
        # Create spawn animation
        self.create_spawn_animation(chest)
        
        return chest
    
    def create_spawn_animation(self, chest: TreasureChest) -> None:
        """Create spawn animation for a chest."""
        spawn_effect = ChestSpawnEffect(chest.position.x, chest.position.y)
        self.spawn_animations.append(spawn_effect)
    
    def update(self, dt: float) -> None:
        """Update all chests and animations."""
        # Update chests
        for chest in self.chests:
            chest.update(dt)
        
        # Update spawn animations
        for anim in self.spawn_animations[:]:
            anim.update(dt)
            if anim.is_complete():
                self.spawn_animations.remove(anim)
    
    def render_to_grid(self, grid: List[List[str]]) -> None:
        """Render all chests to grid."""
        for chest in self.chests:
            x = int(chest.position.x)
            y = int(chest.position.y)
            
            if len(self.chests) > 20:
                # Use mini display for many chests
                if 0 <= x < len(grid[0]) and 0 <= y < len(grid):
                    grid[y][x] = chest.get_mini_display()
            else:
                # Use full display for few chests
                lines = chest.get_display()
                for i, line in enumerate(lines):
                    if 0 <= y + i < len(grid):
                        for j, char in enumerate(line):
                            if 0 <= x + j < len(grid[0]):
                                grid[y + i][x + j] = char

class ChestSpawnEffect:
    """Animation effect when a chest spawns."""
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.duration = 1.5
        self.elapsed = 0.0
        self.particles = []
        
        # Create particle burst
        for i in range(8):
            angle = (2 * math.pi * i) / 8
            self.particles.append({
                'x': x + 2,  # Center of chest
                'y': y + 1,
                'vx': math.cos(angle) * 10,
                'vy': math.sin(angle) * 10,
                'symbol': '✦'
            })
    
    def update(self, dt: float) -> None:
        """Update spawn effect."""
        self.elapsed += dt
        
        # Update particles
        for particle in self.particles:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['vx'] *= 0.95  # Damping
            particle['vy'] *= 0.95
    
    def is_complete(self) -> bool:
        return self.elapsed >= self.duration
    
    def render_to_grid(self, grid: List[List[str]]) -> None:
        """Render effect to grid."""
        if self.elapsed < self.duration:
            for particle in self.particles:
                x = int(particle['x'])
                y = int(particle['y'])
                if 0 <= x < len(grid[0]) and 0 <= y < len(grid):
                    # Fade based on time
                    if self.elapsed < 0.5:
                        grid[y][x] = particle['symbol']
                    elif self.elapsed < 1.0:
                        grid[y][x] = '·'
```

### 7.2 Integrate Treasure System with Game Canvas
```python
# Update src/idle_game/widgets/game_canvas.py
from ..engine.treasure import TreasureManager

class GameCanvas(Static):
    """Main game display area with treasures."""
    
    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
        self.animation_manager = AnimationManager(60, 20)
        self.particle_emitters = []
        self.treasure_manager = TreasureManager(60, 20)
        
        # Track chest count
        self.current_chest_count = 0
        
        # Previous initialization...
    
    def check_treasure_spawns(self) -> None:
        """Check if new treasures should spawn."""
        target_count = self.game_state.get_chest_count()
        
        if target_count != self.current_chest_count:
            new_chests = self.treasure_manager.update_chest_count(target_count)
            
            # Spawn effects for new chests
            for chest in new_chests:
                # Particle burst at chest location
                self.spawn_particle_effect(
                    "treasure", 
                    int(chest.position.x) + 2, 
                    int(chest.position.y) + 1
                )
                
                # Floating text announcement
                text_anim = FloatingText(
                    "TREASURE!", 
                    int(chest.position.x),
                    int(chest.position.y) - 2
                )
                text_anim.duration = 2.0
                self.animation_manager.add_animation(text_anim)
            
            self.current_chest_count = target_count
    
    def update_frame(self) -> None:
        """Update all visual elements."""
        # Check for new treasures
        self.check_treasure_spawns()
        
        # Update systems
        self.animation_manager.update(1/60)
        self.treasure_manager.update(1/60)
        
        for emitter in self.particle_emitters[:]:
            emitter.update(1/60)
            if not emitter.active and len(emitter.particles) == 0:
                self.particle_emitters.remove(emitter)
        
        self.update_display()
    
    def update_display(self) -> None:
        """Render everything including treasures."""
        width, height = 60, 20
        
        # Create base grid
        grid = [[" " for _ in range(width)] for _ in range(height)]
        
        # Render treasures first (background layer)
        self.treasure_manager.render_to_grid(grid)
        
        # Render treasure spawn effects
        for anim in self.treasure_manager.spawn_animations:
            anim.render_to_grid(grid)
        
        # Render animations
        anim_grid = self.animation_manager.render_to_grid()
        for y in range(min(height, len(anim_grid))):
            for x in range(min(width, len(anim_grid[y]))):
                if anim_grid[y][x] != " ":
                    grid[y][x] = anim_grid[y][x]
        
        # Render particles on top
        for emitter in self.particle_emitters:
            emitter.render_to_grid(grid, width, height)
        
        # Build display
        lines = []
        
        # Top area (animations and effects)
        for row in grid[:10]:
            lines.append("".join(row))
        
        # Gold counter section
        lines.append("═" * width)
        lines.append(f"💰 Gold: {int(self.gold)}".center(width))
        lines.append(f"📈 Rate: {self.game_state.passive_rate}/sec".center(width))
        lines.append(f"📦 Treasures: {self.current_chest_count}".center(width))
        lines.append("═" * width)
        
        # Bottom area (treasure chests)
        for row in grid[15:]:
            lines.append("".join(row))
        
        # Create display
        display = Text("\n".join(lines))
        panel = Panel(display, title="💎 Gold Mine 💎", border_style="yellow")
        
        self.update(panel)
```

## Tests to Write

### Test Treasure System
```python
# tests/test_treasure.py
import pytest
from decimal import Decimal
from src.idle_game.engine.treasure import TreasureChest, TreasureManager
from src.idle_game.core.game_state import GameState

def test_treasure_chest_creation():
    chest = TreasureChest(0, 10, 10)
    assert chest.index == 0
    assert chest.position.x == 10
    assert chest.position.y == 10
    assert chest.is_new

def test_treasure_chest_animation():
    chest = TreasureChest(0, 10, 10)
    
    # Initial state
    display = chest.get_display()
    assert len(display) == 3
    
    # After spawn animation
    chest.update(1.5)
    assert not chest.is_new
    display = chest.get_display()
    assert display == chest.CHEST_CLOSED

def test_treasure_manager_spawning():
    manager = TreasureManager()
    
    # Spawn 3 chests
    new_chests = manager.update_chest_count(3)
    assert len(new_chests) == 3
    assert len(manager.chests) == 3
    
    # Check positions are different
    positions = [(c.position.x, c.position.y) for c in manager.chests]
    assert len(set(positions)) == 3  # All unique

def test_treasure_threshold():
    state = GameState()
    
    # No chests initially
    assert state.get_chest_count() == 0
    
    # Add 99 gold - still no chest
    state.gold = Decimal("99")
    assert state.get_chest_count() == 0
    
    # Add 100 gold - one chest
    state.gold = Decimal("100")
    assert state.get_chest_count() == 1
    
    # Add 250 gold - two chests
    state.gold = Decimal("250")
    assert state.get_chest_count() == 2
    
    # Add 1000 gold - ten chests
    state.gold = Decimal("1000")
    assert state.get_chest_count() == 10

def test_treasure_grid_rendering():
    manager = TreasureManager()
    manager.update_chest_count(2)
    
    # Create grid
    grid = [[" " for _ in range(60)] for _ in range(20)]
    
    # Render chests
    manager.render_to_grid(grid)
    
    # Check something was rendered
    rendered = False
    for row in grid:
        if any(c != " " for c in row):
            rendered = True
            break
    
    assert rendered
```

## Success Criteria
- [ ] Treasure chests appear at 100 gold intervals
- [ ] Spawn animation plays for new chests
- [ ] Chests persist on screen
- [ ] Particle effects on spawn
- [ ] Layout handles many chests gracefully
- [ ] Chest count displayed in UI

## Commands to Run
```bash
# Run the app
python -m src.idle_game.app

# Run tests
pytest tests/test_treasure.py -v

# Test with many chests
python -c "
from src.idle_game.core.game_state import GameState
from src.idle_game.engine.treasure import TreasureManager

state = GameState()
state.gold = 5000  # Should create 50 chests
manager = TreasureManager()
manager.update_chest_count(state.get_chest_count())
print(f'Created {len(manager.chests)} treasure chests')
"
```

## Next Phase
Once treasure system is complete, proceed to Phase 8: Progressive Features.
