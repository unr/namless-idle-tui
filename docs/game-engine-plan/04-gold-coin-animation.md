# Phase 4: Gold Coin Animation

## Objective
Create visually appealing gold coin animations that appear when gold is earned, with different styles for passive income and manual clicks.

## Prerequisites
- Phase 3 complete with working animation engine

## Tasks

### 4.1 Create Detailed Coin Animations
```python
# src/idle_game/engine/coin_effects.py
from .animation import Sprite, Vector2
from .effects import FloatingText
import random
import math

class GoldCoin(Sprite):
    """Animated gold coin with multiple display modes."""
    
    # ASCII art representations of coin at different angles
    COIN_FRAMES = [
        "◉",   # Front view
        "◎",   # Slightly turned
        "○",   # Side view
        "◌",   # Other side
        "◎",   # Turning back
    ]
    
    FANCY_COIN = "💰"
    SIMPLE_COIN = "¢"
    
    def __init__(self, x: int, y: int, style: str = "simple"):
        # Choose display style
        if style == "fancy":
            frames = [self.FANCY_COIN]
        elif style == "spinning":
            frames = self.COIN_FRAMES
        else:
            frames = [self.SIMPLE_COIN]
        
        super().__init__(
            position=Vector2(x, y),
            velocity=Vector2(0, -5),  # Float upward
            symbol=frames[0],
            duration=2.0,
            gravity=2
        )
        
        self.frames = frames
        self.current_frame = 0
        self.frame_time = 0
        self.frame_duration = 0.1 if len(frames) > 1 else 1.0
        self.style = style
        
        # Add subtle horizontal wobble
        self.wobble_amplitude = 2
        self.wobble_frequency = 3
        self.initial_x = x
        
    def update(self, dt: float) -> None:
        """Update coin animation."""
        super().update(dt)
        
        if not self.active:
            return
        
        # Update frame for spinning coins
        if len(self.frames) > 1:
            self.frame_time += dt
            if self.frame_time >= self.frame_duration:
                self.frame_time = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.symbol = self.frames[self.current_frame]
        
        # Add horizontal wobble
        wobble = math.sin(self.elapsed * self.wobble_frequency * 2 * math.pi) * self.wobble_amplitude
        self.position.x = self.initial_x + wobble
        
        # Fade out near end
        if self.elapsed > self.duration * 0.7:
            fade_progress = (self.elapsed - self.duration * 0.7) / (self.duration * 0.3)
            if fade_progress > 0.5:
                self.symbol = "·"

class CoinShower:
    """Multiple coins falling in a shower effect."""
    
    def __init__(self, x: int, y: int, count: int = 5):
        self.coins = []
        
        for i in range(count):
            # Spread coins horizontally
            coin_x = x + random.randint(-10, 10)
            coin_y = y + random.randint(-2, 2)
            
            coin = GoldCoin(coin_x, coin_y, style="simple")
            # Vary the physics for each coin
            coin.velocity = Vector2(
                random.uniform(-3, 3),
                random.uniform(-8, -12)
            )
            coin.gravity = random.uniform(15, 25)
            
            # Stagger the start times
            coin.elapsed = -i * 0.05
            
            self.coins.append(coin)
    
    def get_animations(self):
        """Get all coin animations."""
        return self.coins

class CoinFountain(Sprite):
    """Fountain effect of coins."""
    
    def __init__(self, x: int, y: int):
        super().__init__(
            position=Vector2(x, y),
            velocity=Vector2(0, 0),
            symbol="",
            duration=2.0
        )
        
        self.particles = []
        self.spawn_rate = 0.1  # Spawn every 0.1 seconds
        self.last_spawn = 0
        
    def update(self, dt: float) -> None:
        """Update fountain and spawn new coins."""
        super().update(dt)
        
        if not self.active:
            return
        
        self.last_spawn += dt
        
        if self.last_spawn >= self.spawn_rate and len(self.particles) < 10:
            self.last_spawn = 0
            
            # Spawn a new coin particle
            angle = random.uniform(-math.pi/3, math.pi/3)  # Cone shape
            speed = random.uniform(10, 15)
            
            particle = GoldCoin(int(self.position.x), int(self.position.y), "simple")
            particle.velocity = Vector2(
                math.sin(angle) * speed,
                -math.cos(angle) * speed
            )
            particle.gravity = 20
            particle.duration = 1.0
            
            self.particles.append(particle)
        
        # Update all particles
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.active:
                self.particles.remove(particle)
    
    def get_all_sprites(self):
        """Get all sprites for rendering."""
        return [self] + self.particles
```

### 4.2 Create Combined Coin and Text Effect
```python
# src/idle_game/engine/combo_effects.py
from .coin_effects import GoldCoin, CoinShower
from .effects import FloatingText
from typing import List
from .animation import Animation

class CoinWithValue:
    """Combined coin and value text animation."""
    
    def __init__(self, value: int, x: int, y: int, source: str = "passive"):
        self.animations = []
        
        if source == "passive":
            # Single floating coin with value
            coin = GoldCoin(x, y, style="spinning")
            text = FloatingText(f"+{value}", x + 2, y)
            self.animations = [coin, text]
            
        elif source == "click":
            # More dramatic effect for clicks
            # Multiple coins
            shower = CoinShower(x, y, count=3)
            self.animations.extend(shower.get_animations())
            
            # Larger text
            text = FloatingText(f"+{value}!", x, y - 2)
            self.animations.append(text)
            
        elif source == "bonus":
            # Special effect for bonus
            coin = GoldCoin(x, y, style="fancy")
            coin.duration = 3.0
            coin.wobble_amplitude = 4
            
            text = FloatingText(f"★+{value}★", x, y - 1)
            text.duration = 3.0
            
            self.animations = [coin, text]
    
    def get_animations(self) -> List[Animation]:
        """Get all animations in this effect."""
        return self.animations
```

