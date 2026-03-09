"""Recipe definitions for the emotion alchemy system.

This module contains all discoverable recipes organized by difficulty tier.
Recipes define how emotions can be combined to create new emotions.
"""

from decimal import Decimal
from typing import Dict, List, Optional
from enum import Enum


class RecipeDifficulty(Enum):
    """Recipe difficulty tiers."""
    TUTORIAL = "tutorial"
    BASIC = "basic"
    ADVANCED = "advanced"
    MASTER = "master"
    LEGENDARY = "legendary"
    SECRET = "secret"


class RecipeData:
    """Data class for recipe definitions."""

    def __init__(
        self,
        name: str,
        ingredients: Dict[str, float],
        output: str,
        output_quantity: Decimal,
        base_success_rate: float,
        min_purity_required: float,
        difficulty: RecipeDifficulty,
        description: str,
        alchemist_level: int = 0,
        special_equipment: Optional[List[str]] = None,
        contamination_risk: float = 0.1,
        discovery_chance: float = 0.0,
        side_products: Optional[Dict[str, Decimal]] = None,
        tags: Optional[List[str]] = None,
    ):
        """Initialize recipe data.

        Args:
            name: Display name of the recipe
            ingredients: Dict mapping emotion type to percentage (must sum to 100)
            output: Emotion type produced
            output_quantity: Amount of output produced
            base_success_rate: Base chance of success (0.0 to 1.0)
            min_purity_required: Minimum purity of inputs required
            difficulty: Recipe difficulty tier
            description: Flavor text describing the recipe
            alchemist_level: Minimum level required to attempt
            special_equipment: List of required equipment
            contamination_risk: Chance of contamination on failure
            discovery_chance: Chance to discover when experimenting
            side_products: Optional byproducts from successful crafting
            tags: Optional categorization tags
        """
        self.name = name
        self.ingredients = ingredients
        self.output = output
        self.output_quantity = output_quantity
        self.base_success_rate = base_success_rate
        self.min_purity_required = min_purity_required
        self.difficulty = difficulty
        self.description = description
        self.alchemist_level = alchemist_level
        self.special_equipment = special_equipment or []
        self.contamination_risk = contamination_risk
        self.discovery_chance = discovery_chance
        self.side_products = side_products or {}
        self.tags = tags or []

        # Validate ingredients sum to 100%
        total = sum(ingredients.values())
        if abs(total - 100.0) > 0.01:
            raise ValueError(f"Ingredients must sum to 100%, got {total}%")


# =============================================================================
# TUTORIAL PHASE (1 Ingredient)
# =============================================================================
# Note: Tutorial recipes are handled by the customer system
# These are simple conversions taught through customers

# =============================================================================
# EARLY GAME (2 Ingredients)
# =============================================================================

BITTERSWEET = RecipeData(
    name="Bittersweet",
    ingredients={"Joy": 60.0, "Sadness": 40.0},
    output="Nostalgia",
    output_quantity=Decimal("2.0"),
    base_success_rate=0.90,
    min_purity_required=50.0,
    difficulty=RecipeDifficulty.BASIC,
    description="Joy and sadness intertwine to create precious memories of the past.",
    alchemist_level=0,
    discovery_chance=0.35,
    tags=["early_game", "emotional", "memory"],
)

COURAGE = RecipeData(
    name="Courage",
    ingredients={"Anger": 70.0, "Fear": 30.0},
    output="Determination",
    output_quantity=Decimal("1.0"),
    base_success_rate=0.85,
    min_purity_required=55.0,
    difficulty=RecipeDifficulty.BASIC,
    description="Righteous anger overcomes fear to forge unwavering determination.",
    alchemist_level=1,
    discovery_chance=0.30,
    tags=["early_game", "strength", "willpower"],
)

EXCITEMENT = RecipeData(
    name="Excitement",
    ingredients={"Joy": 50.0, "Fear": 50.0},
    output="Thrill",
    output_quantity=Decimal("1.5"),
    base_success_rate=0.88,
    min_purity_required=50.0,
    difficulty=RecipeDifficulty.BASIC,
    description="Joy mixed with just enough fear creates an exhilarating rush.",
    alchemist_level=0,
    discovery_chance=0.32,
    tags=["early_game", "energy", "adventure"],
)

MELANCHOLY = RecipeData(
    name="Melancholy",
    ingredients={"Sadness": 80.0, "Love": 20.0},
    output="Wistfulness",
    output_quantity=Decimal("1.5"),
    base_success_rate=0.92,
    min_purity_required=45.0,
    difficulty=RecipeDifficulty.BASIC,
    description="Deep sadness softened by love becomes a gentle, longing ache.",
    alchemist_level=0,
    discovery_chance=0.38,
    tags=["early_game", "contemplative", "gentle"],
)

