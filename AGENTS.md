# Coding Agent Instructions for idle-tui

## Build/Test Commands

This project uses **uv** for fast, reproducible dependency management.

- Setup: `uv sync --all-extras`
- Run TUI app: `uv run python -m src.idle_game.app`
- Run web version: `uv run textual serve --port 8080 src.idle_game.app:IdleGame`
- Run web with hot reload: `uv run textual serve --port 8080 --reload src.idle_game.app:IdleGame`
- Run with devtools: `uv run textual run --dev src.idle_game.app:IdleGame`
- Run tests: `uv run pytest tests/` or single test: `uv run pytest tests/test_database.py::test_save_and_load -v`
- Run tests with coverage: `uv run pytest tests/ --cov=src --cov-report=term-missing`
- Format code: `uv run black src/ tests/` and `uv run ruff check --fix src/`
- Type checking: `uv run mypy src/`
- Add dependency: `uv add <package>` or dev: `uv add --dev <package>`
- Update dependencies: `uv sync --upgrade`
- Reset game: `uv run python reset_game.py`

## Testing Both Experiences

This game must work in **both terminal and web** modes. Always test changes in both:

1. **Terminal**: `uv run python -m src.idle_game.app`
2. **Web**: `uv run textual serve --port 8080 src.idle_game.app:IdleGame`

Web version is crucial for:
- Cross-device testing
- Demoing to users without terminal access
- Mobile/tablet compatibility testing
- Easier sharing and collaboration

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

