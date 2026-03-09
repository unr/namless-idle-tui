# Integration Strategy Analysis

## Task 1: Wire ActionButtons' HarvestClicked message to GameState.perform_click()

### Strategy A: Direct Widget-to-State Coupling
**Approach:**
- ActionButtons receives game_state reference in constructor
- On button press, directly calls `game_state.perform_click()`
- Widget updates own display from game_state reactive attributes

**Pros:**
- Simple and direct
- Less code overhead
- Immediate feedback

**Cons:**
- Tight coupling between widget and state
- Harder to test in isolation
- Less flexible for future changes
- Not idiomatic Textual

### Strategy B: Message-Based Event System ✅ **CHOSEN**
**Approach:**
- ActionButtons posts HarvestClicked message on button press
- GameScreen or App listens for the message
- Message handler calls `game_state.perform_click()`
- Updates propagate via reactive data binding

**Pros:**
- Separation of concerns
- Textual-idiomatic (message passing is core pattern)
- Easy to test components independently
- Flexible - can add multiple listeners
- Follows existing ProducerPurchased pattern

**Cons:**
- Slightly more code
- One extra layer of indirection

**Decision:** Choose **Strategy B** - it's the proper Textual pattern and maintains clean architecture.

---

## Task 2: Connect ProducerPurchased messages to GameState.purchase_producer()

### Strategy A: Direct State Reference in ProducerButton
**Approach:**
- ProducerButton has game_state injected in constructor
- On purchase button click, directly calls `game_state.purchase_producer()`
- Widget updates own cost/count display from state

**Pros:**
- Direct and straightforward
- Minimal message passing

**Cons:**
- Each ProducerButton needs state reference
- Tight coupling
- Harder to mock for testing

### Strategy B: Message Bubbling to Parent ✅ **CHOSEN**
**Approach:**
- ProducerButton posts ProducerPurchased message (already implemented!)
- Parent (GameScreen) handles the message
- Handler calls `game_state.purchase_producer(emotion_type, count)`
- Updates propagate back to widgets via reactives

**Pros:**
- Already partially implemented
- Clean separation
- Parent coordinates all state changes
- Consistent with Textual patterns

**Cons:**
- Message handling overhead

**Decision:** Choose **Strategy B** - message is already defined, just need to handle it.

---

## Task 3: Update ResourcePanel widgets from GameState reactive attributes

### Strategy A: Manual Polling with Timer
**Approach:**
- GameScreen has update timer (10 FPS)
- On each tick, reads `game_state.resources`
- Manually pushes values to ResourceDisplay widgets
- Widgets have `update_values(amount, purity, rate)` methods

**Pros:**
- Simple to understand
- Explicit control over update timing

**Cons:**
- Updates even when nothing changed (inefficient)
- Manual synchronization code
- Not using Textual's reactive system
- More code to maintain

### Strategy B: Reactive Data Binding ✅ **CHOSEN**
**Approach:**
- GameScreen passes game_state to ResourcePanel
- ResourcePanel creates ResourceDisplay for each emotion
- Each ResourceDisplay binds to specific game_state.resources[emotion]
- When GameState updates resources, widgets auto-update via watchers
- Use game loop to update game_state, widgets follow automatically

**Pros:**
- Automatic updates only when data changes
- Uses Textual's reactive system properly
- Efficient - no unnecessary updates
- Less code - no manual synchronization
- Declarative rather than imperative

**Cons:**
- Need to understand reactive system
- Slightly more setup

**Decision:** Choose **Strategy B** - leverages Textual's strengths, more efficient.

---

## Task 4: Add tutorial customer trigger checks in game loop

### Strategy A: Check in Game Loop Tick ✅ **CHOSEN**
**Approach:**
- In `_game_loop_tick()`, call `check_tutorial_triggers()`
- Compare current resources to tutorial customer thresholds
- If threshold crossed and not yet completed, generate customer
- Add to customer queue
- Mark tutorial as completed

**Pros:**
- Simple and centralized
- Runs in game loop where state changes happen
- Easy to debug
- Tutorial checks are infrequent (only 5 total)

**Cons:**
- Runs every game tick (but very cheap check)

### Strategy B: Reactive Watchers on Resources
**Approach:**
- Create watchers for each resource amount
- When resource crosses threshold, trigger customer
- Requires watching 10 resources × 5 thresholds = complex

**Pros:**
- Only triggers on actual changes
- More "reactive" approach

**Cons:**
- Complex setup (multiple watchers)
- Harder to coordinate (what if multiple triggers at once?)
- Overkill for 5 one-time events
- More code to maintain

**Decision:** Choose **Strategy A** - simpler, easier to maintain, adequate for 5 one-time checks.

---

## Task 5: Implement missing screens (shop, prestige)

### Strategy A: Full Implementation Matching Design Docs
**Approach:**
- Implement complete shop system with all upgrade categories
- Full prestige screen with all meta-upgrade options
- All features from design docs (storage upgrades, production multipliers, etc.)
- Complete ethical/reputation systems

**Pros:**
- Feature-complete immediately
- Matches design vision

**Cons:**
- 6-8 hours of work before playable
- Can't test core gameplay loop until done
- Might discover design issues late
- Over-engineering risk

### Strategy B: Minimal Viable Implementation ✅ **CHOSEN**
**Approach:**
- **Shop:** 3-5 essential upgrades only
  - Click power upgrade
  - One storage upgrade
  - One production multiplier
  - Simple purchase screen
- **Prestige:** Basic screen with ED calculation and reset
  - Show ED earned
  - Confirm reset button
  - Display production bonus
  - Can add meta-upgrades later

**Pros:**
- Get to playable state in 2-3 hours
- Test core gameplay loop sooner
- Iterate based on actual play
- Add more upgrades as needed
- Agile approach

**Cons:**
- Not feature-complete initially
- Need to add more later

**Decision:** Choose **Strategy B** - get to playable faster, iterate based on testing.

---

## Implementation Order

1. **Wire game state to UI** (1-2 hours)
   - Connect message handlers
   - Set up reactive data binding
   - Wire game loop to update state

2. **Add tutorial customer triggers** (30 min)
   - Implement trigger checks in game loop
   - Test first customer appears at 10 Smiles

3. **Minimal shop system** (1-2 hours)
   - Define 5 essential upgrades
   - Create simple shop screen
   - Implement purchase logic

4. **Basic prestige screen** (1 hour)
   - ED calculation display
   - Reset confirmation
   - Production bonus display

5. **End-to-end testing** (1-2 hours)
   - Play through tutorial
   - Test resource generation
   - Verify save/load
   - Test offline progression

6. **Update README** (30 min)
   - Installation instructions
   - How to play
   - Feature status
   - Development info

**Total estimated time: 6-9 hours to fully playable game**

---

## Key Architectural Decisions

1. **Message passing** for all user actions (clicks, purchases)
2. **Reactive data binding** for automatic UI updates
3. **Centralized state** in GameState with game loop updates
4. **Minimal viable features** to reach playable state faster
5. **Incremental improvement** based on playtesting

This approach balances clean architecture with practical delivery.
