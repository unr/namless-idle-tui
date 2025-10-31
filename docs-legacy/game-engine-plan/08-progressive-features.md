# Phase 8: Progressive Features

## Objective
Implement progressive gameplay features including the +50 gold button unlock at 500 gold with dramatic unlock animation.

## Prerequisites
- Phase 7 complete with treasure system

## Tasks

### 8.1 Create Unlock System
```python
# src/idle_game/core/unlocks.py
from dataclasses import dataclass
from decimal import Decimal
from typing import Callable, Optional, List
from enum import Enum

class UnlockType(Enum):
    BUTTON = "button"
    UPGRADE = "upgrade"
    FEATURE = "feature"
    ACHIEVEMENT = "achievement"

@dataclass
class Unlock:
    """Represents an unlockable feature."""
    
    id: str
    name: str
    description: str
    unlock_type: UnlockType
    requirement: Decimal
    unlocked: bool = False
    on_unlock: Optional[Callable] = None
    
    def check_unlock(self, gold: Decimal) -> bool:
        """Check if this should be unlocked."""
        if not self.unlocked and gold >= self.requirement:
            self.unlocked = True
            if self.on_unlock:
                self.on_unlock()
            return True
        return False

class UnlockManager:
    """Manages all game unlocks and progression."""
    
    def __init__(self):
        self.unlocks: List[Unlock] = []
        self.recent_unlocks: List[Unlock] = []
        self.initialize_unlocks()
        
    def initialize_unlocks(self) -> None:
        """Set up all game unlocks."""
        self.unlocks = [
            Unlock(
                id="button_50",
                name="Mega Click",
                description="Unlock the +50 gold button",
                unlock_type=UnlockType.BUTTON,
                requirement=Decimal("500")
            ),
            Unlock(
                id="button_100",
                name="Ultra Click",
                description="Unlock the +100 gold button",
                unlock_type=UnlockType.BUTTON,
                requirement=Decimal("2000")
            ),
            Unlock(
                id="auto_clicker",
                name="Auto Clicker",
                description="Automatically clicks once per second",
                unlock_type=UnlockType.UPGRADE,
                requirement=Decimal("1000")
            ),
            Unlock(
                id="double_passive",
                name="Golden Touch",
                description="Double passive income rate",
                unlock_type=UnlockType.UPGRADE,
                requirement=Decimal("1500")
            ),
            Unlock(
                id="treasure_bonus",
                name="Treasure Hunter",
                description="Treasures give bonus gold",
                unlock_type=UnlockType.FEATURE,
                requirement=Decimal("3000")
            )
        ]
    
    def check_unlocks(self, gold: Decimal) -> List[Unlock]:
        """Check for new unlocks and return newly unlocked items."""
        newly_unlocked = []
        
        for unlock in self.unlocks:
            if unlock.check_unlock(gold):
                newly_unlocked.append(unlock)
                self.recent_unlocks.append(unlock)
        
        return newly_unlocked
    
    def get_unlock(self, unlock_id: str) -> Optional[Unlock]:
        """Get a specific unlock by ID."""
        for unlock in self.unlocks:
            if unlock.id == unlock_id:
                return unlock
        return None
    
    def is_unlocked(self, unlock_id: str) -> bool:
        """Check if a specific feature is unlocked."""
        unlock = self.get_unlock(unlock_id)
        return unlock.unlocked if unlock else False
```

