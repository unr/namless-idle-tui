"""Recipe system for emotion alchemy.

This module contains the Recipe and RecipeBook classes that handle
recipe crafting, success calculation, and discovery mechanics.
"""

from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import random
from enum import Enum

from ..data.recipes import RecipeData, ALL_RECIPES, RECIPE_BY_NAME


class FailureType(Enum):
    """Types of crafting failures."""
    MINOR = "minor"  # 50% of failures - lose 50% ingredients, get sludge
    MAJOR = "major"  # 35% of failures - lose all ingredients, equipment needs cleaning
    CATASTROPHIC = "catastrophic"  # 10% of failures - explosion, damage storage
    INTERESTING = "interesting"  # 5% of failures - discover something new!


@dataclass
class CraftingResult:
    """Result of a recipe crafting attempt."""
    success: bool
    output: Optional[str] = None
    output_quantity: Decimal = Decimal("0")
    output_purity: float = 0.0
    side_products: Dict[str, Decimal] = field(default_factory=dict)
    failure_type: Optional[FailureType] = None
    message: str = ""
    ingredients_consumed: Dict[str, Decimal] = field(default_factory=dict)
    xp_gained: int = 0
    new_recipe_discovered: Optional[str] = None


@dataclass
class RecipeProgress:
    """Tracks player's progress with a specific recipe."""
    recipe_name: str
    discovered: bool = False
    times_crafted: int = 0
    times_failed: int = 0
    best_purity_achieved: float = 0.0
    first_discovered_at: Optional[datetime] = None
    last_crafted_at: Optional[datetime] = None


