# MVP Implementation Plan - Idle TUI Game

## Overview
Build a minimal viable idle game with Textual that runs in terminal and web browser, featuring automatic increments, manual clicking, persistent state, and offline progression calculation.

## MVP Core Features
1. **Counter System**: Value that auto-increments at 1/second
2. **Manual Interaction**: Click button to add +10 to counter
3. **Persistence**: Save state to local SQLite database
4. **Offline Progression**: Calculate earnings while app was closed
5. **Visual Feedback**: Show increment amounts as floating text
6. **Cross-Platform**: Run as TUI or web app from same codebase

## Project Structure
```
idle-tui/
├── src/
│   └── idle_game/
│       ├── __init__.py
│       ├── app.py              # Main Textual app
│       ├── models.py           # Game state & number handling
│       ├── database.py         # SQLite persistence layer
│       ├── widgets/
│       │   ├── __init__.py
│       │   ├── counter.py      # Main counter display
│       │   └── clicker.py      # Click button widget
│       └── styles/
│           └── main.tcss       # UI styling
├── tests/
│   ├── test_models.py
│   ├── test_database.py
│   └── test_offline_calc.py
├── data/                       # SQLite files (gitignored)
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Phase 1: Core Models & Number System (Day 1)

### 1.1 Game Number Implementation
```python
# src/idle_game/models.py
from decimal import Decimal, getcontext
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

getcontext().prec = 50  # Precision for large numbers

@dataclass
class GameNumber:
    """Wrapper for Decimal to handle idle game numbers"""
    value: Decimal = field(default_factory=lambda: Decimal(0))
    
    def add(self, amount: Decimal) -> 'GameNumber':
        return GameNumber(self.value + amount)
    
    def multiply(self, factor: Decimal) -> 'GameNumber':
        return GameNumber(self.value * factor)
    
    def format(self) -> str:
        """Format for display with suffixes"""
        if self.value < 1000:
            return f"{self.value:.0f}"
        
        suffixes = ['', 'K', 'M', 'B', 'T', 'Qa', 'Qi', 'Sx', 'Sp', 'Oc', 'No', 'Dc']
        magnitude = 0
        num = float(self.value)
        
        while abs(num) >= 1000 and magnitude < len(suffixes) - 1:
            magnitude += 1
            num /= 1000.0
        
        return f"{num:.2f}{suffixes[magnitude]}"

@dataclass
class GameState:
    """Core game state"""
    counter: GameNumber = field(default_factory=GameNumber)
    click_power: GameNumber = field(default_factory=lambda: GameNumber(Decimal(10)))
    auto_increment: GameNumber = field(default_factory=lambda: GameNumber(Decimal(1)))
    last_update: datetime = field(default_factory=datetime.now)
    last_save: datetime = field(default_factory=datetime.now)
    
    def calculate_offline_earnings(self, seconds_offline: float) -> GameNumber:
        """Calculate earnings while game was closed"""
        return self.auto_increment.multiply(Decimal(str(seconds_offline)))
    
    def update(self, current_time: datetime) -> GameNumber:
        """Update state and return increment amount"""
        time_delta = (current_time - self.last_update).total_seconds()
        increment = self.auto_increment.multiply(Decimal(str(time_delta)))
        self.counter = self.counter.add(increment.value)
        self.last_update = current_time
        return increment
    
    def click(self) -> GameNumber:
        """Handle manual click"""
        self.counter = self.counter.add(self.click_power.value)
        return self.click_power
```

### 1.2 Unit Tests for Models
```python
# tests/test_models.py
import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from src.idle_game.models import GameNumber, GameState

def test_game_number_formatting():
    assert GameNumber(Decimal("0")).format() == "0"
    assert GameNumber(Decimal("999")).format() == "999"
    assert GameNumber(Decimal("1000")).format() == "1.00K"
    assert GameNumber(Decimal("1500000")).format() == "1.50M"
    assert GameNumber(Decimal("1234567890")).format() == "1.23B"

def test_game_number_operations():
    num1 = GameNumber(Decimal("100"))
    num2 = num1.add(Decimal("50"))
    assert num2.value == Decimal("150")
    
    num3 = num1.multiply(Decimal("2.5"))
    assert num3.value == Decimal("250")

def test_offline_calculation():
    state = GameState(
        counter=GameNumber(Decimal("1000")),
        auto_increment=GameNumber(Decimal("5"))
    )
    
    # Simulate 60 seconds offline
    earnings = state.calculate_offline_earnings(60)
    assert earnings.value == Decimal("300")  # 5 * 60

