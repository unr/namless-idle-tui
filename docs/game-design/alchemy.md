# Emotion Alchemy System

## Recipe Progression

### Tutorial Phase (1 Ingredient)
Simple conversions to teach basics:
- **10 Smiles → 1 Joy** (via customer)
- **50 Joy → 5 Sadness** (via customer)
- **100 Love → 10 Anger** (via customer)

### Early Game (2 Ingredients)
Basic combinations unlocked after 3 emotions:

| Recipe | Ingredients | Output | Success Rate |
|--------|------------|--------|--------------|
| Bittersweet | 60% Joy + 40% Sadness | Nostalgia ×2 | 90% |
| Courage | 70% Anger + 30% Fear | Determination | 85% |
| Excitement | 50% Joy + 50% Fear | Thrill | 88% |
| Melancholy | 80% Sadness + 20% Love | Wistfulness | 92% |

### Mid Game (3 Ingredients)
Complex emotions requiring balance:

| Recipe | Ingredients | Output | Success Rate |
|--------|------------|--------|--------------|
| Hope | 40% Joy + 30% Sadness + 30% Determination | Hope (Rare) | 75% |
| Compassion | 40% Love + 30% Sadness + 30% Joy | Empathy | 70% |
| Wisdom | 33% each Joy/Sadness/Anger | Understanding | 65% |
| Zen | 50% Serenity + 25% Joy + 25% Sadness | Perfect Calm | 60% |

### Late Game (4+ Ingredients)
Master alchemist recipes:
- **Transcendence**: All 5 primary emotions in perfect balance
- **Emotional Singularity**: Every emotion type (10+ ingredients)
- **The Void**: Absence created from opposing emotions
- **Pure Experience**: Distilled essence of all feelings

## Recipe Discovery

### Discovery Methods

1. **Tutorial Recipes**: Given automatically
2. **Experimentation**: Try combinations
3. **Customer Hints**: "I heard mixing joy and sadness..."
4. **Recipe Books**: Found or purchased
5. **Master Alchemists**: Special NPCs teach recipes

### Experimentation System

```
SELECT INGREDIENTS:
[Joy: 0-100%] ████████──
[Sadness: 0-100%] ████──────
[Anger: 0-100%] ──────────
Total: 120% (Warning: Unstable!)

PREDICTED OUTCOME:
- 45% Chance: Bittersweet Memory
- 30% Chance: Contaminated Mix
- 20% Chance: Unknown Recipe
- 5% Chance: Explosion!

[ATTEMPT] [ADJUST] [CANCEL]
```

### Discovery Rewards
- First discovery: +100 XP
- Perfect mix (100% purity): +50 XP
- Discover all variants: Achievement
- Share recipe: Reputation boost

## Recipe Properties

```python
class Recipe:
    name: str
    ingredients: Dict[EmotionType, float]  # Type → percentage
    output: EmotionType
    output_quantity: Decimal
    
    # Requirements
    min_purity_required: float  # Input purity
    alchemist_level: int  # Skill requirement
    special_equipment: List[str]  # Needed tools
    
    # Chances
    base_success_rate: float
    contamination_risk: float
    discovery_chance: float  # For unknowns
    
    # Results
    output_purity: float  # Result quality
    side_products: List[EmotionType]  # Byproducts
    
    # Meta
    discovered: bool
    times_crafted: int
    best_purity_achieved: float
```

## Crafting Interface

### Basic Mixing
```
╔════════════════════════════════╗
║      ALCHEMY LABORATORY         ║
╠════════════════════════════════╣
║ Known Recipe: COURAGE           ║
║                                ║
║ Required:                       ║
║   70% Anger (Have: 145K)       ║
║   30% Fear (Have: 89K)         ║
║                                ║
║ Output: 1 Courage Vial          ║
║ Success Rate: 85%               ║
║ Purity: ~78% (Based on inputs)  ║
║                                ║
║ [CRAFT] [CRAFT 10x] [DETAILS]  ║
╚════════════════════════════════╝
```

### Advanced Mixing
```
╔════════════════════════════════╗
║    EXPERIMENTAL ALCHEMY         ║
╠════════════════════════════════╣
║ Custom Mix                      ║
║                                ║
║ Joy      [████████──] 42%      ║
║ Sadness  [██████────] 31%      ║
║ Fear     [████──────] 18%      ║
║ Love     [██────────] 9%       ║
║ ─────────────────────           ║
║ Total:   100% ✓                 ║
║                                ║
║ Possible Outcomes:              ║
║   65% - Hope                    ║
║   20% - Anxiety                 ║
║   10% - Unknown                 ║
║   5%  - Failure                 ║
║                                ║
║ [EXPERIMENT] [SAVE] [RESET]     ║
╚════════════════════════════════╝
```

