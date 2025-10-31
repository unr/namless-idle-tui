# Core Game Mechanics

## Game Phases

### Phase 1: Tutorial (0-10 minutes)
**Goal**: Learn basic mechanics through guided progression

1. **Click Training** (0-2 min)
   - Manual clicking for Smiles
   - Introduce click power concept
   - Goal: Reach 10 Smiles

2. **First Customer** (2-5 min)
   - Event triggered at 10 Smiles
   - Tutorial customer offers Joy for Smiles
   - Introduces transaction concept
   - Unlocks Joy resource

3. **Production Chain** (5-10 min)
   - Joy generates Smiles passively
   - Introduce auto-increment concept
   - Build up to 50 Joy for next customer

### Phase 2: Early Game (10-30 minutes)
**Goal**: Unlock core emotions and basic systems

- Unlock all 5 primary emotions via customers
- Learn storage management (limited capacity)
- Discover first 2-ingredient recipes
- Reputation system activates
- Queue system unlocks after 5 emotions

### Phase 3: Mid Game (30 min - 2 hours)  
**Goal**: Master emotion economy

- Customer queue management
- Complex 3+ ingredient recipes
- Market fluctuations begin
- Purity management critical
- Storage upgrades essential

### Phase 4: Late Game (2-8 hours)
**Goal**: Reach transcendent tiers

- Wisdom-tier emotions unlock
- Ethical dilemmas intensify
- Customer story arcs complete
- Prepare for first prestige

## Emotion Harvesting

### Manual Harvesting (Clicking)
```
Base Click = 5 Smiles
× Click Power Multiplier (upgrades)
× Mood Bonus (0.5x - 2x)
× Active Boost (temporary)
= Total Harvest
```

### Passive Generation
```
For each Emotion Tier:
  Base Production Rate
  × Building Count
  × Global Multiplier
  × Prestige Bonus
  = Production/sec
```

### Storage Mechanics

**Storage States**:
- **Empty** (0-25%): Fast production
- **Moderate** (25-75%): Normal production  
- **Near Full** (75-95%): Reduced production
- **Full** (95-100%): Production stops
- **Overflow** (>100%): Emotion lost, purity damage

**Storage Upgrades**:
```
Tier 1: Basic Vessels (+50% capacity)
Tier 2: Reinforced Containers (+100% capacity, -10% degradation)
Tier 3: Crystal Storage (+200% capacity, -25% degradation)
Tier 4: Quantum Containment (+500% capacity, -50% degradation)
Tier 5: Infinite Void (∞ capacity, no degradation)
```

## Purity System

### Contamination Sources
1. **Time Decay**: -0.1% per minute in storage
2. **Overflow**: -10% when storage exceeds capacity
3. **Mix Incompatible**: -20% when opposing emotions mix
4. **Random Events**: -5 to -15% from contamination events

### Purification Methods
1. **Filter Process**: Costs 10% of resource, +10% purity
2. **Distillation**: Costs 25% of resource, +25% purity  
3. **Crystallization**: Costs 40% of resource, +50% purity
4. **Perfect Cleanse**: Costs 50% of resource, 100% purity

### Purity Effects
- **Sell Price**: Purity% × Base Price
- **Customer Satisfaction**: +1 star per 20% purity
- **Recipe Success**: Minimum purity requirements
- **Side Effects**: Lower purity = more side effects

## Customer Interaction Flow

### Tutorial Customers (Event-Based)
```
Trigger → Special Customer → Fixed Transaction → Unlock
Example:
10 Smiles → "Joy Seeker" → Trade 10 Smiles for 1 Joy → Joy Unlocked
```

### Queue System (Post-Tutorial)
```
1. Customer arrives (timer/reputation based)
2. Enters queue (max 5 waiting)
3. Player selects customer to serve
4. Analyze emotional need
5. Choose response:
   - Sell appropriate emotion
   - Refuse service
   - Recommend alternative
6. Calculate satisfaction
7. Update reputation/story
```

### Customer Properties
```python
class Customer:
    name: str              # Generated name
    emotional_need: str    # What they want
    budget: Decimal        # Max they can pay
    patience: int         # Turns before leaving
    dependency_risk: float # Addiction potential
    story_id: str         # Links to story arc
    visits: int           # Return customer tracking
```

## Market System

### Price Fluctuations
```
Base Price × Market Modifier × Purity × Reputation
Where Market Modifier cycles between 0.5x - 2x based on:
- Global events
- Supply/demand
- Time of day
- Random events
```

### Market Events
- **Emotional Crisis**: Specific emotion demand +200%
- **Festival Season**: Joy/Love prices +50%
- **Economic Downturn**: All prices -30%
- **Celebrity Endorsement**: Random emotion +100%

## Progression Gates

### Unlock Requirements

**Buildings** (Production):
| Tier | Unlock Requirement |
|------|-------------------|
| Joy Factory | 10 Smiles (customer event) |
| Love Garden | 100 Joy + Customer |
| Nostalgia Mine | 500 Love + Customer |
| Serenity Temple | 2.5K Nostalgia + Customer |
| Euphoria Lab | 12.5K Serenity + Recipe |

**Features**:
- **Alchemy**: Unlock after getting 3 emotions
- **Customer Queue**: Unlock after 5 emotions
- **Market**: Unlock after first prestige
- **Empathy Mode**: 100 customers served
- **Black Market**: 20% ethical score

## Ethical System

### Choice Types
1. **Addiction Management**: Sell to dependent customer?
2. **Purity Standards**: Sell contaminated product?
3. **Price Gouging**: Raise prices during crisis?
4. **Free Service**: Help those who can't pay?

### Ethical Score Calculation
```
Base: 50%
+ Good Choices × 2%
- Bad Choices × 3%
+ Free Services × 1%
- Contaminated Sales × 5%
= Final Score (0-100%)
```

### Score Thresholds
- **80-100%**: Saint Path - Healing bonuses, special customers
- **60-79%**: Good Merchant - Standard gameplay
- **40-59%**: Neutral - Access to all content
- **20-39%**: Questionable - Black market access
- **0-19%**: Dark Path - Maximum profit, locked endings

## Auto-Save System
- Every 10 seconds during active play
- On significant actions (purchases, upgrades)
- Before prestige
- On app close

## Offline Progression
```
Time Offline (seconds)
× Production Rate
× Offline Efficiency (starts 100%, upgradeable)
× Storage Capacity Limit
= Resources Gained

Note: Purity degrades during offline time
```
