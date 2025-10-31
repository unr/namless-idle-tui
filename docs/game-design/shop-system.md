# Shop & Customer System

## Customer Generation

### Tutorial Phase Customers

**Event-Triggered Customers** (First 5):

1. **Joy Seeker** (10 Smiles)
   - "I heard you collect smiles. Can I buy some happiness?"
   - Trades: 10 Smiles → 1 Joy
   - Unlocks: Joy resource, basic production

2. **Melancholy Poet** (50 Joy)
   - "I need sadness for my art. Too much joy lately."
   - Trades: 50 Joy → 5 Sadness
   - Unlocks: Sadness emotion, mixing potential

3. **Frustrated Worker** (100 Love)
   - "I'm too content. I need anger to demand change."
   - Trades: 100 Love → 10 Anger
   - Unlocks: Anger emotion, courage recipes

4. **Thrill Seeker** (500 Nostalgia)
   - "Life's too predictable. I need some fear."
   - Trades: 500 Nostalgia → 20 Fear
   - Unlocks: Fear emotion, excitement mixing

5. **Boundary Setter** (1K Serenity)
   - "I need to reject toxic people. Give me disgust."
   - Trades: 1K Serenity → 50 Disgust
   - Unlocks: Disgust, full emotion palette

### Queue System (Post-Tutorial)

**Customer Flow**:
```
Generate → Queue → Selection → Service → Resolution
   ↓         ↓         ↓          ↓          ↓
Timer    Max 5    Player     Success?    Story
Based   Waiting   Chooses    Rating     Update
```

**Generation Rate**:
```
Base: 1 customer per 30 seconds
× Reputation Multiplier (0.5x - 2x)
× Special Event Bonus
× Marketing Upgrades
= Actual Rate
```

## Customer Types

### Regular Customers
- **Random names** from pool
- **Random emotional needs** based on current tier
- **Standard pricing** based on market
- **No special requirements**

### Story Customers
- **Named characters** with backstories
- **Progressive story arcs** (5-10 visits)
- **Specific emotional needs** each visit
- **Consequences** for choices
- **Special rewards** for completing arcs

### Special Customers

**VIP Customers** (High reputation):
- Pay 2x normal price
- Boost reputation significantly
- Require high purity (90%+)
- Leave if not served quickly

**Desperate Customers** (Random):
- Pay 3x price
- Need specific emotion urgently
- Ethical dilemma (exploit or help?)
- Affect ethical score heavily

**Addicted Customers** (Return):
- Previous customers with dependency
- Increasing frequency of visits
- Declining ability to pay
- Major ethical choice point

## Customer Properties

```python
class Customer:
    # Identity
    id: str
    name: str
    avatar: str  # Text emoji/symbol
    
    # Need
    primary_need: EmotionType
    need_intensity: float  # How badly they need it
    acceptable_purity: float  # Minimum quality
    
    # Economics
    budget: Decimal  # Max payment
    patience: int  # Turns before leaving
    
    # Story
    visit_count: int
    satisfaction_history: List[float]
    dependency_level: float  # 0-1 addiction scale
    story_arc: Optional[StoryArc]
    
    # Display
    dialogue: str  # What they say
    emotion_state: str  # Their current mood
```

## Interaction Interface

### Queue Display
```
╔════════════════════════════════╗
║   CUSTOMER QUEUE (3 waiting)   ║
╠════════════════════════════════╣
║ 1. Sarah M. 😰                 ║
║    Needs: Calm (High)          ║
║    Budget: 1,200◊              ║
║    ⏱ Patience: ████──          ║
║                                ║
║ 2. Marcus C. 😢 [RETURNING]    ║
║    Needs: Joy (Desperate)      ║
║    Budget: 800◊                ║
║    ⏱ Patience: ██────          ║
║    ⚠ Dependency Risk: 67%      ║
║                                ║
║ 3. [VIP] Dr. Kim 🎭            ║
║    Needs: Complex Mix          ║
║    Budget: 5,000◊              ║
║    ⏱ Patience: █─────          ║
╠════════════════════════════════╣
║ [1-3] Select  [R]efuse All     ║
╚════════════════════════════════╝
```

