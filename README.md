# Emotion Merchant

A terminal-based idle game where you trade in the economy of feelings. Extract emotions from experiences, refine them into pure essence, and serve customers seeking specific emotional states.

## A notice about vibe coding

This is mostly a vibe coded experimental project in my spare time, investigating how to solve ideas for side projects in new technology. The primary focus here is to mess around with python, the terminal, and game design in general. A _vast_ majority of the code written at this time is not written by me.

## Quick Start

### Prerequisites

Install [uv](https://docs.astral.sh/uv/) - a fast Python package manager:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Terminal Version

```bash
# Clone and setup (installs all dependencies automatically)
git clone <repository>
cd namless-idle-tui
uv sync --all-extras

# Run in terminal
uv run python -m src.emotion_merchant.app
```

### Web Version

The app can also run in your browser using Textual's web server:

```bash
# Same setup as above
uv sync --all-extras

# Run web server
uv run textual serve --port 8080 src.emotion_merchant.app:EmotionMerchantApp

# Open http://localhost:8080 in your browser
```

**Why uv?** 10-100x faster than pip, automatic virtual environment management, reproducible builds via lockfile.

## Game Overview

In Emotion Merchant, you:

- **Harvest** smiles through clicks and passive collection
- **Refine** basic emotions into powerful essences
- **Serve** customers with specific emotional needs
- **Manage** purity, storage, and ethical choices
- **Progress** through 10 tiers of emotional complexity

## Core Resources

| Tier | Resource | Cost | Production | Symbol |
|------|----------|------|------------|--------|
| 0 | Smiles | Click: 5 | 1/sec | ☺ |
| 1 | Joy | 10 Smiles | 0.5 Smiles/sec | ❤ |
| 2 | Love | 100 Joy | 2 Joy/sec | 💕 |
| 3 | Nostalgia | 500 Love | 5 Love/sec | ❖ |
| 4 | Serenity | 2.5K Nostalgia | 10 Nostalgia/sec | ◉ |
| 5 | Euphoria | 12.5K Serenity | 50 Serenity/sec | ✧ |
| 6 | Compassion | 62.5K Euphoria | 100 Euphoria/sec | ❀ |
| 7 | Wisdom | 312.5K Compassion | 500 Compassion/sec | ◈ |
| 8 | Transcendence | 1.5M Wisdom | 1K Wisdom/sec | ✵ |
| 9 | Singularity | 10M Transcendence | 10K Transcendence/sec | ∞ |

## Game Controls

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Harvest smiles |
| `t` | Trade with tutorial customer |
| `s` | Save game |
| `p` | Pause/Resume |
| `q` | Quit |

### Mouse

- Click the "CLICK!" button to harvest smiles
- Navigate UI elements with mouse

## Documentation

- [Game Design Docs](docs/game-design/) - Detailed mechanics
- [Technical Docs](docs/technical/) - Architecture and implementation

## Current Features

- Click harvesting for Smiles
- Passive resource generation
- 10-tier emotion resource hierarchy
- Storage capacity management
- Purity system (emotions degrade over time)
- Tutorial customers (event-triggered progression)
- Customer queue system
- Production buildings with exponential cost scaling
- Save/load game state
- Pause/resume functionality
- Three-panel TUI layout (Resources | Game Area | Customers)

## Architecture

```
src/emotion_merchant/
├── app.py                 # Main Textual App
├── game/
│   ├── state.py           # Game state management with observer pattern
│   ├── resources.py       # Emotion tier definitions
│   ├── production.py      # Production engine & storage upgrades
│   └── customers.py       # Customer & tutorial system
├── widgets/
│   ├── resource_panel.py  # Resource display with progress bars
│   ├── clicker.py         # Click harvesting widget
│   └── customer_panel.py  # Customer queue display
└── styles/
    └── main.tcss          # Textual CSS styling
```

## Development

```bash
# Install dev dependencies
uv sync --all-extras

# Run tests
uv run pytest tests/ -v

# Run linting
uv run ruff check src/

# Run the game
uv run python -m src.emotion_merchant.app
```

## License

MIT
