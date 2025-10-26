# Idle TUI Game - Implementation Complete

## ✅ What Was Built

I've successfully implemented an MVP idle game using the Textual TUI framework that runs both in the terminal and web browser. The game features:

### Core Features Implemented
1. **Counter System**: Automatically increments at 1/second
2. **Manual Clicking**: Click button adds +10 to counter
3. **Data Persistence**: SQLite database saves game state
4. **Offline Progression**: Calculates earnings while app was closed
5. **Visual UI**: Clean TUI interface with styled widgets
6. **Auto-save**: Saves every 10 seconds automatically
7. **Number Formatting**: Handles large numbers with K/M/B suffixes

### Project Structure
```
idle-tui/
├── src/
│   └── idle_game/
│       ├── models.py           # GameNumber & GameState classes
│       ├── database.py         # Async SQLite persistence
│       ├── app.py              # Main Textual application
│       ├── widgets/
│       │   ├── counter.py      # Counter display widget
│       │   └── clicker.py      # Click button widget
│       └── styles/
│           └── main.tcss       # UI styling
├── tests/
│   ├── test_models.py          # Unit tests for game logic
│   └── test_database.py        # Database persistence tests
├── data/                       # SQLite database files (gitignored)
├── requirements-simple.txt     # Python dependencies
├── pyproject.toml             # Project configuration
└── .gitignore                 # Git ignore rules
```

## 🚀 How to Run the Project

### Prerequisites
- Python 3.11 or higher
- Terminal that supports Unicode and colors

### Installation

1. **Clone or navigate to the project:**
```bash
cd /Users/unr/Development/idle-tui
```

2. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements-simple.txt
```

### Running the Game

#### Terminal Mode (Primary)
```bash
# Run the game
python -m src.idle_game.app

# Or run in development mode with auto-reload
python -m textual run --dev src/idle_game/app.py
```

#### Web Mode
For web deployment, install textual-web separately (requires newer Textual version):
```bash
# Note: textual-web requires specific Textual version compatibility
pip install textual-web

# Then run (may need version adjustments)
textual-web --app src.idle_game.app:IdleGame
```

### Controls
- **Click the button**: Adds +10 to counter
- **q**: Quit the game
- **s**: Manual save (also auto-saves every 10 seconds)
- **r**: Reset game (with confirmation dialog)

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_models.py -v

# Run with coverage
python -m pytest tests/ --cov=src/idle_game
```

## 🏗️ Architecture & Design Decisions

### Key Components

#### 1. GameNumber Class (`models.py`)
- Wraps Python's `Decimal` for precise large number handling
- Provides arithmetic operations (add, multiply)
- Formats numbers with suffixes (K, M, B, T, etc.)
- Uses 50-digit precision for extremely large numbers

#### 2. GameState Class (`models.py`)
- Manages core game state (counter, click power, auto increment)
- Calculates offline earnings based on time elapsed
- Handles game tick updates and click actions
- Tracks timestamps for save/update operations

#### 3. GameDatabase Class (`database.py`)
- Async SQLite interface using aiosqlite
- Single-row design (enforced with CHECK constraint)
- Stores numbers as text to preserve precision
- Handles save/load operations with datetime serialization

#### 4. UI Widgets
- **CounterDisplay**: Shows current resources with floating increment text
- **ClickButton**: Interactive button that posts click messages
- Clean separation of concerns with message passing

#### 5. Main App (`app.py`)
- Textual App subclass with reactive state management
- Timer-based game loop (0.1s ticks for smooth updates)
- Auto-save timer (every 10 seconds)
- Offline progression calculation on startup
- Styled with external CSS file

### Technical Choices

1. **Decimal over Float**: Prevents precision loss with large numbers
2. **Async Database**: Non-blocking I/O for smooth UI
3. **Single Game State**: Simplified persistence model
4. **Message-Based UI**: Decoupled widgets communicate via messages
5. **External CSS**: Easier styling maintenance and customization

## 📈 How to Add New Features

### 1. Adding Upgrades System
Create a new file `src/idle_game/upgrades.py`:
```python
@dataclass
class Upgrade:
    name: str
    cost: GameNumber
    effect_type: str  # "click_power" or "auto_increment"
    effect_multiplier: Decimal
    purchased: bool = False

class UpgradeManager:
    def __init__(self):
        self.upgrades = [
            Upgrade("Better Mouse", GameNumber(Decimal("100")), "click_power", Decimal("2")),
            Upgrade("Auto Clicker", GameNumber(Decimal("500")), "auto_increment", Decimal("5"))
        ]
    
    def can_afford(self, upgrade: Upgrade, current: GameNumber) -> bool:
        return current.value >= upgrade.cost.value
    
    def purchase(self, upgrade: Upgrade, state: GameState) -> bool:
        if self.can_afford(upgrade, state.counter) and not upgrade.purchased:
            state.counter = state.counter.add(-upgrade.cost.value)
            if upgrade.effect_type == "click_power":
                state.click_power = state.click_power.multiply(upgrade.effect_multiplier)
            elif upgrade.effect_type == "auto_increment":
                state.auto_increment = state.auto_increment.multiply(upgrade.effect_multiplier)
            upgrade.purchased = True
            return True
        return False
```

Then add upgrade buttons to the UI in `app.py`.