BOUNDARIES = RecipeData(
    name="Boundaries",
    ingredients={"Disgust": 65.0, "Fear": 35.0},
    output="Caution",
    output_quantity=Decimal("1.0"),
    base_success_rate=0.87,
    min_purity_required=50.0,
    difficulty=RecipeDifficulty.BASIC,
    description="Disgust and fear combine to create healthy protective instincts.",
    alchemist_level=1,
    discovery_chance=0.28,
    tags=["early_game", "protection", "awareness"],
)

# =============================================================================
# MID GAME (3 Ingredients)
# =============================================================================

HOPE = RecipeData(
    name="Hope",
    ingredients={"Joy": 40.0, "Sadness": 30.0, "Determination": 30.0},
    output="Hope",
    output_quantity=Decimal("1.0"),
    base_success_rate=0.75,
    min_purity_required=60.0,
    difficulty=RecipeDifficulty.ADVANCED,
    description="Even in sadness, joy and determination kindle the flame of hope.",
    alchemist_level=3,
    special_equipment=["Glass Beakers"],
    discovery_chance=0.20,
    tags=["mid_game", "rare", "inspirational"],
)

COMPASSION_RECIPE = RecipeData(
    name="Compassion",
    ingredients={"Love": 40.0, "Sadness": 30.0, "Joy": 30.0},
    output="Empathy",
    output_quantity=Decimal("1.5"),
    base_success_rate=0.70,
    min_purity_required=65.0,
    difficulty=RecipeDifficulty.ADVANCED,
    description="Understanding another's pain through love and shared joy creates deep empathy.",
    alchemist_level=4,
    special_equipment=["Glass Beakers"],
    discovery_chance=0.18,
    tags=["mid_game", "connection", "altruistic"],
)

WISDOM_RECIPE = RecipeData(
    name="Wisdom",
    ingredients={"Joy": 33.33, "Sadness": 33.33, "Anger": 33.34},
    output="Understanding",
    output_quantity=Decimal("1.0"),
    base_success_rate=0.65,
    min_purity_required=70.0,
    difficulty=RecipeDifficulty.ADVANCED,
    description="Perfect balance of emotions reveals deep understanding of the human condition.",
    alchemist_level=5,
    special_equipment=["Centrifuge"],
    discovery_chance=0.15,
    tags=["mid_game", "philosophical", "balance"],
)

ZEN = RecipeData(
    name="Zen",
    ingredients={"Serenity": 50.0, "Joy": 25.0, "Sadness": 25.0},
    output="Perfect Calm",
    output_quantity=Decimal("1.0"),
    base_success_rate=0.60,
    min_purity_required=75.0,
    difficulty=RecipeDifficulty.ADVANCED,
    description="Serenity embraces both joy and sorrow, achieving perfect tranquility.",
    alchemist_level=6,
    special_equipment=["Distillery"],
    discovery_chance=0.12,
    tags=["mid_game", "meditative", "peaceful"],
)

PASSION = RecipeData(
    name="Passion",
    ingredients={"Love": 50.0, "Anger": 30.0, "Joy": 20.0},
    output="Intensity",
    output_quantity=Decimal("2.0"),
    base_success_rate=0.72,
    min_purity_required=60.0,
    difficulty=RecipeDifficulty.ADVANCED,
    description="Love and anger fuel an intense, burning passion for life.",
    alchemist_level=4,
    special_equipment=["Glass Beakers"],
    discovery_chance=0.22,
    tags=["mid_game", "energy", "powerful"],
)

# =============================================================================
# LATE GAME (4+ Ingredients)
# =============================================================================

TRANSCENDENCE_RECIPE = RecipeData(
    name="Transcendence",
    ingredients={
        "Joy": 20.0,
        "Sadness": 20.0,
        "Anger": 20.0,
        "Fear": 20.0,
        "Love": 20.0,
    },
    output="Transcendence",
    output_quantity=Decimal("1.0"),
    base_success_rate=0.50,
    min_purity_required=80.0,
    difficulty=RecipeDifficulty.MASTER,
    description="All primary emotions in perfect harmony create transcendent experience.",
    alchemist_level=10,
    special_equipment=["Crystallization Chamber", "Quantum Mixer"],
    discovery_chance=0.08,
    tags=["late_game", "legendary", "ascension"],
)

EMOTIONAL_SINGULARITY = RecipeData(
    name="Emotional Singularity",
    ingredients={
        "Joy": 10.0,
        "Sadness": 10.0,
        "Anger": 10.0,
        "Fear": 10.0,
        "Love": 10.0,
        "Disgust": 10.0,
        "Hope": 10.0,
        "Empathy": 10.0,
        "Understanding": 10.0,
        "Transcendence": 10.0,
    },
    output="Singularity",
    output_quantity=Decimal("1.0"),
    base_success_rate=0.25,
    min_purity_required=90.0,
    difficulty=RecipeDifficulty.LEGENDARY,
    description="The ultimate convergence - every emotion unified into pure consciousness.",
    alchemist_level=15,
    special_equipment=["Quantum Mixer", "Philosopher's Stone"],
    contamination_risk=0.3,
    discovery_chance=0.02,
    tags=["late_game", "legendary", "ultimate"],
)

