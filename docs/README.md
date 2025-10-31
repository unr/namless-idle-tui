# Emotion Merchant Documentation

## Quick Navigation

### Game Design
- [📋 Overview](game-design/overview.md) - Core concept and vision
- [💎 Resources](game-design/resources.md) - Emotions, tiers, and currencies  
- [⚙️ Mechanics](game-design/mechanics.md) - Core gameplay systems
- [🛍️ Shop System](game-design/shop-system.md) - Customers and interactions
- [⚗️ Alchemy](game-design/alchemy.md) - Recipe discovery and crafting
- [✨ Prestige](game-design/prestige.md) - Meta-progression system

### Technical
- [🏗️ Architecture](architecture/game-engine.md) - Current implementation
- [💾 Database](technical/database-schema.md) - Data models and storage

### Development
- [🚀 Getting Started](../DEVELOPMENT.md) - Setup and workflows
- [📝 Contributing](../DEVELOPMENT.md#contributing) - Guidelines

## Game Progression Overview

```mermaid
graph LR
    A[Click Smiles] --> B[First Customer]
    B --> C[Unlock Joy]
    C --> D[More Customers]
    D --> E[5 Primary Emotions]
    E --> F[Alchemy System]
    F --> G[Customer Queue]
    G --> H[Complex Recipes]
    H --> I[Transcendence]
    I --> J[Prestige/Rebirth]
    J --> A
```

## Current Development Phase

**✅ Completed:**
- Basic idle game loop
- Click and passive generation
- Save/load system
- Offline progression
- Large number handling
- TUI and web support

**🚧 In Progress:**
- Emotion resource system
- Storage mechanics
- Customer interactions

**📋 Planned:**
- Recipe discovery
- Purity system
- Customer stories
- Market dynamics
- Prestige system
- Ethical choices

## Key Features

### Emotion Economy
- 10 tiers of emotional resources
- Storage management crucial
- Purity affects value
- Market-driven pricing

### Customer Relationships  
- Event-triggered tutorial
- Queue system for choices
- Story arcs with consequences
- Addiction and dependency mechanics

### Alchemy System
- Progressive complexity (1→2→3+ ingredients)
- Discovery through experimentation
- Success rates and contamination
- Special and forbidden recipes

### Ethical Gameplay
- Meaningful moral choices
- Long-term consequences
- Multiple endings
- Affects progression and unlocks

## Resource Quick Reference

| Symbol | Emotion | Tier |
|--------|---------|------|
| ☺ | Smiles | 0 |
| ❤ | Joy | 1 |
| 💕 | Love | 2 |
| ❖ | Nostalgia | 3 |
| ◉ | Serenity | 4 |
| ✧ | Euphoria | 5 |
| ❀ | Compassion | 6 |
| ◈ | Wisdom | 7 |
| ✵ | Transcendence | 8 |
| ∞ | Singularity | 9 |

## Documentation Standards

- **Game Design**: Focus on mechanics and player experience
- **Technical**: Implementation details and code structure
- **Examples**: Use game-relevant scenarios
- **Updates**: Keep synchronized with implementation

## Questions or Feedback?

- Check [Development Guide](../DEVELOPMENT.md) for setup help
- Review [Game Overview](game-design/overview.md) for design philosophy
- Submit issues on GitHub for bugs or suggestions
