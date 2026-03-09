# Emotion Merchant - Go/Bubble Tea Version

A terminal-based idle game about harvesting and refining emotions, built with [Bubble Tea](https://github.com/charmbracelet/bubbletea) framework in Go.

## About

Emotion Merchant is an idle/incremental game where you:
- Harvest Smiles by clicking
- Unlock higher-tier emotions (Joy, Love, Hope, Nostalgia, Pride, Gratitude, Serenity, Transcendence)
- Build producers that automatically generate lower-tier emotions
- Manage purity and storage capacity
- Prestige for permanent bonuses (Emotional Depth)

## Features

✅ **Complete Bubble Tea UI** with multiple screens
✅ **10 FPS game loop** with delta-time calculations
✅ **9 emotion tiers** with production chains
✅ **Prestige system** for permanent bonuses
✅ **JSON save/load** system
✅ **Keyboard-driven** interface
✅ **Auto-save** on quit
✅ **Mouse support** (where applicable)

## Installation

### Prerequisites

- Go 1.20 or higher

### Build from Source

```bash
# Clone the repository
git clone https://github.com/unr/emotion-merchant
cd emotion-merchant

# Build
go build -o emotion-merchant .

# Run
./emotion-merchant
```

### Quick Start (Binary)

If you have a pre-built binary:

```bash
chmod +x emotion-merchant
./emotion-merchant
```

## Controls

### Navigation
- `1` - Game Screen (main view with resources)
- `2` - Producers Screen (buy/manage producers)
- `3` - Stats Screen (view statistics and multipliers)
- `4` - Prestige Screen (emotional rebirth)
- `5` - Help Screen (this help)

### Actions
- `h` - Harvest Smiles (manual click)
- `j` - Quick buy Joy producer
- `o` - Quick buy Love producer
- `p` - Prestige (when requirements met)

### System
- `s` - Save game manually
- `l` - Load saved game
- `q` or `Ctrl+C` - Quit (auto-saves)

## Game Mechanics

### Emotion Tiers

| Tier | Emotions | Produces |
|------|----------|----------|
| 0 (Basic) | Smiles | - (harvested by clicking) |
| 1 (Simple) | Joy | Smiles |
| 2 (Complex) | Love, Hope | Joy |
| 3 (Nuanced) | Nostalgia, Pride | Love/Hope |
| 4 (Deep) | Gratitude, Serenity | Nostalgia/Pride |
| 5 (Profound) | Transcendence | Gratitude |

### Production Chain

Producers for higher-tier emotions automatically generate lower-tier emotions:
- Joy producers generate Smiles
- Love producers generate Joy
- Nostalgia producers generate Love
- And so on...

### Prestige (Emotional Rebirth)

When you meet the requirements:
- **Minimum:** 3 recipes discovered, 10 customers served
- **Gain:** Emotional Depth (permanent production bonus)
- **Keep:** Emotional Depth, prestige count, ethical score
- **Lose:** All resources, producers, unlocks (except Smiles), upgrades

Each point of Emotional Depth grants **+3% to all production**.

### Storage & Purity

- Each emotion has **storage capacity** that limits how much you can hold
- **Purity** decays over time (0.1% per minute) and affects value
- **Full storage** (95%+) stops production
- **Overflow** damages purity and wastes resources

## Project Structure

```
emotion-merchant/
├── main.go              # Entry point
├── game/                # Game logic (Go)
│   ├── emotions.go      # Emotion definitions
│   ├── resources.go     # Resource management
│   ├── state.go         # Game state
│   ├── calculator.go    # Production formulas
│   └── loop.go          # Game loop
├── ui/                  # Bubble Tea UI
│   ├── model.go         # Main Model (Init/Update/View)
│   ├── view.go          # View rendering for all screens
│   ├── styles.go        # Lipgloss styles
│   └── messages.go      # Custom message types
├── persistence/         # Save/Load
│   └── save.go          # JSON serialization
└── README_GO.md         # This file
```

## Architecture

Built using **The Elm Architecture** (Model-Update-View):

- **Model:** Complete game state (resources, unlocks, statistics)
- **Update:** Processes messages (clicks, purchases, ticks)
- **View:** Renders the current screen based on model state

### Message Types

- `TickMsg` - Game loop tick (10 FPS)
- `HarvestMsg` - Manual click
- `PurchaseProducerMsg` - Buy a producer
- `PrestigeMsg` - Perform prestige
- `SaveGameMsg` / `LoadGameMsg` - Persistence
- `ChangeScreenMsg` - Navigation

## Save Files

Games are automatically saved to: `~/.emotion-merchant/save.json`

Save format is JSON for easy inspection and debugging.

## Dependencies

- [Bubble Tea](https://github.com/charmbracelet/bubbletea) - TUI framework
- [Lipgloss](https://github.com/charmbracelet/lipgloss) - Terminal styling
- [Decimal](https://github.com/shopspring/decimal) - Precise number handling

## Development

### Run in Development

```bash
go run .
```

### Build Optimized Binary

```bash
go build -ldflags="-s -w" -o emotion-merchant .
```

### Clean Build

```bash
go clean
rm -f emotion-merchant
```

## Comparison with Python Version

The original Python version uses **Textual** framework. This Go version:

| Feature | Python/Textual | Go/Bubble Tea |
|---------|----------------|---------------|
| Language | Python 3.11+ | Go 1.20+ |
| Framework | Textual | Bubble Tea |
| Architecture | Reactive/Widget-based | Elm Architecture |
| Binary Size | ~50MB (PyInstaller) | ~5MB (native) |
| Startup Time | ~1-2s | <100ms |
| Memory Usage | ~80MB | ~10MB |
| Web Support | ✅ Yes | ❌ No (terminal only) |
| Cross-platform | ✅ Yes | ✅ Yes |

Both versions implement the same core game mechanics.

## License

MIT

## Credits

Built with love using Charm's excellent Go TUI libraries.