### 8.2 Create Unlock Animation Effects
```python
# src/idle_game/engine/unlock_effects.py
from .animation import Animation, Sprite, Vector2
from .particles import ParticleEmitter, ParticleEffects
from typing import List
import math
import random

class UnlockAnimation(Animation):
    """Dramatic unlock animation."""
    
    def __init__(self, x: int, y: int, text: str):
        super().__init__(duration=3.0)
        self.x = x
        self.y = y
        self.text = text
        self.phase = 0
        self.particles = []
        
        # Create initial particle burst
        self.create_burst()
    
    def create_burst(self) -> None:
        """Create particle burst effect."""
        for i in range(20):
            angle = (2 * math.pi * i) / 20
            speed = random.uniform(15, 25)
            
            particle = {
                'x': float(self.x),
                'y': float(self.y),
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'lifetime': 0.0,
                'symbol': random.choice(['✦', '★', '✨', '◆'])
            }
            self.particles.append(particle)
    
    def update(self, dt: float) -> None:
        """Update unlock animation."""
        super().update(dt)
        
        # Update phase
        self.phase = self.elapsed / self.duration
        
        # Update particles
        for particle in self.particles:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['vx'] *= 0.95
            particle['vy'] *= 0.95
            particle['lifetime'] += dt
    
    def render(self) -> str:
        """Render current animation state."""
        if self.phase < 0.3:
            # Building up
            return "..."
        elif self.phase < 0.6:
            # Reveal
            return f"★ {self.text} ★"
        elif self.phase < 0.9:
            # Celebration
            return f"✨ {self.text.upper()} ✨"
        else:
            # Fade
            return self.text
    
    def get_particles(self) -> List[dict]:
        """Get particles for rendering."""
        return [p for p in self.particles if p['lifetime'] < 2.0]

class UnlockBanner:
    """Banner display for new unlocks."""
    
    def __init__(self, unlock_name: str, description: str):
        self.name = unlock_name
        self.description = description
        self.lifetime = 0.0
        self.duration = 4.0
        
        # Banner design
        self.width = 40
        self.height = 7
        
    def update(self, dt: float) -> None:
        """Update banner animation."""
        self.lifetime += dt
    
    def is_active(self) -> bool:
        """Check if banner should still display."""
        return self.lifetime < self.duration
    
    def render(self) -> List[str]:
        """Render banner to lines."""
        if not self.is_active():
            return []
        
        lines = []
        
        # Fade in/out
        if self.lifetime < 0.5:
            alpha = self.lifetime / 0.5
        elif self.lifetime > self.duration - 0.5:
            alpha = (self.duration - self.lifetime) / 0.5
        else:
            alpha = 1.0
        
        if alpha < 0.3:
            border = "·"
        elif alpha < 0.6:
            border = "─"
        else:
            border = "═"
        
        # Create banner
        lines.append("╔" + border * (self.width - 2) + "╗")
        lines.append("║" + " UNLOCKED! ".center(self.width - 2) + "║")
        lines.append("║" + f" {self.name} ".center(self.width - 2) + "║")
        lines.append("║" + " " * (self.width - 2) + "║")
        lines.append("║" + f" {self.description} ".center(self.width - 2) + "║")
        lines.append("║" + " " * (self.width - 2) + "║")
        lines.append("╚" + border * (self.width - 2) + "╝")
        
        return lines
```

### 8.3 Update Sidebar with Progressive Unlocks
```python
# Update src/idle_game/widgets/sidebar.py
from ..core.unlocks import UnlockManager
from ..engine.unlock_effects import UnlockBanner

class Sidebar(Static):
    """Sidebar with progressive unlocks."""
    
    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
        self.unlock_manager = UnlockManager()
        self.buttons = {}
        self.unlock_banners = []
        
    def compose(self) -> ComposeResult:
        """Create sidebar layout."""
        with Vertical():
            yield Label("⚡ Actions ⚡", id="actions-title")
            
            # Button container
            yield Container(id="button-container")
            
            # Stats panel
            yield StatsPanel(self.game_state)
            
            # Upgrades section (initially hidden)
            yield Container(id="upgrades-container")
    
    def on_mount(self) -> None:
        """Start checking for unlocks."""
        self.set_interval(0.5, self.check_unlocks)
        self.set_interval(1/60, self.update_banners)
        
        # Add initial button
        self.add_button("gold-button-10", "🖱️ Click for Gold", 10)
    
    def add_button(self, button_id: str, label: str, reward: int) -> None:
        """Add a button to the sidebar."""
        container = self.query_one("#button-container")
        
        button = AnimatedButton(label, reward=reward, id=button_id)
        self.buttons[button_id] = button
        container.mount(Center(button))
    
    def check_unlocks(self) -> None:
        """Check for and handle new unlocks."""
        newly_unlocked = self.unlock_manager.check_unlocks(self.game_state.gold)
        
        for unlock in newly_unlocked:
            # Create unlock banner
            banner = UnlockBanner(unlock.name, unlock.description)
            self.unlock_banners.append(banner)
            
            # Handle specific unlocks
            if unlock.id == "button_50":
                self.add_button("gold-button-50", "💎 MEGA Click!", 50)
                self.play_unlock_sound()  # Placeholder for sound
                
            elif unlock.id == "button_100":
                self.add_button("gold-button-100", "⚡ ULTRA Click!", 100)
                
            elif unlock.id == "double_passive":
                self.game_state.passive_rate *= Decimal("2")
                
            # Trigger canvas effects
            canvas = self.app.query_one(GameCanvas)
            canvas.trigger_unlock_effect(unlock)
    
    def update_banners(self) -> None:
        """Update and display unlock banners."""
        for banner in self.unlock_banners[:]:
            banner.update(1/60)
            if not banner.is_active():
                self.unlock_banners.remove(banner)
    
    def play_unlock_sound(self) -> None:
        """Play unlock sound effect (placeholder)."""
        # Could integrate with a sound library if desired
        pass
```