## Success Factors

### Success Rate Calculation
```
Base Success Rate (from recipe)
+ Alchemist Level Bonus (+2% per level)
+ Equipment Bonus (+5-15%)
+ Purity Bonus (+1% per 5% above minimum)
- Contamination (-5% if any input <50% pure)
- Complexity Penalty (-5% per ingredient over 3)
= Final Success Rate (capped at 95%)
```

### Failure Types

1. **Minor Failure** (50% of failures)
   - Lose 50% of ingredients
   - Get contaminated sludge
   - Can be purified for 25% recovery

2. **Major Failure** (35% of failures)
   - Lose all ingredients
   - Equipment needs cleaning
   - -5% success rate for next attempt

3. **Catastrophic** (10% of failures)
   - Explosion! Lose all ingredients
   - Damage nearby stored emotions
   - Equipment damaged (needs repair)

4. **Interesting Failure** (5% of failures)
   - Discover new recipe!
   - Create unexpected emotion
   - Gain bonus XP

## Equipment & Tools

### Basic Equipment
- **Mixing Bowl**: Default, no bonus
- **Glass Beakers**: +5% success rate
- **Centrifuge**: +10% purity output
- **Distillery**: Can purify ingredients first

### Advanced Equipment
- **Crystallization Chamber**: +15% purity, +10% success
- **Quantum Mixer**: Mix 5+ ingredients safely
- **Emotion Synthesizer**: Create emotions from nothing
- **Philosopher's Stone**: 100% success rate

### Equipment Upgrades
```
Level 1: Basic → +0% bonus
Level 2: Improved → +5% success, +5% purity
Level 3: Advanced → +10% success, +10% purity
Level 4: Master → +15% success, +20% purity
Level 5: Legendary → +25% success, +30% purity
```

## Special Recipes

### Forbidden Emotions
Unlocked through special means:

**Schadenfreude** (Joy from others' pain)
- 60% Joy + 40% Sadness (from someone else)
- Ethical cost: -10% score
- Sells for 5x normal price

**Ennui** (Sophisticated boredom)
- Equal parts of all emotions, left to stagnate
- Takes real-time hour to craft
- Sought by intellectuals

**The Void** (Absence of feeling)
- Mix opposing emotions to cancel out
- 50% Joy + 50% Sadness → Numbness → Void
- Dangerous but valuable

### Seasonal Recipes
Available only during certain times:

**Holiday Cheer** (December)
- 70% Joy + 20% Nostalgia + 10% Love
- Triple price during season

**Summer Romance** (June-August)
- 60% Love + 30% Excitement + 10% Fear
- Popular with young customers

**Autumn Melancholy** (September-November)
- 50% Nostalgia + 40% Sadness + 10% Serenity
- Artists pay premium

## Recipe Book UI

```
╔════════════════════════════════╗
║        RECIPE BOOK              ║
╠════════════════════════════════╣
║ Discovered: 47/200              ║
║ Mastered: 23/200                ║
║                                ║
║ [BASIC]    ████████ 15/15      ║
║ [ADVANCED] ████──── 22/50      ║
║ [MASTER]   ██────── 10/75      ║
║ [LEGENDARY] ─────── 0/50       ║
║ [SECRET]   ???──── 3/??        ║
║                                ║
║ Recent Discovery:               ║
║ "Hopeful Melancholy"            ║
║ A bittersweet hope for future   ║
║                                ║
║ [BROWSE] [SEARCH] [FAVORITES]   ║
╚════════════════════════════════╝
```

## Alchemy Progression Goals

### Early Goals
- Discover 10 recipes
- Achieve 90% purity output
- Craft 100 emotional items

### Mid Goals  
- Discover 50 recipes
- Master 25 recipes (craft 10+ times)
- Create a perfect 100% pure emotion

### Late Goals
- Discover all basic recipes
- Create forbidden emotions
- Achieve Emotional Singularity

### ??? Goals (Hidden)
- Create an emotion that doesn't exist
- Mix emotions from 10 different customers
- Discover the "True Happiness" recipe
- Craft using only contaminated inputs
- Create perfect Void
