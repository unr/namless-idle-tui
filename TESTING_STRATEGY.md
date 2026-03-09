# Testing Strategy for Emotion Merchant

## Overview

This document outlines the testing strategy for the Emotion Merchant idle game. The goal is to achieve comprehensive test coverage of game logic while keeping UI tests separate and manageable.

## Test Categories

### 1. Unit Tests (Core Logic)
**Location**: `tests/unit/`

These tests focus on isolated components without UI dependencies:

#### Models (`tests/unit/test_models.py`)
- **GameState**
  - ✓ Resource initialization
  - ✓ Emotion unlocking
  - ✓ Click harvesting
  - ✓ Producer purchasing
  - ✓ Upgrade purchasing and effects
  - ✓ Tutorial trade execution
  - ✓ Prestige calculation and reset
  - ✓ Ethical score management

- **EmotionResource**
  - ✓ Amount management (add/remove)
  - ✓ Capacity limits
  - ✓ Purity tracking
  - ✓ Storage percentage calculations
  - ✓ Producer count tracking

- **UpgradeManager**
  - ✓ Cost calculation with scaling
  - ✓ Affordability checks
  - ✓ Level tracking
  - ✓ Effect calculation (multipliers)
  - ✓ Max level enforcement

#### Calculators (`tests/unit/test_calculators.py`)
- **ResourceCalculator**
  - ✓ Click power calculation
  - ✓ Production rate calculation
  - ✓ Producer cost scaling
  - ✓ Purity decay over time
  - ✓ Storage state determination
  - ✓ Prestige bonus calculation

#### Game Loop (`tests/unit/test_game_loop.py`)
- **GameLoop**
  - ✓ Passive generation with delta-time
  - ✓ Multi-tier production chains
  - ✓ Purity decay application
  - ✓ Storage capacity overflow
  - ✓ Tutorial milestone checking
  - ✓ Production rate queries

#### Customers (`tests/unit/test_customers.py`)
- **CustomerGenerator**
  - ✓ Tutorial customer triggering
  - ✓ Regular customer generation
  - ✓ Customer type distribution
  - ✓ Returning customer tracking
  - ✓ Dependency level calculation

- **Customer**
  - ✓ Satisfaction calculation
  - ✓ Patience management
  - ✓ Special customer modifiers

#### Save Manager (`tests/unit/test_save_manager.py`)
- **SaveManager**
  - ✓ Game state serialization
  - ✓ Game state deserialization
  - ✓ Version migration
  - ✓ File I/O operations
  - ✓ Offline progression calculation

### 2. Integration Tests
**Location**: `tests/integration/`

These tests verify component interactions:

#### End-to-End Gameplay (`tests/integration/test_gameplay.py`)
- ✓ Full game progression from start to first prestige
- ✓ Tutorial customer sequence
- ✓ Resource production chains
- ✓ Save/load cycle
- ✓ Upgrade purchase and effects

#### Screen Navigation (`tests/integration/test_screens.py`)
- ✓ Screen transitions
- ✓ Data flow between screens
- ✓ Message passing

### 3. UI Tests (Minimal)
**Location**: `tests/ui/`

Keep UI tests minimal and focused on critical paths:

#### Textual Testing (`tests/ui/test_app.py`)
- ✓ App launches successfully
- ✓ Main game screen loads
- ✓ Basic interactions (click, navigate)
- ✓ Screenshot generation

## Test Infrastructure

### Required Dependencies
```toml
[project.optional-dependencies]
test = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
]
```

### Pytest Configuration
**File**: `pyproject.toml`
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
```

### Coverage Goals
- **Overall**: ≥80% coverage
- **Models**: ≥90% coverage
- **Calculators**: ≥95% coverage
- **Game Loop**: ≥85% coverage
- **UI**: ≥50% coverage (basic smoke tests only)

## Testing Best Practices

### 1. Isolation
- Each test should be independent
- Use fixtures to set up clean state
- No shared state between tests

### 2. Fast Execution
- Unit tests should run in <5 seconds total
- Integration tests should run in <30 seconds
- Use mocks for slow operations

### 3. Clarity
- Test names describe what they test
- Use AAA pattern: Arrange, Act, Assert
- One assertion per test (when practical)

### 4. Fixtures
Create reusable fixtures for common scenarios:
```python
@pytest.fixture
def fresh_game_state():
    """Provide a fresh GameState instance."""
    return GameState()

@pytest.fixture
def mid_game_state():
    """Provide a game state with Joy unlocked."""
    state = GameState()
    state.unlock_emotion("joy")
    state.get_resource("smiles").amount = Decimal("100")
    return state
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/idle_game --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_models.py

# Run with verbose output
uv run pytest -v

# Run and show print statements
uv run pytest -s
```

## Continuous Integration

Tests should run on:
- Every commit
- Pull requests
- Pre-deployment

## Test Naming Convention

```
test_<component>_<scenario>_<expected_outcome>

Examples:
- test_gamestate_unlock_emotion_adds_to_unlocked_set
- test_resource_add_amount_respects_capacity
- test_calculator_click_power_applies_multiplier
- test_gameloop_passive_generation_increases_resources
```

## Mocking Strategy

### What to Mock
- File I/O (for save manager tests)
- Time-dependent operations (for decay tests)
- Random number generation (for customer generation)

### What NOT to Mock
- Core game logic
- Resource calculations
- State management

## Edge Cases to Test

1. **Numeric Precision**
   - Very large numbers (Decimal overflow)
   - Very small numbers (near-zero)
   - Negative values (should be prevented)

2. **Boundaries**
   - Empty resources
   - Full storage
   - Max upgrade levels
   - Prestige requirements not met

3. **Invalid States**
   - Unlocking already unlocked emotion
   - Purchasing unaffordable items
   - Trading without sufficient resources

## Performance Tests

For critical paths, verify performance:
- Game loop update completes in <10ms
- Save operation completes in <100ms
- Load operation completes in <100ms

## Documentation

- Keep this document updated as tests evolve
- Document any test data files
- Explain complex test scenarios