### Service Interface
```
╔════════════════════════════════╗
║     SERVING: Marcus Chen        ║
╠════════════════════════════════╣
║ Portrait: 👤                    ║
║ Mood: 😢 Deeply Sad (85%)      ║
║                                ║
║ "The joy you sold me last time ║
║ helped, but it wore off. I     ║
║ need something stronger..."     ║
║                                ║
║ Analysis:                       ║
║ • 5th visit (frequent)          ║
║ • Satisfaction trending down    ║
║ • Showing signs of dependency   ║
║ • May need intervention         ║
╠════════════════════════════════╣
║         YOUR OPTIONS:           ║
╠════════════════════════════════╣
║ 1. [Joy - 85% Pure] - 500◊     ║
║    Standard dose, safe          ║
║                                ║
║ 2. [Enhanced Joy] - 1,500◊     ║
║    Stronger, dependency risk    ║
║                                ║
║ 3. [Therapy Blend] - 2,000◊    ║
║    Helps reduce dependency      ║
║                                ║
║ 4. [Refuse Service]             ║
║    Ethical but lose customer    ║
╠════════════════════════════════╣
║ [1-4] Choose  [E]mpathy Mode    ║
╚════════════════════════════════╝
```

## Satisfaction Calculation

```
Base Satisfaction = 50%
+ Emotion Match Bonus (+30% if exact need)
+ Purity Bonus (+1% per 2% purity above 50%)
+ Price Fairness (+10% if below budget)
+ Speed Bonus (+5% if served quickly)
- Wrong Emotion (-20%)
- Low Purity (-2% per 1% below threshold)
- Overpriced (-15% if above budget)
- Kept Waiting (-5% per patience bar lost)
= Final Satisfaction (0-100%)
```

### Satisfaction Results
- **90-100%**: ⭐⭐⭐⭐⭐ Perfect service
- **70-89%**: ⭐⭐⭐⭐ Great service
- **50-69%**: ⭐⭐⭐ Good service
- **30-49%**: ⭐⭐ Poor service
- **0-29%**: ⭐ Terrible service

## Reputation System

### Reputation Calculation
```
Average of last 20 customer satisfactions
× Ethical score modifier (0.8x - 1.2x)
× Special event bonuses
= Shop Reputation (0-5 stars)
```

### Reputation Effects
- **5 Stars**: VIP customers, +50% prices
- **4 Stars**: More customers, +20% prices
- **3 Stars**: Normal gameplay
- **2 Stars**: Fewer customers, -20% prices
- **1 Star**: Rare customers, -50% prices

## Customer Story Arcs

### Example: Sarah's Journey

**Visit 1**: "I'm anxious about a job interview"
- Needs: Courage or Calm
- Choice affects arc direction

**Visit 2a** (if given Courage): "I got the job! Thank you!"
- Needs: Joy to celebrate
- Satisfaction bonus

**Visit 2b** (if given Calm): "I was too relaxed, didn't get it"
- Needs: Determination
- Lower satisfaction

**Visit 5**: "I rely on your emotions too much..."
- Major choice point
- Can lead to addiction or recovery arc

**Final Visit** (Recovery): "Thank you for refusing me. I got help."
- Rewards: Huge reputation boost, special emotion unlock

### Story Arc Types
1. **Success Story**: Help achieve goals
2. **Dependency Arc**: Deal with addiction
3. **Romance Arc**: Emotional journey of love
4. **Grief Arc**: Processing loss
5. **Growth Arc**: Personal development

## Empathy Mode

**Activation**: Press 'E' when serving customer

**Effects**:
```
You feel their emotions for 30 seconds:
- See their true emotional state
- Understand hidden needs
- Better recommendation accuracy
- Costs emotional energy
- Risk of emotional burnout
```

**Benefits**:
- +20% recipe quality when crafting for them
- Reveals hidden story paths
- +10% satisfaction bonus
- Unlocks special dialogue

## Shop Upgrades

### Customer Service
- **Comfortable Seating**: +1 patience for all customers
- **Mood Music**: +5% base satisfaction
- **Express Lane**: Serve 2 customers simultaneously
- **Appointment System**: Preview upcoming customers
- **VIP Lounge**: Attracts more high-value customers

### Queue Management
- **Larger Waiting Room**: Queue size 5 → 8
- **Priority System**: Reorder queue
- **Triage Nurse**: Auto-sort by urgency
- **Reservation System**: Save customer for later
- **Fast Track**: Reduce service time by 50%

### Reputation
- **Word of Mouth**: +0.1 reputation per perfect service
- **Marketing Campaign**: +20% customer generation
- **Celebrity Endorsement**: Instant +1 star
- **Loyalty Program**: Increase return rate
- **Premium Brand**: All prices +25%
