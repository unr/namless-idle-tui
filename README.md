# Idle TUI Game

A terminal-based idle/incremental game built with Python and Textual framework.

**✨ Now with Web Support!** Run the game in your terminal OR in a web browser using the latest Textual version.

## Quick Start

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd idle-tui

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Install development dependencies for web serving
pip install -r requirements-dev.txt
```

### Terminal Version (TUI)

Run the game directly in your terminal:

```bash
python -m src.idle_game.app
```

### Web Browser Version

Serve the game in your web browser using Textual's built-in server:

```bash
# Requires textual-dev to be installed (included in requirements-dev.txt)
textual serve --port 8080 "python -m src.idle_game.app"

# Open browser to http://localhost:8080
```

## Game Controls

- **Click Button** - Adds +10 resources
- **s** - Save game (also auto-saves every 10 seconds)
- **r** - Reset game progress (with confirmation)
- **q** - Quit

## Reset Progress

Three ways to reset your game:

1. **In-game**: Press 'r' while playing
2. **Script**: Run `python3 reset_game.py`
3. **Manual**: Delete `data/game.db`

## Features

- 🔄 Auto-increment resources (1/second)
- 💾 Persistent saves with SQLite
- 🌙 Offline progression calculation
- 🎨 Styled terminal UI
- 🔢 Large number support with suffixes (K, M, B, T, etc.)

## Project Goals

- fast, performant incremental game
- ascii / tui interface
- truly a tui -- can run as a local package in your terminal
- truly a webapp -- can run as a web app as an authenticated user
- cross progression (same account both web+tui)

## Dependencies

### Production
- **Textual** 6.4.0+ - Modern TUI framework
- **aiosqlite** - Async SQLite database
- **pydantic** - Data validation  
- **python-dateutil** - Date/time utilities

### Development  
- **textual-dev** - Includes `textual serve` command for web version
- **pytest** - Testing framework
- **black**, **ruff**, **mypy** - Code quality tools

## Documentation

See [COMPLETE.md](COMPLETE.md) for full documentation on:
- Architecture details
- How to add new features
- Troubleshooting
- Development tips
