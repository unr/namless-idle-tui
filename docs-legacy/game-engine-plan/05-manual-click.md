# Phase 5: Manual Click System

## Objective
Implement the manual click button that gives +10 gold with enhanced visual feedback and button animations.

## Prerequisites
- Phase 4 complete with working coin animations

## Tasks

### 5.1 Enhanced Button Widget
```python
# src/idle_game/widgets/animated_button.py
from textual.widgets import Button
from textual.reactive import reactive
from rich.text import Text
import asyncio

class AnimatedButton(Button):
    """Button with click animations and effects."""
    
    pressed = reactive(False)
    cooldown = reactive(False)
    
    def __init__(self, label: str, reward: int = 10, **kwargs):
        super().__init__(label, **kwargs)
        self.reward = reward
        self.original_label = label
        self.click_count = 0
        self.cooldown_duration = 0.1  # Prevent spam clicking
        
    async def on_click(self) -> None:
        """Handle button click with animation."""
        if self.cooldown:
            return
            
        self.pressed = True
        self.cooldown = True
        self.click_count += 1
        
        # Animate button press
        await self.animate_press()
        
        # Reset after cooldown
        await asyncio.sleep(self.cooldown_duration)
        self.cooldown = False
    
    async def animate_press(self) -> None:
        """Animate the button press."""
        # Change label temporarily
        self.label = f"💥 +{self.reward}! 💥"
        
        # Visual feedback
        self.add_class("button-pressed")
        
        # Hold animation
        await asyncio.sleep(0.2)
        
        # Reset
        self.label = self.original_label
        self.remove_class("button-pressed")
        self.pressed = False
    
    def watch_pressed(self, pressed: bool) -> None:
        """React to pressed state changes."""
        if pressed:
            self.styles.background = "green"
            self.styles.color = "white"
        else:
            self.styles.background = "blue"
            self.styles.color = "white"
```

### 5.2 Update Sidebar with Enhanced Buttons
```python
# Update src/idle_game/widgets/sidebar.py
from textual.widgets import Static
from textual.containers import Vertical, Center
from textual.widgets import Label
from textual.app import ComposeResult
from rich.panel import Panel
from rich.text import Text
from .animated_button import AnimatedButton

class Sidebar(Static):
    """Sidebar with action buttons and stats."""
    
    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
        self.button_10 = None
        self.button_50 = None
        
    def compose(self) -> ComposeResult:
        """Create sidebar layout."""
        with Vertical():
            # Title
            yield Label("⚡ Actions ⚡", id="actions-title")
            
            # Main click button (always visible)
            self.button_10 = AnimatedButton(
                "🖱️ Click for Gold",
                reward=10,
                id="gold-button-10"
            )
            yield Center(self.button_10)
            
            # Stats panel
            yield StatsPanel(self.game_state)
            
            # Placeholder for second button
            yield Center(Static("", id="button-50-container"))
    
    def on_mount(self) -> None:
        """Start checking for unlocks."""
        self.set_interval(0.5, self.check_unlocks)
    
    def check_unlocks(self) -> None:
        """Check if new buttons should be unlocked."""
        container = self.query_one("#button-50-container")
        
        # Check for 500 gold unlock
        if self.game_state.is_button2_unlocked() and self.button_50 is None:
            self.button_50 = AnimatedButton(
                "💎 MEGA Click!",
                reward=50,
                id="gold-button-50"
            )
            container.update(self.button_50)
            
            # Play unlock animation
            self.animate_unlock()
    
    def animate_unlock(self) -> None:
        """Animate the unlock of new button."""
        if self.button_50:
            self.button_50.add_class("button-unlocked")
            self.set_timer(0.5, lambda: self.button_50.remove_class("button-unlocked"))

class StatsPanel(Static):
    """Display game statistics."""
    
    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state
        
    def on_mount(self) -> None:
        """Start updating stats."""
        self.set_interval(0.1, self.update_stats)
    
    def update_stats(self) -> None:
        """Update statistics display."""
        stats = [
            f"💰 Total Earned: {int(self.game_state.total_earned)}",
            f"📦 Treasure Chests: {self.game_state.get_chest_count()}",
            f"⚡ Click Power: 10",
        ]
        
        if self.game_state.is_button2_unlocked():
            stats.append(f"💎 Mega Power: 50")
        
        # Create formatted text
        text = Text("\n".join(stats), style="cyan")
        
        # Wrap in panel
        panel = Panel(
            text,
            title="📊 Stats",
            border_style="cyan"
        )
        
        self.update(panel)
```