class Recipe:
    """Runtime recipe instance with crafting logic."""

    def __init__(self, recipe_data: RecipeData):
        """Initialize a recipe from recipe data.

        Args:
            recipe_data: The recipe definition
        """
        self.data = recipe_data
        self.name = recipe_data.name
        self.ingredients = recipe_data.ingredients
        self.output = recipe_data.output
        self.output_quantity = recipe_data.output_quantity
        self.base_success_rate = recipe_data.base_success_rate
        self.min_purity_required = recipe_data.min_purity_required
        self.difficulty = recipe_data.difficulty
        self.description = recipe_data.description

    def calculate_success_rate(
        self,
        alchemist_level: int,
        equipment_bonus: float = 0.0,
        input_purities: Optional[Dict[str, float]] = None,
    ) -> float:
        """Calculate final success rate for this recipe.

        Formula from docs:
        Base Success Rate (from recipe)
        + Alchemist Level Bonus (+2% per level)
        + Equipment Bonus (+5-15%)
        + Purity Bonus (+1% per 5% above minimum)
        - Contamination (-5% if any input <50% pure)
        - Complexity Penalty (-5% per ingredient over 3)
        = Final Success Rate (capped at 95%)

        Args:
            alchemist_level: Player's current alchemist level
            equipment_bonus: Bonus from equipment (0.0 to 0.25)
            input_purities: Dict of ingredient name to purity percentage

        Returns:
            Final success rate (0.0 to 0.95)
        """
        if input_purities is None:
            input_purities = {}

        success_rate = self.base_success_rate

        # Alchemist level bonus: +2% per level
        success_rate += (alchemist_level * 0.02)

        # Equipment bonus
        success_rate += equipment_bonus

        # Purity bonus: +1% per 5% above minimum
        avg_purity = sum(input_purities.values()) / len(input_purities) if input_purities else 0
        if avg_purity > self.min_purity_required:
            purity_bonus = (avg_purity - self.min_purity_required) / 5.0 * 0.01
            success_rate += purity_bonus

        # Contamination penalty: -5% if any input <50% pure
        if any(p < 50.0 for p in input_purities.values()):
            success_rate -= 0.05

        # Complexity penalty: -5% per ingredient over 3
        num_ingredients = len(self.ingredients)
        if num_ingredients > 3:
            complexity_penalty = (num_ingredients - 3) * 0.05
            success_rate -= complexity_penalty

        # Cap at 95%
        return min(0.95, max(0.0, success_rate))

    def calculate_output_purity(
        self,
        input_purities: Dict[str, float],
        equipment_purity_bonus: float = 0.0,
    ) -> float:
        """Calculate output purity based on input purities.

        Output purity is a weighted average of input purities,
        weighted by the percentage of each ingredient used.

        Args:
            input_purities: Dict of ingredient name to purity percentage
            equipment_purity_bonus: Bonus from equipment (0.0 to 0.30)

        Returns:
            Output purity percentage (0.0 to 100.0)
        """
        if not input_purities:
            return 0.0

        # Weighted average based on ingredient percentages
        weighted_purity = 0.0
        for ingredient, percentage in self.ingredients.items():
            ingredient_purity = input_purities.get(ingredient, 0.0)
            weight = percentage / 100.0
            weighted_purity += ingredient_purity * weight

        # Apply equipment bonus
        weighted_purity += (equipment_purity_bonus * 100.0)

        # Cap at 100%
        return min(100.0, max(0.0, weighted_purity))

    def can_attempt(
        self,
        alchemist_level: int,
        available_resources: Dict[str, Decimal],
        available_equipment: List[str],
    ) -> Tuple[bool, str]:
        """Check if the player can attempt this recipe.

        Args:
            alchemist_level: Player's current alchemist level
            available_resources: Dict of available emotions and quantities
            available_equipment: List of owned equipment

        Returns:
            Tuple of (can_attempt, reason_if_not)
        """
        # Check alchemist level
        if alchemist_level < self.data.alchemist_level:
            return False, f"Requires Alchemist Level {self.data.alchemist_level}"

        # Check equipment
        for equipment in self.data.special_equipment:
            if equipment not in available_equipment:
                return False, f"Requires {equipment}"

        # Check ingredients (we need at least enough for one craft)
        # Calculate minimum needed based on some base amount (e.g., 10 units)
        base_amount = Decimal("10")
        for ingredient, percentage in self.ingredients.items():
            needed = base_amount * Decimal(str(percentage / 100.0))
            available = available_resources.get(ingredient, Decimal("0"))
            if available < needed:
                return False, f"Insufficient {ingredient} (need {needed}, have {available})"

        return True, ""

    def attempt_craft(
        self,
        alchemist_level: int,
        input_purities: Dict[str, float],
        equipment_bonus: float = 0.0,
        equipment_purity_bonus: float = 0.0,
        quantity_multiplier: int = 1,
    ) -> CraftingResult:
        """Attempt to craft this recipe.

        Args:
            alchemist_level: Player's current alchemist level
            input_purities: Purity of each input ingredient
            equipment_bonus: Success rate bonus from equipment
            equipment_purity_bonus: Purity bonus from equipment
            quantity_multiplier: Craft multiple at once (affects difficulty)

        Returns:
            CraftingResult with outcome details
        """
        # Calculate success rate
        success_rate = self.calculate_success_rate(
            alchemist_level, equipment_bonus, input_purities
        )

        # Penalty for batch crafting
        if quantity_multiplier > 1:
            success_rate *= (0.95 ** (quantity_multiplier - 1))

        # Roll for success
        roll = random.random()
        success = roll < success_rate

        # Calculate ingredients consumed (base 10 units per craft)
        base_amount = Decimal("10") * quantity_multiplier
        ingredients_consumed = {
            ingredient: base_amount * Decimal(str(percentage / 100.0))
            for ingredient, percentage in self.ingredients.items()
        }

        if success:
            # Calculate output purity
            output_purity = self.calculate_output_purity(
                input_purities, equipment_purity_bonus
            )

            # Calculate XP (more for first time, perfect purity, etc.)
            xp = 10 * quantity_multiplier
            if output_purity >= 100.0:
                xp += 50  # Perfect purity bonus

            result = CraftingResult(
                success=True,
                output=self.output,
                output_quantity=self.output_quantity * quantity_multiplier,
                output_purity=output_purity,
                side_products=self.data.side_products.copy(),
                message=f"Successfully crafted {self.name}!",
                ingredients_consumed=ingredients_consumed,
                xp_gained=xp,
            )
        else:
            # Determine failure type
            failure_roll = random.random()
            if failure_roll < 0.50:
                failure_type = FailureType.MINOR
                # Recover 50% of ingredients
                ingredients_consumed = {
                    k: v * Decimal("0.5") for k, v in ingredients_consumed.items()
                }
                message = "Minor failure - some ingredients recovered as contaminated sludge."
                xp = 2
            elif failure_roll < 0.85:
                failure_type = FailureType.MAJOR
                message = "Major failure - all ingredients lost. Equipment needs cleaning."
                xp = 1
            elif failure_roll < 0.95:
                failure_type = FailureType.CATASTROPHIC
                message = "CATASTROPHIC FAILURE! Explosion damages nearby storage!"
                xp = 0
            else:
                failure_type = FailureType.INTERESTING
                message = "Interesting failure - you discovered something unexpected!"
                xp = 25  # Bonus XP for discovery

            result = CraftingResult(
                success=False,
                failure_type=failure_type,
                message=message,
                ingredients_consumed=ingredients_consumed,
                xp_gained=xp,
            )

        return result


