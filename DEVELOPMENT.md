# Development Guide

## Setup

### Prerequisites
- [uv](https://docs.astral.sh/uv/) - Fast Python package manager
- Python 3.11+ (uv can install this for you)
- Git

### Install uv
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via Homebrew
brew install uv

# Or via pip (if you have Python already)
pip install uv
```

### Environment Setup
```bash
# Clone and setup (one command!)
git clone <repository>
cd idle-tui
uv sync --all-extras  # Creates venv, installs all dependencies

# That's it! No manual venv activation needed.
```

### Running the Game

#### Terminal Version
```bash
# Basic run
uv run python -m src.idle_game.app

# With Textual devtools (recommended for development)
uv run textual run --dev src.idle_game.app:IdleGame
```

#### Web Version
The game runs in your browser using Textual's built-in web server. Perfect for testing UI on different devices or sharing with others.

```bash
# Basic web server
uv run textual serve --port 8080 src.idle_game.app:IdleGame

# Then open http://localhost:8080 in your browser

# With hot reload (auto-restarts on code changes)
uv run textual serve --port 8080 --reload src.idle_game.app:IdleGame

# Custom host (allow external connections)
uv run textual serve --host 0.0.0.0 --port 8080 src.idle_game.app:IdleGame
```

**Web Version Features:**
- Runs in any modern browser
- Full feature parity with terminal version
- Responsive layout
- Perfect for demoing or testing on mobile
- No installation needed for end users

## Development Workflows

### Adding New Features

1. **Plan the feature** in docs/game-design/
2. **Update models** in `src/idle_game/models.py`
3. **Add database migrations** if needed
4. **Create/update widgets** in `src/idle_game/widgets/`
5. **Update main app** in `src/idle_game/app.py`
6. **Add tests** in `tests/`
7. **Update documentation**

### Code Quality

All commands automatically use the project's virtual environment via `uv run`:

```bash
# Format code
uv run black src/ tests/
uv run ruff check --fix src/

# Type checking
uv run mypy src/

# Run tests
uv run pytest tests/
uv run pytest tests/ -v  # Verbose
uv run pytest tests/test_models.py::test_specific -v  # Single test

# Run tests with coverage
uv run pytest tests/ --cov=src --cov-report=term-missing

# Run full quality check (recommended before commits)
uv run black src/ tests/ && \
uv run ruff check --fix src/ && \
uv run mypy src/ && \
uv run pytest tests/ -v
```

### Dependency Management

```bash
# Add a new dependency
uv add package-name

# Add a dev dependency
uv add --dev package-name

# Update all dependencies
uv sync --upgrade

# Update specific package
uv add package-name@latest

# Remove a dependency
uv remove package-name

# View installed packages
uv pip list
```

### Database Management

```bash
# Reset game state
uv run python reset_game.py

# Manual reset
rm data/game.db

# Backup save
cp data/game.db data/game.backup.db
```

## Project Structure

```
src/idle_game/
├── app.py              # Main Textual application
├── models.py           # Game state and data models
├── database.py         # SQLite persistence
├── widgets/
│   ├── clicker.py     # Click button widget
│   ├── counter.py     # Resource display widget
│   ├── shop.py        # Customer shop (TODO)
│   └── storage.py     # Emotion storage (TODO)
└── styles/
    └── main.tcss      # Textual CSS styling
```

## Key Components

### GameState Model
- Central game state management
- Handles resource calculations
- Offline progression logic
- Located: `src/idle_game/models.py`

### Database Layer
- Async SQLite with aiosqlite
- Auto-save every 10 seconds
- Offline earnings calculation
- Located: `src/idle_game/database.py`

### Number System
- Uses Decimal for precision
- Supports scientific notation
- Auto-formats with K/M/B/T suffixes
- Located: `src/idle_game/models.py:GameNumber`

### Widget Architecture
- Inherits from Textual's Static/Container
- Reactive properties for auto-updates
- Composed using `compose()` method
- Styled via TCSS files

## Adding New Emotions

1. Define in `models.py`:
```python
@dataclass
class Emotion:
    name: str
    symbol: str
    base_cost: Decimal
    production_rate: Decimal
    storage_capacity: int
    purity: float = 1.0
```

2. Add to database schema
3. Create purchase/upgrade logic
4. Add UI components
5. Test progression balance

## Debug Commands

### Terminal Debug Mode
While running with `textual run --dev`:
- **Ctrl+D** - Open Textual devtools
- **Ctrl+R** - Hot reload CSS
- **Print statements** appear in devtools console

```bash
uv run textual run --dev src.idle_game.app:IdleGame
```

### Web Debug Mode
While running with `textual serve --reload`:
- Auto-reloads on code changes
- Open browser console for JavaScript errors
- Textual logs appear in terminal

```bash
uv run textual serve --port 8080 --reload src.idle_game.app:IdleGame
```

### Console Debugging
```bash
# Run with Textual console for live inspection
uv run textual console

# In another terminal, run the app
uv run python -m src.idle_game.app
```

## Testing Guidelines

- Test save/load cycles
- Verify offline progression
- Check large number handling
- Test all user interactions
- Validate progression balance

## Performance Considerations

- Cache formatted strings
- Batch database operations  
- Limit update frequency (10 FPS)
- Use Decimal only for game math
- Profile with `cProfile` if needed

## Common Issues

### Game won't start
- Check Python version: `python --version` (need 3.11+)
- Reinstall dependencies: `uv sync --all-extras`
- Try: `uv run python -m src.idle_game.app`

### Save not working
- Check data/ directory exists: `mkdir -p data`
- Verify write permissions: `ls -la data/`
- Look for database locks: `lsof data/game.db`

### Display issues in terminal
- Update Textual: `uv add textual@latest`
- Check terminal compatibility (use iTerm2, Windows Terminal, or modern terminal)
- **Try web version instead**: `uv run textual serve --port 8080 src.idle_game.app:IdleGame`

### Web version not loading
- Check port availability: `lsof -i :8080`
- Try different port: `uv run textual serve --port 8081 src.idle_game.app:IdleGame`
- Check browser console for errors
- Ensure textual-serve is installed: `uv add --dev textual-dev`

### uv command not found
- Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Restart terminal to load PATH
- Or use full path: `~/.local/bin/uv`

## Contributing

1. Follow existing code patterns
2. Add tests for new features
3. Update relevant documentation
4. Use type hints consistently
5. Run formatters before commit
