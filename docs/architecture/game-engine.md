# Game Engine Architecture

## Current Implementation

The game engine is built on Textual framework for TUI rendering with async SQLite for persistence.

## Core Loop

```
User Input → Widget Event → State Update → Database Save → UI Render
     ↑                                                          ↓
     ←──────────────── Timer Events (100ms) ←──────────────────
```

### Update Cycle
- **Timer**: 100ms intervals (10 FPS)
- **Auto-save**: Every 10 seconds
- **Offline calculation**: On game load

## Component Overview

### App Layer (`app.py`)
```python
class IdleGameApp(App):
    - Manages application lifecycle
    - Coordinates widgets
    - Handles global keybindings
    - Manages save/load cycles
```

### State Management (`models.py`)
```python
class GameState:
    counter: GameNumber        # Current resources
    click_power: GameNumber    # Manual click value  
    auto_increment: GameNumber # Passive generation
    last_update: datetime      # For offline progress
    last_save: datetime        # Save tracking
```

### Widget System

**Base Widget Pattern**:
```python
class EmotionWidget(Static):
    value = reactive(0)  # Auto-updates UI
    
    def compose(self):
        # Build child widgets
        
    def watch_value(self):
        # Handle value changes
```

**Current Widgets**:
- `ClickerWidget`: Manual harvesting button
- `CounterWidget`: Resource display
- `ShopWidget`: (TODO) Customer interface
- `StorageWidget`: (TODO) Emotion inventory

### Database Layer (`database.py`)

**Schema**:
```sql
CREATE TABLE game_state (
    id INTEGER PRIMARY KEY,
    counter TEXT,           -- Decimal as string
    click_power TEXT,      
    auto_increment TEXT,
    last_update TIMESTAMP,
    last_save TIMESTAMP
)
```

**Operations**:
- Async SQLite via aiosqlite
- JSON serialization for complex types
- Single row state storage
- Automatic migration support

## Number System

### GameNumber Class
- Wraps Python Decimal (50 digit precision)
- Handles idle game scale (up to 10^308)
- Auto-formatting with suffixes

### Formatting Rules
```
< 1,000: Raw number (847)
< 1M: K suffix (8.47K)
< 1B: M suffix (8.47M)
...continues through Dc (Decillion)
> 1e33: Scientific notation
```

## Timing System

### Offline Progression
```python
def calculate_offline_earnings(seconds_offline):
    return auto_increment * seconds_offline
```

### Update Timing
- Game logic: 100ms (smooth feel)
- UI updates: On reactive change
- Database saves: 10 seconds
- Offline calc: On startup only

## Event Flow

### Click Event
1. User clicks button
2. ClickerWidget.on_button_pressed()
3. Updates GameState.counter
4. Triggers reactive update
5. CounterWidget refreshes display
6. Schedules next auto-save

### Timer Event  
1. App.action_tick() fires (100ms)
2. Calculates time delta
3. Updates state with auto_increment
4. Triggers reactive updates
5. All widgets refresh

## Planned Extensions

### Emotion System
```python
class EmotionResource:
    type: EmotionType
    amount: Decimal
    purity: float (0-1)
    storage_used: int
    storage_max: int
```

### Customer System
```python
class Customer:
    id: str
    name: str
    emotional_need: EmotionType
    satisfaction: float
    story_progress: int
```

### Recipe System
```python
class Recipe:
    inputs: List[EmotionAmount]
    output: EmotionType
    discovered: bool
    success_rate: float
```

## Performance Optimizations

### Current
- Cached number formatting
- Batched database writes
- Reactive updates (no polling)

### Planned
- Resource pooling for widgets
- Lazy loading for hidden tabs
- Delta compression for saves
- Background worker for calculations

## File Structure
```
src/idle_game/
├── app.py              # Main application
├── models.py           # Data models
├── database.py         # Persistence
├── widgets/
│   ├── __init__.py
│   ├── clicker.py     # Click button
│   ├── counter.py     # Display
│   ├── shop.py        # TODO
│   └── storage.py     # TODO
└── styles/
    └── main.tcss      # Styling
```

## CSS Styling

Uses Textual CSS (TCSS) for theming:
```css
Screen {
    background: $surface;
}

Button {
    width: 100%;
    height: 3;
}

.counter-display {
    text-align: center;
    text-style: bold;
}
```

## Debug Features

### Dev Mode (`--dev`)
- Live CSS reload
- Console output
- Performance metrics
- Widget inspector

### Debug Commands
```python
# In app.py
self.log.debug(f"State: {self.state}")
self.bell()  # Audio feedback
self.notify("Debug message")  # Toast
```