### 4.3 Update Game Canvas with Coin Animations
```python
# Update src/idle_game/widgets/game_canvas.py
from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align
from decimal import Decimal
import time
import random
from ..engine.animation_manager import AnimationManager
from ..engine.combo_effects import CoinWithValue

class GameCanvas(Static):
    """Main game display area with coin animations."""
    
    gold = reactive(Decimal("0"))
    
    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
        self.animation_manager = AnimationManager(60, 20)
        
        # Track animation spawning
        self.last_passive_animation = 0
        self.passive_animation_cooldown = 1.0  # Match passive rate
        
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
        """Handle gold earned event with coin animation."""
        current_time = time.perf_counter()
        
        # Limit passive animations to prevent spam
        if source == "passive":
            if current_time - self.last_passive_animation < self.passive_animation_cooldown:
                return
            self.last_passive_animation = current_time
        
        # Spawn coin animation at random position in upper area
        x = random.randint(20, 40)
        y = random.randint(3, 8)
        
        # Create combined effect
        effect = CoinWithValue(int(amount), x, y, source)
        
        # Add all animations
        for anim in effect.get_animations():
            self.animation_manager.add_animation(anim)
    
    def update_display(self) -> None:
        """Update the canvas display with animations."""
        # Create layered display
        lines = []
        
        # Get animation grid
        anim_grid = self.animation_manager.render_to_grid()
        
        # Top section - animations
        for y in range(10):
            if y < len(anim_grid):
                line = "".join(anim_grid[y][:60])  # Limit width
                lines.append(line)
            else:
                lines.append(" " * 60)
        
        # Middle section - gold counter
        lines.append("─" * 60)
        lines.append(f"💰 Gold: {int(self.gold)}".center(60))
        lines.append(f"📈 Rate: {self.game_state.passive_rate}/sec".center(60))
        lines.append("─" * 60)
        
        # Bottom section - more animations
        for y in range(14, 20):
            if y < len(anim_grid):
                line = "".join(anim_grid[y][:60])
                lines.append(line)
            else:
                lines.append(" " * 60)
        
        # Create rich text with styling
        display = Text("\n".join(lines))
        
        # Wrap in panel
        panel = Panel(
            display,
            title="💎 Gold Mine 💎",
            border_style="yellow"
        )
        
        self.update(panel)
    
    def add_gold(self, amount: Decimal) -> None:
        """Add gold with visual feedback."""
        self.gold = self.game_state.add_gold(amount)
        # Trigger animation through event
        for callback in self.game_state.on_gold_earned:
            callback(amount, "click")
```

## Tests to Write

### Test Coin Animations
```python
# tests/test_coin_animation.py
import pytest
from src.idle_game.engine.coin_effects import GoldCoin, CoinShower, CoinFountain
from src.idle_game.engine.combo_effects import CoinWithValue

def test_gold_coin_creation():
    coin = GoldCoin(10, 10, style="simple")
    assert coin.symbol == "¢"
    assert coin.position.x == 10
    assert coin.position.y == 10

def test_spinning_coin():
    coin = GoldCoin(0, 0, style="spinning")
    assert len(coin.frames) > 1
    
    # Update to trigger frame change
    for _ in range(3):
        coin.update(0.15)
    
    # Should have changed frame
    assert coin.current_frame > 0

def test_coin_wobble():
    coin = GoldCoin(10, 10)
    initial_x = coin.position.x
    
    # Update for a bit
    coin.update(0.5)
    
    # X position should have changed due to wobble
    assert coin.position.x != initial_x

def test_coin_shower():
    shower = CoinShower(20, 20, count=5)
    coins = shower.get_animations()
    
    assert len(coins) == 5
    
    # Each coin should have different velocity
    velocities = [coin.velocity.x for coin in coins]
    assert len(set(velocities)) > 1  # Not all the same

def test_combo_effect():
    # Test passive effect
    effect = CoinWithValue(1, 10, 10, "passive")
    anims = effect.get_animations()
    assert len(anims) == 2  # Coin and text
    
    # Test click effect
    effect = CoinWithValue(10, 10, 10, "click")
    anims = effect.get_animations()
    assert len(anims) > 2  # Multiple coins and text
    
    # Test bonus effect
    effect = CoinWithValue(50, 10, 10, "bonus")
    anims = effect.get_animations()
    assert len(anims) == 2
    assert anims[0].duration == 3.0  # Longer duration for bonus
```

## Success Criteria
- [ ] Gold coins appear when earning passive income
- [ ] Different animation for manual clicks
- [ ] Coins spin/rotate during animation
- [ ] Smooth 60fps animation
- [ ] No visual glitches or overlaps
- [ ] Memory efficient (old animations cleaned up)

## Commands to Run
```bash
# Run the app
python -m src.idle_game.app

# Run tests  
pytest tests/test_coin_animation.py -v

# Profile performance
python -m cProfile -s cumulative src/idle_game/app.py
```

## Next Phase
Once coin animations are polished, proceed to Phase 5: Manual Click System.