### 5.3 Add Click Feedback System
```python
# src/idle_game/engine/click_effects.py
from .animation import Sprite, Vector2
from .coin_effects import CoinShower
from .effects import FloatingText
import random
import math

class ClickBurst:
    """Burst effect at click location."""
    
    def __init__(self, x: int, y: int, power: int = 10):
        self.animations = []
        
        # Create burst of particles
        particle_count = min(power // 5, 10)
        
        for i in range(particle_count):
            angle = (2 * math.pi * i) / particle_count
            speed = random.uniform(8, 12)
            
            particle = Sprite(
                position=Vector2(x, y),
                velocity=Vector2(
                    math.cos(angle) * speed,
                    math.sin(angle) * speed
                ),
                symbol="✦",
                duration=0.5
            )
            
            self.animations.append(particle)
        
        # Add central flash
        flash = Sprite(
            position=Vector2(x, y),
            velocity=Vector2(0, 0),
            symbol="💫",
            duration=0.3
        )
        self.animations.append(flash)
    
    def get_animations(self):
        return self.animations

class PowerClick:
    """Enhanced click effect for larger rewards."""
    
    def __init__(self, x: int, y: int, reward: int):
        self.animations = []
        
        # Coin shower
        shower = CoinShower(x, y, count=reward // 10)
        self.animations.extend(shower.get_animations())
        
        # Big text
        text = FloatingText(f"💰+{reward}💰", x, y - 2)
        text.duration = 2.0
        text.velocity.y = -8
        self.animations.append(text)
        
        # Burst effect
        burst = ClickBurst(x, y, reward)
        self.animations.extend(burst.get_animations())
        
        # Add sparkles around
        for _ in range(5):
            sparkle = Sprite(
                position=Vector2(
                    x + random.randint(-5, 5),
                    y + random.randint(-5, 5)
                ),
                velocity=Vector2(
                    random.uniform(-2, 2),
                    random.uniform(-2, 2)
                ),
                symbol="✨",
                duration=1.0
            )
            self.animations.append(sparkle)
    
    def get_animations(self):
        return self.animations
```

### 5.4 Update Main App with Click Handling
```python
# Update src/idle_game/app.py
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Header, Footer
from textual.message import Message
from .core.game_state import GameState
from .widgets.game_canvas import GameCanvas
from .widgets.sidebar import Sidebar
from .engine.click_effects import PowerClick
import random

class IdleGameApp(App):
    """Main application class for the idle game."""
    
    CSS = """
    GameCanvas {
        width: 70%;
        height: 100%;
    }
    
    Sidebar {
        width: 30%;
        height: 100%;
    }
    
    AnimatedButton {
        margin: 1;
        width: 90%;
        height: 3;
        background: blue;
        color: white;
        text-align: center;
    }
    
    .button-pressed {
        background: green !important;
    }
    
    .button-unlocked {
        background: gold !important;
        color: black !important;
    }
    
    #actions-title {
        text-align: center;
        text-style: bold;
        background: $primary;
        padding: 1;
    }
    
    StatsPanel {
        margin: 1;
        height: auto;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.game_state = GameState()
        
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            yield GameCanvas(self.game_state)
            yield Sidebar(self.game_state)
        yield Footer()
    
    def on_mount(self) -> None:
        """Start game systems when app mounts."""
        self.title = "Idle Gold Mine"
        self.sub_title = "Click or wait to earn gold!"
    
    def on_button_pressed(self, event) -> None:
        """Handle button clicks with effects."""
        canvas = self.query_one(GameCanvas)
        
        if event.button.id == "gold-button-10":
            # Add gold
            canvas.add_gold(10)
            
            # Spawn click effect
            x = random.randint(20, 40)
            y = random.randint(5, 15)
            effect = PowerClick(x, y, 10)
            
            for anim in effect.get_animations():
                canvas.animation_manager.add_animation(anim)
                
        elif event.button.id == "gold-button-50":
            # Add gold
            canvas.add_gold(50)
            
            # Spawn bigger effect
            x = random.randint(20, 40)
            y = random.randint(5, 15)
            effect = PowerClick(x, y, 50)
            
            for anim in effect.get_animations():
                canvas.animation_manager.add_animation(anim)
```

## Tests to Write

### Test Button Functionality
```python
# tests/test_click_system.py
import pytest
from decimal import Decimal
from src.idle_game.widgets.animated_button import AnimatedButton
from src.idle_game.engine.click_effects import ClickBurst, PowerClick

@pytest.mark.asyncio
async def test_animated_button():
    button = AnimatedButton("Test", reward=10)
    
    assert button.reward == 10
    assert not button.pressed
    assert not button.cooldown
    
    # Simulate click
    await button.on_click()
    
    # Should be in cooldown
    assert button.cooldown

def test_click_burst():
    burst = ClickBurst(10, 10, power=20)
    anims = burst.get_animations()
    
    # Should create particles based on power
    assert len(anims) > 4  # At least 4 particles plus flash

def test_power_click():
    effect = PowerClick(10, 10, 50)
    anims = effect.get_animations()
    
    # Should create multiple effect types
    assert len(anims) > 10  # Coins, burst, sparkles, text

def test_button_unlock_threshold():
    from src.idle_game.core.game_state import GameState
    
    state = GameState()
    assert not state.is_button2_unlocked()
    
    state.gold = Decimal("499")
    assert not state.is_button2_unlocked()
    
    state.gold = Decimal("500")
    assert state.is_button2_unlocked()
```

## Success Criteria
- [ ] +10 gold button always visible and working
- [ ] Button shows click animation
- [ ] Click creates burst effect in game area
- [ ] +50 gold button appears at 500 gold
- [ ] Unlock animation plays for new button
- [ ] Stats panel updates in real-time
- [ ] No spam clicking (cooldown works)

## Commands to Run
```bash
# Run the app
python -m src.idle_game.app

# Run tests
pytest tests/test_click_system.py -v

# Test button responsiveness
python -m pytest tests/test_click_system.py -v --durations=10
```

## Next Phase
Once manual clicking is polished, proceed to Phase 6: Particle Effects.