### 8.4 Update Game Canvas for Unlock Effects
```python
# Update src/idle_game/widgets/game_canvas.py
from ..engine.unlock_effects import UnlockAnimation

class GameCanvas(Static):
    """Game canvas with unlock effects."""
    
    def trigger_unlock_effect(self, unlock) -> None:
        """Trigger special effect for unlock."""
        # Create unlock animation in center
        anim = UnlockAnimation(30, 10, unlock.name)
        self.animation_manager.add_animation(anim)
        
        # Create particle fountain
        self.spawn_particle_effect("fountain", 30, 12)
        
        # Create surrounding sparkles
        for _ in range(5):
            x = 30 + random.randint(-10, 10)
            y = 10 + random.randint(-5, 5)
            self.spawn_particle_effect("sparkle", x, y)
        
        # Flash effect
        self.trigger_flash_effect()
    
    def trigger_flash_effect(self) -> None:
        """Create a screen flash effect."""
        self.add_class("flash")
        self.set_timer(0.2, lambda: self.remove_class("flash"))
```

## Tests to Write

### Test Unlock System
```python
# tests/test_unlocks.py
import pytest
from decimal import Decimal
from src.idle_game.core.unlocks import Unlock, UnlockManager, UnlockType

def test_unlock_creation():
    unlock = Unlock(
        id="test",
        name="Test Unlock",
        description="Test description",
        unlock_type=UnlockType.BUTTON,
        requirement=Decimal("100")
    )
    
    assert not unlock.unlocked
    assert unlock.requirement == Decimal("100")

def test_unlock_checking():
    unlock = Unlock(
        id="test",
        name="Test",
        description="Test",
        unlock_type=UnlockType.BUTTON,
        requirement=Decimal("100")
    )
    
    # Not enough gold
    assert not unlock.check_unlock(Decimal("99"))
    assert not unlock.unlocked
    
    # Enough gold
    assert unlock.check_unlock(Decimal("100"))
    assert unlock.unlocked
    
    # Already unlocked
    assert not unlock.check_unlock(Decimal("200"))

def test_unlock_manager():
    manager = UnlockManager()
    
    # Check initial state
    assert not manager.is_unlocked("button_50")
    
    # Check unlocks at different gold levels
    unlocked = manager.check_unlocks(Decimal("499"))
    assert len(unlocked) == 0
    
    unlocked = manager.check_unlocks(Decimal("500"))
    assert len(unlocked) == 1
    assert unlocked[0].id == "button_50"
    assert manager.is_unlocked("button_50")
    
    # Check multiple unlocks
    unlocked = manager.check_unlocks(Decimal("2000"))
    # Should unlock button_100, auto_clicker, double_passive
    assert len(unlocked) >= 1

def test_unlock_callback():
    called = False
    
    def callback():
        nonlocal called
        called = True
    
    unlock = Unlock(
        id="test",
        name="Test",
        description="Test",
        unlock_type=UnlockType.BUTTON,
        requirement=Decimal("10"),
        on_unlock=callback
    )
    
    unlock.check_unlock(Decimal("10"))
    assert called
```

## Success Criteria
- [ ] +50 button appears at 500 gold
- [ ] Dramatic unlock animation plays
- [ ] Unlock banner displays
- [ ] Particle effects on unlock
- [ ] Further unlocks at higher thresholds
- [ ] Upgrades apply correctly
- [ ] Save/load preserves unlocks

## Commands to Run
```bash
# Run the app
python -m src.idle_game.app

# Run tests
pytest tests/test_unlocks.py -v

# Test progression
python -c "
from src.idle_game.core.game_state import GameState
from src.idle_game.core.unlocks import UnlockManager

state = GameState()
manager = UnlockManager()

# Simulate progression
for gold in [100, 500, 1000, 1500, 2000, 3000]:
    state.gold = gold
    unlocked = manager.check_unlocks(state.gold)
    if unlocked:
        print(f'At {gold} gold, unlocked: {[u.name for u in unlocked]}')
"
```

## Next Phase
Once progressive features work, proceed to Phase 9: Testing & Polish.
