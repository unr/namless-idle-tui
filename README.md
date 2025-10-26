# Idle TUI Game

A terminal-based idle/incremental game built with Python and Textual framework.

**✨ Now with Web Support!** Run the game in your terminal OR in a web browser.

## Quick Start

### Terminal Version (Original)

```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-simple.txt

# Run the game
python -m src.idle_game.app
```

### Web Browser Version (New!)

```bash
# Use Python 3.12.7 for best compatibility
pyenv local 3.12.7

# Create separate environment for web version
/Users/unr/.pyenv/versions/3.12.7/bin/python3 -m venv venv-web
source venv-web/bin/activate

# Install web dependencies
pip install -r requirements-web.txt

# Start web server
python start_web.py

# Open browser to http://localhost:8000
```

See [textual-readme.md](textual-readme.md) for detailed web setup instructions.

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

## Documentation

See [COMPLETE.md](COMPLETE.md) for full documentation on:
- Architecture details
- How to add new features
- Troubleshooting
- Development tips