THE_VOID = RecipeData(
    name="The Void",
    ingredients={
        "Joy": 25.0,
        "Sadness": 25.0,
        "Anger": 25.0,
        "Fear": 25.0,
    },
    output="Void",
    output_quantity=Decimal("0.5"),
    base_success_rate=0.40,
    min_purity_required=85.0,
    difficulty=RecipeDifficulty.MASTER,
    description="Opposing emotions cancel out, creating an absence - the terrifying void.",
    alchemist_level=12,
    special_equipment=["Crystallization Chamber"],
    contamination_risk=0.25,
    discovery_chance=0.05,
    tags=["late_game", "dangerous", "philosophical"],
)

# =============================================================================
# SECRET RECIPES
# =============================================================================

SCHADENFREUDE = RecipeData(
    name="Schadenfreude",
    ingredients={"Joy": 60.0, "Sadness": 40.0},
    output="Schadenfreude",
    output_quantity=Decimal("3.0"),
    base_success_rate=0.80,
    min_purity_required=70.0,
    difficulty=RecipeDifficulty.SECRET,
    description="Joy derived from another's misfortune - profitable but ethically questionable.",
    alchemist_level=7,
    special_equipment=["Distillery"],
    discovery_chance=0.03,
    tags=["secret", "forbidden", "ethical_cost"],
)

ENNUI = RecipeData(
    name="Ennui",
    ingredients={
        "Joy": 20.0,
        "Sadness": 20.0,
        "Anger": 20.0,
        "Fear": 20.0,
        "Disgust": 20.0,
    },
    output="Ennui",
    output_quantity=Decimal("1.0"),
    base_success_rate=0.95,  # Easy to achieve but requires time
    min_purity_required=50.0,
    difficulty=RecipeDifficulty.SECRET,
    description="Let all emotions stagnate together - sophisticated boredom emerges.",
    alchemist_level=8,
    discovery_chance=0.01,
    tags=["secret", "time_based", "intellectual"],
)

PURE_EXPERIENCE = RecipeData(
    name="Pure Experience",
    ingredients={
        "Transcendence": 40.0,
        "Understanding": 30.0,
        "Perfect Calm": 30.0,
    },
    output="Pure Experience",
    output_quantity=Decimal("1.0"),
    base_success_rate=0.55,
    min_purity_required=95.0,
    difficulty=RecipeDifficulty.LEGENDARY,
    description="The distilled essence of all feelings - existence in its purest form.",
    alchemist_level=20,
    special_equipment=["Philosopher's Stone", "Crystallization Chamber"],
    discovery_chance=0.01,
    side_products={"Euphoria": Decimal("0.5")},
    tags=["secret", "legendary", "mystical"],
)


# =============================================================================
# RECIPE REGISTRY
# =============================================================================

ALL_RECIPES = [
    # Early Game (2 ingredients)
    BITTERSWEET,
    COURAGE,
    EXCITEMENT,
    MELANCHOLY,
    BOUNDARIES,

    # Mid Game (3 ingredients)
    HOPE,
    COMPASSION_RECIPE,
    WISDOM_RECIPE,
    ZEN,
    PASSION,

    # Late Game (4+ ingredients)
    TRANSCENDENCE_RECIPE,
    EMOTIONAL_SINGULARITY,
    THE_VOID,

    # Secret Recipes
    SCHADENFREUDE,
    ENNUI,
    PURE_EXPERIENCE,
]

# Recipe lookup by name
RECIPE_BY_NAME = {recipe.name: recipe for recipe in ALL_RECIPES}

# Recipes by difficulty
RECIPES_BY_DIFFICULTY = {
    RecipeDifficulty.BASIC: [r for r in ALL_RECIPES if r.difficulty == RecipeDifficulty.BASIC],
    RecipeDifficulty.ADVANCED: [r for r in ALL_RECIPES if r.difficulty == RecipeDifficulty.ADVANCED],
    RecipeDifficulty.MASTER: [r for r in ALL_RECIPES if r.difficulty == RecipeDifficulty.MASTER],
    RecipeDifficulty.LEGENDARY: [r for r in ALL_RECIPES if r.difficulty == RecipeDifficulty.LEGENDARY],
    RecipeDifficulty.SECRET: [r for r in ALL_RECIPES if r.difficulty == RecipeDifficulty.SECRET],
}

# Recipes by required level
def get_recipes_for_level(level: int) -> List[RecipeData]:
    """Get all recipes available at a given alchemist level."""
    return [r for r in ALL_RECIPES if r.alchemist_level <= level]


# Recipes by ingredient (for discovery hints)
def get_recipes_with_ingredient(ingredient: str) -> List[RecipeData]:
    """Get all recipes that use a specific ingredient."""
    return [r for r in ALL_RECIPES if ingredient in r.ingredients]
