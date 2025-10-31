# Emotion Merchant (Name TBD)

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
cd idle-tui
uv sync --all-extras

# Run in terminal
uv run python -m src.idle_game.app
```

### Web Version

The app can also run in your browser using Textual's web server:

```bash
# Same setup as above
uv sync --all-extras

# Run web server
uv run textual serve --port 8080 src.idle_game.app:IdleGame

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

### Terminal Version

- **Click/Space** - Harvest smiles
- **s** - Save game (auto-saves every 10s)
- **r** - Reset progress
- **q** - Quit
- **Tab** - Navigate UI elements

### Web Version

- **Click button** - Harvest smiles
- All keyboard shortcuts work the same as terminal version
- Runs in any modern browser without installation

## Documentation

- [Development Guide](DEVELOPMENT.md) - Setup and workflows
- [Game Design Docs](docs/game-design/) - Detailed mechanics
- [Technical Docs](docs/technical/) - Architecture and implementation
- [Legacy Ideas](docs-legacy/) - Previous design explorations

## Current Features

✅ Basic clicking and idle progression  
✅ Persistent saves with offline progress  
✅ Large number formatting  
✅ Terminal and web support  
⏳ Emotion storage system  
⏳ Customer interactions  
⏳ Alchemy and recipes  
⏳ Shop and upgrades  

## Project Status

**Phase: Early Development**  
Currently implementing core emotion harvesting and storage systems. The basic idle game loop is functional with saves and offline progression.

## License

MIT
