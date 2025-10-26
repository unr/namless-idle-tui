# Requirements Files Guide

This project has three different requirements files for different use cases:

## 📦 requirements-simple.txt
**For: Basic Terminal Version**
- Minimal dependencies for running the TUI game
- Uses Textual 0.43.x for stability
- Includes only essential packages

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-simple.txt
python -m src.idle_game.app
```

## 📦 requirements.txt
**For: Full Development Setup**
- All dependencies from requirements-simple.txt
- Plus development tools (black, ruff, mypy)
- Testing frameworks (pytest, coverage)
- Code formatting and linting tools

```bash
python3 -m venv venv-dev
source venv-dev/bin/activate
pip install -r requirements.txt
```

## 📦 requirements-web.txt
**For: Web Browser Version**
- Requires separate virtual environment
- Uses Textual 6.4.0+ (incompatible with TUI version)
- Includes textual-serve for web serving
- Includes aiohttp for web server functionality

```bash
# Use Python 3.12.7 to avoid uvloop issues
pyenv local 3.12.7
/Users/unr/.pyenv/versions/3.12.7/bin/python3 -m venv venv-web
source venv-web/bin/activate
pip install -r requirements-web.txt
python start_web.py
```

## ⚠️ Important Notes

1. **Version Conflict**: The TUI and Web versions use different Textual versions:
   - TUI: Textual 0.43.x (stable, works well in terminal)
   - Web: Textual 6.4.0+ (required by textual-serve)
   
2. **Separate Environments**: Always use separate virtual environments:
   - `venv` for terminal version
   - `venv-web` for web version
   
3. **Python Version**: For web version, use Python 3.12.7 to avoid uvloop installation issues on macOS

## Quick Reference

| Use Case | Requirements File | Virtual Env | Command |
|----------|------------------|-------------|---------|
| Play in Terminal | requirements-simple.txt | venv | `python -m src.idle_game.app` |
| Develop/Test | requirements.txt | venv-dev | `pytest tests/` |
| Play in Browser | requirements-web.txt | venv-web | `python start_web.py` |