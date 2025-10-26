# Coding Agent Instructions for idle-tui

## Build/Test Commands
- Install dependencies: `pip install textual textual-web decimal aiosqlite pydantic python-dateutil`
- Run TUI app: `textual run --dev src/idle_game/app.py`
- Run web version: `textual-web`
- Run tests: `pytest tests/` or single test: `pytest tests/test_game_state.py::test_function_name -v`
- Format code: `black src/ tests/` and `ruff check --fix src/`
- Type checking: `mypy src/`

## Code Style Guidelines
- Use Python 3.11+ with type hints for all functions
- Follow PEP 8, enforce with Black formatter (line length 100)
- Use Decimal for game numbers, never float (precision issues with large numbers)
- Async/await for all I/O operations (database, file access)
- Dataclasses with frozen=True for immutable game state
- Import order: stdlib, third-party (textual, pydantic), local (absolute imports)
- Error handling: use try/except with specific exceptions, log errors
- Naming: snake_case for functions/variables, PascalCase for classes, CAPS_SNAKE for constants
- Textual widgets: inherit from Static/Container, use compose() for child widgets
- CSS styling: use .tcss files in styles/ directory, follow Textual CSS conventions
- Cache formatted number strings to avoid re-formatting every frame
- Test files mirror src structure with test_ prefix