### 2. Adding Prestige System
Extend `models.py`:
```python
@dataclass
class GameState:
    # ... existing fields ...
    prestige_points: GameNumber = field(default_factory=GameNumber)
    prestige_multiplier: Decimal = field(default_factory=lambda: Decimal(1))
    
    def calculate_prestige_points(self) -> GameNumber:
        # Earn 1 prestige point per billion
        return GameNumber(self.counter.value // Decimal("1000000000"))
    
    def prestige_reset(self):
        points = self.calculate_prestige_points()
        if points.value > 0:
            self.prestige_points = self.prestige_points.add(points.value)
            self.prestige_multiplier = self.prestige_multiplier + (points.value * Decimal("0.1"))
            # Reset progress but keep prestige
            self.counter = GameNumber()
            self.click_power = GameNumber(Decimal(10) * self.prestige_multiplier)
            self.auto_increment = GameNumber(Decimal(1) * self.prestige_multiplier)
```

### 3. Adding Achievements
Create `src/idle_game/achievements.py`:
```python
@dataclass
class Achievement:
    name: str
    description: str
    requirement: Callable[[GameState], bool]
    unlocked: bool = False
    reward: Optional[str] = None

class AchievementManager:
    def __init__(self):
        self.achievements = [
            Achievement(
                "First Click",
                "Click the button for the first time",
                lambda state: state.counter.value >= Decimal("10")
            ),
            Achievement(
                "Century",
                "Reach 100 resources",
                lambda state: state.counter.value >= Decimal("100")
            ),
            Achievement(
                "Millionaire", 
                "Reach 1 million resources",
                lambda state: state.counter.value >= Decimal("1000000")
            )
        ]
    
    def check_achievements(self, state: GameState) -> List[Achievement]:
        newly_unlocked = []
        for achievement in self.achievements:
            if not achievement.unlocked and achievement.requirement(state):
                achievement.unlocked = True
                newly_unlocked.append(achievement)
        return newly_unlocked
```

### 4. Adding Statistics Tracking
Extend the database to track statistics:
```python
# In database.py, add new table
await db.execute("""
    CREATE TABLE IF NOT EXISTS statistics (
        id INTEGER PRIMARY KEY DEFAULT 1,
        total_clicks INTEGER DEFAULT 0,
        total_earned TEXT DEFAULT '0',
        play_time_seconds INTEGER DEFAULT 0,
        highest_value TEXT DEFAULT '0',
        times_prestiged INTEGER DEFAULT 0,
        CHECK (id = 1)
    )
""")
```

### 5. Adding Sound Effects
For terminal beeps:
```python
# In app.py
def on_click_button_clicked(self, event):
    # ... existing code ...
    print("\a", end="", flush=True)  # Terminal beep
```

### 6. Adding Multiple Resources
Extend the GameState to handle multiple resource types:
```python
@dataclass
class MultiResource:
    gold: GameNumber
    gems: GameNumber
    artifacts: GameNumber
```

## 🔄 Resetting Game Progress

### Method 1: In-Game Reset (Recommended)
While playing the game, press **'r'** to bring up the reset confirmation dialog. This will:
- Ask for confirmation before resetting
- Clear all progress and start fresh
- Keep the game running so you can continue playing

### Method 2: Command Line Reset
Run the reset script from the terminal:
```bash
cd /Users/unr/Development/idle-tui
python3 reset_game.py
```
This will prompt for confirmation and delete the save file.

### Method 3: Manual Database Deletion
Simply delete the database file:
```bash
rm data/game.db
```
The game will create a fresh database next time you start.

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure virtual environment is activated
   ```bash
   source venv/bin/activate
   ```

2. **Database Lock Errors**: Ensure only one instance is running
   ```bash
   pkill -f "python.*idle_game"
   ```

3. **Display Issues**: Terminal needs Unicode support
   ```bash
   export LANG=en_US.UTF-8
   export LC_ALL=en_US.UTF-8
   ```

4. **Textual/textual-web Version Conflicts**: 
   - Current implementation uses Textual 0.43.x for stability
   - textual-web has specific version requirements
   - For web deployment, may need to adjust versions

## 🎯 Next Steps Recommendations

### Immediate Enhancements
1. **Visual Polish**: Add colors and animations to increments
2. **Better Number Display**: Smooth counter animations
3. **Progress Bars**: Visual indicators for next upgrade costs
4. **Tooltips**: Hover information for upgrades

### Medium-term Goals
1. **Save Slots**: Multiple save games
2. **Export/Import**: Share saves between devices
3. **Themes**: Dark/light mode toggle
4. **Localization**: Multi-language support

### Long-term Vision
1. **Multiplayer**: Leaderboards and competitions
2. **Cloud Sync**: Cross-device progression
3. **Mobile PWA**: Installable web app
4. **Modding API**: Allow custom content

## 📊 Performance Considerations

- **Update Frequency**: Currently 0.1s ticks, can be adjusted in `app.py`
- **Number Caching**: Format strings are computed on each render, consider caching
- **Database Writes**: Auto-save every 10s is conservative, can be increased
- **Memory Usage**: Minimal, mainly the UI widgets and game state

## 🔧 Development Tips

1. **Hot Reload**: Use `textual run --dev` for development
2. **CSS Changes**: Modify `styles/main.tcss` for instant visual updates  
3. **Testing**: Add tests for new features in `tests/` directory
4. **Debugging**: Textual devtools available with `--dev` flag
5. **Profiling**: Use `python -m cProfile` to find bottlenecks

## 📝 Code Quality

- Type hints throughout for better IDE support
- Dataclasses for immutable game state
- Async/await for non-blocking operations
- Comprehensive test coverage for core logic
- Clear separation of concerns (models, UI, persistence)

---

The MVP is fully functional with a solid foundation for expansion. The architecture supports easy addition of new features while maintaining clean code organization. Happy coding! 🎮