def test_click_mechanics():
    state = GameState(
        counter=GameNumber(Decimal("100")),
        click_power=GameNumber(Decimal("10"))
    )
    
    increment = state.click()
    assert increment.value == Decimal("10")
    assert state.counter.value == Decimal("110")

def test_auto_update():
    state = GameState(
        counter=GameNumber(Decimal("100")),
        auto_increment=GameNumber(Decimal("2"))
    )
    
    # Simulate 5 seconds passing
    future_time = state.last_update + timedelta(seconds=5)
    increment = state.update(future_time)
    
    assert increment.value == Decimal("10")  # 2 * 5
    assert state.counter.value == Decimal("110")
```

## Phase 2: Database & Persistence (Day 1-2)

### 2.1 SQLite Database Layer
```python
# src/idle_game/database.py
import aiosqlite
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from .models import GameState, GameNumber
from decimal import Decimal

class GameDatabase:
    def __init__(self, db_path: str = "data/game.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(exist_ok=True)
    
    async def initialize(self):
        """Create tables if they don't exist"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS game_state (
                    id INTEGER PRIMARY KEY DEFAULT 1,
                    counter TEXT NOT NULL,
                    click_power TEXT NOT NULL,
                    auto_increment TEXT NOT NULL,
                    last_update TEXT NOT NULL,
                    last_save TEXT NOT NULL,
                    CHECK (id = 1)
                )
            """)
            await db.commit()
    
    async def save_state(self, state: GameState):
        """Save current game state"""
        async with aiosqlite.connect(self.db_path) as db:
            state.last_save = datetime.now()
            await db.execute("""
                INSERT OR REPLACE INTO game_state 
                (id, counter, click_power, auto_increment, last_update, last_save)
                VALUES (1, ?, ?, ?, ?, ?)
            """, (
                str(state.counter.value),
                str(state.click_power.value),
                str(state.auto_increment.value),
                state.last_update.isoformat(),
                state.last_save.isoformat()
            ))
            await db.commit()
    
    async def load_state(self) -> Optional[GameState]:
        """Load saved game state"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT counter, click_power, auto_increment, last_update, last_save "
                "FROM game_state WHERE id = 1"
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return GameState(
                        counter=GameNumber(Decimal(row[0])),
                        click_power=GameNumber(Decimal(row[1])),
                        auto_increment=GameNumber(Decimal(row[2])),
                        last_update=datetime.fromisoformat(row[3]),
                        last_save=datetime.fromisoformat(row[4])
                    )
        return None
```

### 2.2 Database Tests
```python
# tests/test_database.py
import pytest
import asyncio
from pathlib import Path
from decimal import Decimal
from src.idle_game.database import GameDatabase
from src.idle_game.models import GameState, GameNumber

@pytest.fixture
async def test_db():
    """Create test database"""
    db_path = "data/test_game.db"
    db = GameDatabase(db_path)
    await db.initialize()
    yield db
    # Cleanup
    Path(db_path).unlink(missing_ok=True)

@pytest.mark.asyncio
async def test_save_and_load(test_db):
    # Create and save state
    state = GameState(
        counter=GameNumber(Decimal("12345")),
        click_power=GameNumber(Decimal("50")),
        auto_increment=GameNumber(Decimal("10"))
    )
    await test_db.save_state(state)
    
    # Load state
    loaded = await test_db.load_state()
    assert loaded is not None
    assert loaded.counter.value == Decimal("12345")
    assert loaded.click_power.value == Decimal("50")
    assert loaded.auto_increment.value == Decimal("10")

@pytest.mark.asyncio
async def test_empty_database(test_db):
    loaded = await test_db.load_state()
    assert loaded is None
```

## Phase 3: UI Implementation (Day 2-3)

### 3.1 Counter Widget
```python
# src/idle_game/widgets/counter.py
from textual.widgets import Static
from textual.reactive import reactive
from ..models import GameNumber

class CounterDisplay(Static):
    """Display current counter value with animations"""
    
    value: reactive[GameNumber] = reactive(GameNumber())
    increment_text: reactive[str] = reactive("")
    
    def render(self) -> str:
        lines = [
            f"[bold cyan]Resources:[/bold cyan]",
            f"[bold yellow]{self.value.format()}[/bold yellow]",
        ]
        if self.increment_text:
            lines.append(f"[green]{self.increment_text}[/green]")
        return "\n".join(lines)
    
    def show_increment(self, amount: GameNumber):
        """Show floating increment text"""
        self.increment_text = f"+{amount.format()}"
        self.set_timer(1.0, self.clear_increment)
    
    def clear_increment(self):
        self.increment_text = ""
```

### 3.2 Clicker Button Widget
```python
# src/idle_game/widgets/clicker.py
from textual.widgets import Button
from textual.message import Message

class ClickButton(Button):
    """Button for manual clicking"""
    
    class Clicked(Message):
        """Message sent when button is clicked"""
        pass
    
    def __init__(self):
        super().__init__("🖱️ CLICK FOR +10", id="click-button")
    
    def on_button_pressed(self):
        self.post_message(self.Clicked())
```

### 3.3 Main Application
```python
# src/idle_game/app.py
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, Label
from textual.reactive import reactive
from textual.timer import Timer
import asyncio
from datetime import datetime
from decimal import Decimal

from .models import GameState, GameNumber
from .database import GameDatabase
from .widgets.counter import CounterDisplay
from .widgets.clicker import ClickButton

class IdleGame(App):
    """Main idle game application"""
    
    CSS_PATH = "styles/main.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "save", "Save Game"),
    ]
    
    game_state: reactive[GameState] = reactive(GameState())
    
    def __init__(self):
        super().__init__()
        self.db = GameDatabase()
        self.update_timer: Optional[Timer] = None
        self.save_timer: Optional[Timer] = None
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main-container"):
            with Vertical(id="game-area"):
                yield CounterDisplay(id="counter")
                yield ClickButton()
                yield Label("[dim]Auto: +1/sec[/dim]", id="rate-display")
        yield Footer()
    
    async def on_mount(self):
        """Initialize game on mount"""
        await self.db.initialize()
        
        # Load saved state
        saved_state = await self.db.load_state()
        if saved_state:
            # Calculate offline earnings
            now = datetime.now()
            seconds_offline = (now - saved_state.last_save).total_seconds()
            if seconds_offline > 0:
                offline_earnings = saved_state.calculate_offline_earnings(seconds_offline)
                saved_state.counter = saved_state.counter.add(offline_earnings.value)
                self.notify(
                    f"Welcome back! You earned {offline_earnings.format()} while away!",
                    severity="information"
                )
            saved_state.last_update = now
            self.game_state = saved_state
        
        # Start timers
        self.update_timer = self.set_interval(0.1, self.game_tick)
        self.save_timer = self.set_interval(10.0, self.auto_save)
    
    def game_tick(self):
        """Main game loop tick"""
        now = datetime.now()
        increment = self.game_state.update(now)
        
        # Update display
        counter_widget = self.query_one("#counter", CounterDisplay)
        counter_widget.value = self.game_state.counter
        
        # Show increment if significant
        if increment.value >= Decimal("0.1"):
            counter_widget.show_increment(increment)
    
    async def auto_save(self):
        """Auto-save every 10 seconds"""
        await self.db.save_state(self.game_state)
    
    async def on_click_button_clicked(self, event: ClickButton.Clicked):
        """Handle manual clicks"""
        increment = self.game_state.click()
        
        # Update and show increment
        counter_widget = self.query_one("#counter", CounterDisplay)
        counter_widget.value = self.game_state.counter
        counter_widget.show_increment(increment)
    
    async def action_save(self):
        """Manual save action"""
        await self.db.save_state(self.game_state)
        self.notify("Game saved!", severity="information")
    
    async def on_unmount(self):
        """Clean up on exit"""
        if self.update_timer:
            self.update_timer.stop()
        if self.save_timer:
            self.save_timer.stop()
        await self.db.save_state(self.game_state)

def main():
    """Entry point"""
    app = IdleGame()
    app.run()

if __name__ == "__main__":
    main()
```

### 3.4 Styling
```css
/* src/idle_game/styles/main.tcss */
#main-container {
    align: center middle;
}

#game-area {
    width: 60;
    height: 20;
    border: solid cyan;
    padding: 2;
}

#counter {
    height: 5;
    content-align: center middle;
    margin-bottom: 2;
}

#click-button {
    width: 100%;
    margin-bottom: 1;
}

#click-button:hover {
    background: $primary;
}

#rate-display {
    content-align: center middle;
    color: $text-muted;
}

.notification {
    background: $success;
    color: $text;
    padding: 1;
}
```

## Phase 4: Testing & Development Setup (Day 3)

### 4.1 Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_models.py -v

# Run with coverage
pytest tests/ --cov=src/idle_game --cov-report=term-missing

# Run specific test function
pytest tests/test_models.py::test_offline_calculation -v
```

### 4.2 Local Development

#### Terminal Mode
```bash
# Install dependencies
pip install -r requirements.txt

# Run in development mode with hot reload
textual run --dev src/idle_game/app.py

# Run normally
python -m src.idle_game.app
```

#### Web Mode
```bash
# Install web dependencies
pip install textual-web

# Start web server (default port 8000)
textual-web --app src.idle_game.app:IdleGame

# Custom port
textual-web --app src.idle_game.app:IdleGame --port 3000

# Access at http://localhost:8000
```

### 4.3 Requirements File
```txt
# requirements.txt
textual>=0.47.0
textual-web>=0.6.0
aiosqlite>=0.19.0
python-dateutil>=2.8.2

# Dev dependencies
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
black>=23.0.0
ruff>=0.1.0
mypy>=1.7.0
```

## Phase 5: Deployment Guide

### 5.1 Docker Deployment (Recommended)
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/

# For web version
EXPOSE 8000
CMD ["textual-web", "--app", "src.idle_game.app:IdleGame", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  idle-game:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data  # Persist game saves
    restart: unless-stopped
```

### 5.2 Cloud Deployment Options

#### Option A: Deploy to Fly.io (Free tier available)
```toml
# fly.toml
app = "idle-tui-game"

[build]
  builder = "paketobuildpacks/builder:base"

[[services]]
  internal_port = 8000
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]
    
  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

[mounts]
  source = "data"
  destination = "/app/data"
```

```bash
# Deploy
fly launch
fly deploy
```

#### Option B: Deploy to Railway
```json
// railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "textual-web --app src.idle_game.app:IdleGame --host 0.0.0.0 --port $PORT"
  }
}
```

#### Option C: VPS Deployment (DigitalOcean/Linode)
```bash
# On VPS
git clone <your-repo>
cd idle-tui
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Use systemd for service management
sudo nano /etc/systemd/system/idle-game.service
```

```ini
[Unit]
Description=Idle TUI Game
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/idle-tui
ExecStart=/var/www/idle-tui/venv/bin/textual-web --app src.idle_game.app:IdleGame --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### 5.3 Nginx Reverse Proxy (for production)
```nginx
server {
    listen 80;
    server_name yourgame.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Development Timeline

### Week 1 Sprint
- **Day 1**: Core models, number system, unit tests
- **Day 2**: Database layer, persistence, offline calculation
- **Day 3**: Basic UI, counter widget, click button
- **Day 4**: Polish, auto-save, floating text
- **Day 5**: Testing, deployment setup, documentation

## Success Metrics
- [ ] Counter increments at 1/sec
- [ ] Manual clicks add +10
- [ ] State persists between sessions
- [ ] Offline progression calculated correctly
- [ ] Floating text shows increments
- [ ] Runs in terminal with `textual run`
- [ ] Runs in browser with `textual-web`
- [ ] All unit tests pass
- [ ] Auto-save every 10 seconds
- [ ] Docker container builds and runs

## Future Enhancements (Post-MVP)
1. **Upgrades System**: Buy upgrades to increase auto-increment rate
2. **Prestige Mechanics**: Reset for multipliers
3. **Achievements**: Track milestones
4. **Multiple Resources**: Add different currencies
5. **User Authentication**: Save to cloud, cross-device sync
6. **Leaderboards**: Compare progress with others
7. **Sound Effects**: Audio feedback for actions
8. **Particle Effects**: Better visual feedback
9. **Mobile PWA**: Installable web app
10. **Save Slots**: Multiple save games

## Troubleshooting

### Common Issues
1. **SQLite locked**: Ensure only one instance runs at a time
2. **Web socket errors**: Check firewall/proxy settings
3. **Slow performance**: Reduce update frequency, cache formatted strings
4. **State not saving**: Check file permissions in data/ directory

### Debug Commands
```bash
# Check database
sqlite3 data/game.db "SELECT * FROM game_state;"

# Watch logs
textual run --dev src/idle_game/app.py 2>&1 | tee debug.log

# Profile performance
python -m cProfile -o profile.stats src/idle_game/app.py
```

## Resources
- [Textual Documentation](https://textual.textualize.io/)
- [Textual-Web Guide](https://github.com/Textualize/textual-web)
- [Idle Game Dev Reddit](https://reddit.com/r/incremental_games)
- [Number Formatting Best Practices](./docs/tui/idle-game-number-best-practices.md)