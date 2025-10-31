# Emotion Resources

## Resource Hierarchy

### Primary Currency Chain

| Tier | Resource | Base Cost | Production | Storage | Symbol |
|------|----------|-----------|------------|---------|--------|
| 0 | Smiles | Click: 5 | 1/sec base | 100 → ∞ | ☺ |
| 1 | Joy | 10 Smiles | 0.5 Smiles/sec | 50 → 10K | ❤ |
| 2 | Love | 100 Joy | 2 Joy/sec | 25 → 5K | 💕 |
| 3 | Nostalgia | 500 Love | 5 Love/sec | 10 → 1K | ❖ |
| 4 | Serenity | 2.5K Nostalgia | 10 Nostalgia/sec | 5 → 500 | ◉ |
| 5 | Euphoria | 12.5K Serenity | 50 Serenity/sec | 3 → 100 | ✧ |
| 6 | Compassion | 62.5K Euphoria | 100 Euphoria/sec | 2 → 50 | ❀ |
| 7 | Wisdom | 312.5K Compassion | 500 Compassion/sec | 1 → 25 | ◈ |
| 8 | Transcendence | 1.5M Wisdom | 1K Wisdom/sec | 1 → 10 | ✵ |
| 9 | Singularity | 10M Transcendence | 10K Transcendence/sec | 1 → 5 | ∞ |

### Storage Progression

**Early Game** (Tiers 0-3):
- Start with minimal storage
- First upgrades are storage expansions
- Creates resource management decisions

**Mid Game** (Tiers 4-6):
- Storage becomes less restrictive
- Focus shifts to production optimization
- Special storage for rare emotions

**Late Game** (Tiers 7-9):
- Nearly unlimited basic storage
- Constraints on highest tier resources
- Storage quality affects purity

### Primary Emotions (Unlocked via customers)

| Emotion | Color | Unlock Trigger | Use Case |
|---------|-------|----------------|----------|
| Joy | Yellow | First customer (10 Smiles) | Basic positive recipes |
| Sadness | Blue | Second customer (50 Joy) | Nostalgia, bittersweet |
| Anger | Red | Third customer (100 Love) | Courage, determination |
| Fear | Purple | Fourth customer (500 Nostalgia) | Excitement, caution |
| Disgust | Green | Fifth customer (1K Serenity) | Boundaries, rejection |

## Purity System

### Purity Levels
- **100%**: Pure - Perfect quality, premium price
- **75-99%**: Clean - Good quality, standard price
- **50-74%**: Mixed - Noticeable impurities, reduced price
- **25-49%**: Contaminated - Poor quality, barely sellable
- **0-24%**: Corrupted - Dangerous, cannot sell

### Purity Factors
1. **Storage Time**: Emotions degrade slowly over time
2. **Container Quality**: Better storage = slower degradation
3. **Mixing**: Incompatible emotions reduce purity
4. **Contamination Events**: Random events can affect batches
5. **Purification**: Can spend resources to improve purity

### Purity Mechanics
```
Base Purity = 100%
- (Time in Storage × 0.1% per minute)
- (Contamination Events × 10%)
+ (Purification Process × 20%)
× (Container Quality Multiplier)
= Final Purity
```

## Secondary Resources

### Experience Points (XP)
- **Source**: Customer interactions, discoveries
- **Use**: Unlock new features, recipes, upgrades
- **Cannot be purchased**: Earned only through gameplay
- **Persistent**: Carries through prestige

### Mood Rating
- **Range**: 0-5 stars
- **Affects**: Customer frequency, prices, unlock requirements
- **Improved by**: Good service, ethical choices
- **Reduced by**: Failed customers, selling contaminated emotions

### Ethical Score
- **Range**: 0-100%
- **Tracks**: Player's moral choices
- **Affects**: Ending, special customers, unique emotions
- **Examples**:
  - (+) Refusing addicted customers
  - (+) Fair pricing during crises
  - (-) Selling contaminated emotions
  - (-) Creating dependencies

### Emotional Depth (Prestige Currency)
- **Formula**: (Recipes × Satisfaction × Ethics) / 100
- **Benefits**: +3% all production per point
- **Unlocks**: Meta upgrades, forbidden emotions
- **Stacks**: Multiplicatively across prestiges

## Resource Interactions

### Conversion Chains
```
Smiles → Joy → Love → Nostalgia → Serenity
                ↓         ↓           ↓
            Customer   Recipe     Complex
            Stories    System     Emotions
```

### Resource Gates

**Tutorial Phase** (0-10 min):
- Click for Smiles
- First customer at 10 Smiles → Unlocks Joy
- Second customer at 50 Joy → Unlocks Sadness
- Third customer at 100 Love → Unlocks Anger

**Early Game** (10-30 min):
- Unlock remaining primary emotions
- Begin basic recipes (2 ingredients)
- Storage management becomes important

**Mid Game** (30 min - 2 hrs):
- Complex recipes (3+ ingredients)
- Customer queue system activates
- Market fluctuations begin

## Visual Indicators

### Resource Display Format
```
Smiles: 8.47K [████████──] 85/100
         ↑        ↑           ↑
      Amount   Storage    Capacity
               Visual
```

### Purity Indicators
- ◊◊◊◊◊ = 100% Pure (5 diamonds)
- ◊◊◊◊ = 80% Clean (4 diamonds)
- ◊◊◊ = 60% Mixed (3 diamonds)
- ◊◊ = 40% Contaminated (2 diamonds)
- ◊ = 20% Corrupted (1 diamond)

### Production Indicators
- ↑ Rising (increasing production)
- → Stable (constant rate)
- ↓ Falling (decreasing/contamination)
- ⚠ Warning (storage nearly full)
- 🔒 Locked (requires unlock)