class RecipeBook:
    """Manages discovered recipes and crafting history."""

    def __init__(self):
        """Initialize an empty recipe book."""
        self.recipes: Dict[str, Recipe] = {}
        self.progress: Dict[str, RecipeProgress] = {}

        # Initialize all recipes (but mark as undiscovered)
        for recipe_data in ALL_RECIPES:
            recipe = Recipe(recipe_data)
            self.recipes[recipe.name] = recipe
            self.progress[recipe.name] = RecipeProgress(
                recipe_name=recipe.name,
                discovered=False,
            )

    def discover_recipe(self, recipe_name: str) -> bool:
        """Discover a recipe by name.

        Args:
            recipe_name: Name of the recipe to discover

        Returns:
            True if newly discovered, False if already known
        """
        if recipe_name not in self.progress:
            return False

        progress = self.progress[recipe_name]
        if not progress.discovered:
            progress.discovered = True
            progress.first_discovered_at = datetime.now()
            return True
        return False

    def record_craft(
        self,
        recipe_name: str,
        result: CraftingResult,
    ) -> None:
        """Record a crafting attempt.

        Args:
            recipe_name: Name of the recipe crafted
            result: The crafting result
        """
        if recipe_name not in self.progress:
            return

        progress = self.progress[recipe_name]
        progress.last_crafted_at = datetime.now()

        if result.success:
            progress.times_crafted += 1
            if result.output_purity > progress.best_purity_achieved:
                progress.best_purity_achieved = result.output_purity
        else:
            progress.times_failed += 1

    def get_discovered_recipes(self) -> List[Recipe]:
        """Get all discovered recipes.

        Returns:
            List of discovered recipes
        """
        return [
            self.recipes[name]
            for name, progress in self.progress.items()
            if progress.discovered
        ]

    def get_recipes_by_difficulty(self, difficulty: str) -> List[Recipe]:
        """Get all discovered recipes of a given difficulty.

        Args:
            difficulty: Difficulty tier to filter by

        Returns:
            List of discovered recipes at that difficulty
        """
        return [
            recipe
            for recipe in self.get_discovered_recipes()
            if recipe.difficulty.value == difficulty
        ]

    def get_discovery_count(self) -> Dict[str, int]:
        """Get counts of discovered vs total recipes by difficulty.

        Returns:
            Dict mapping difficulty to (discovered, total) counts
        """
        from ..data.recipes import RecipeDifficulty, RECIPES_BY_DIFFICULTY

        counts = {}
        for difficulty in RecipeDifficulty:
            total = len(RECIPES_BY_DIFFICULTY.get(difficulty, []))
            discovered = len([
                r for r in self.get_discovered_recipes()
                if r.difficulty == difficulty
            ])
            counts[difficulty.value] = (discovered, total)

        # Overall count
        total_discovered = len(self.get_discovered_recipes())
        total_recipes = len(ALL_RECIPES)
        counts["total"] = (total_discovered, total_recipes)

        return counts

    def get_recipe_progress(self, recipe_name: str) -> Optional[RecipeProgress]:
        """Get progress for a specific recipe.

        Args:
            recipe_name: Name of the recipe

        Returns:
            RecipeProgress or None if not found
        """
        return self.progress.get(recipe_name)

    def attempt_discovery(
        self,
        ingredients: Dict[str, float],
        tolerance: float = 5.0,
    ) -> Optional[str]:
        """Attempt to discover a recipe through experimentation.

        Checks if the provided ingredients match any undiscovered recipe
        within the given tolerance.

        Args:
            ingredients: Dict of emotion type to percentage
            tolerance: How close ingredients must match (default 5%)

        Returns:
            Recipe name if discovered, None otherwise
        """
        # Normalize ingredients to sum to 100
        total = sum(ingredients.values())
        if total > 0:
            normalized = {k: v / total * 100.0 for k, v in ingredients.items()}
        else:
            return None

        # Check each undiscovered recipe
        for name, progress in self.progress.items():
            if progress.discovered:
                continue

            recipe = self.recipes[name]

            # Check if all ingredients match within tolerance
            matches = True
            for ingredient, percentage in recipe.ingredients.items():
                provided = normalized.get(ingredient, 0.0)
                if abs(provided - percentage) > tolerance:
                    matches = False
                    break

            # Check no extra ingredients
            for ingredient in normalized:
                if ingredient not in recipe.ingredients:
                    provided = normalized[ingredient]
                    if provided > tolerance:
                        matches = False
                        break

            if matches:
                # Discovery chance check
                if random.random() < recipe.data.discovery_chance:
                    self.discover_recipe(name)
                    return name

        return None

    def to_dict(self) -> dict:
        """Serialize recipe book to dictionary for saving.

        Returns:
            Dictionary of recipe progress
        """
        return {
            name: {
                "discovered": progress.discovered,
                "times_crafted": progress.times_crafted,
                "times_failed": progress.times_failed,
                "best_purity_achieved": progress.best_purity_achieved,
                "first_discovered_at": (
                    progress.first_discovered_at.isoformat()
                    if progress.first_discovered_at
                    else None
                ),
                "last_crafted_at": (
                    progress.last_crafted_at.isoformat()
                    if progress.last_crafted_at
                    else None
                ),
            }
            for name, progress in self.progress.items()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RecipeBook":
        """Deserialize recipe book from dictionary.

        Args:
            data: Dictionary of recipe progress

        Returns:
            Reconstructed RecipeBook
        """
        book = cls()

        for name, progress_data in data.items():
            if name in book.progress:
                progress = book.progress[name]
                progress.discovered = progress_data.get("discovered", False)
                progress.times_crafted = progress_data.get("times_crafted", 0)
                progress.times_failed = progress_data.get("times_failed", 0)
                progress.best_purity_achieved = progress_data.get("best_purity_achieved", 0.0)

                first_discovered = progress_data.get("first_discovered_at")
                if first_discovered:
                    progress.first_discovered_at = datetime.fromisoformat(first_discovered)

                last_crafted = progress_data.get("last_crafted_at")
                if last_crafted:
                    progress.last_crafted_at = datetime.fromisoformat(last_crafted)

        return book
