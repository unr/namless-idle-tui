"""Alchemy screen for recipe mixing and experimentation.

This screen provides two modes:
1. Known Recipes: Select and craft discovered recipes
2. Experimentation: Mix custom combinations to discover new recipes
"""

from decimal import Decimal
from typing import Optional

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Button, TabbedContent, TabPane
from textual.containers import Horizontal, Vertical, Container
from textual.reactive import reactive

from ..models.recipe import Recipe, RecipeBook, CraftingResult
from ..widgets.recipe_list import RecipeList
from ..widgets.alchemy_mixer import AlchemyMixer


class AlchemyScreen(Screen):
    """Main alchemy interface with recipe browsing and mixing."""

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("r", "switch_tab('known')", "Known Recipes"),
        ("e", "switch_tab('experiment')", "Experiment"),
    ]

    # Reactive state
    selected_recipe: reactive[Optional[Recipe]] = reactive(None)
    alchemist_level: reactive[int] = reactive(0)
    equipment_bonus: reactive[float] = reactive(0.0)
    equipment_purity_bonus: reactive[float] = reactive(0.0)

    def __init__(
        self,
        recipe_book: RecipeBook,
        available_resources: dict,
        available_equipment: list,
        name: Optional[str] = None,
        id: Optional[str] = None,
    ):
        """Initialize the alchemy screen.

        Args:
            recipe_book: The player's recipe book
            available_resources: Dict of available emotions
            available_equipment: List of owned equipment
            name: Optional screen name
            id: Optional screen ID
        """
        super().__init__(name=name, id=id)
        self.recipe_book = recipe_book
        self.available_resources = available_resources
        self.available_equipment = available_equipment

    def compose(self) -> ComposeResult:
        """Create the alchemy screen layout."""
        yield Header()

        with TabbedContent(initial="known"):
            # Known Recipes Tab
            with TabPane("Known Recipes", id="known"):
                with Horizontal():
                    # Left: Recipe list
                    with Vertical(id="recipe-list-panel"):
                        yield Static("📖 Recipe Book", classes="panel-title")
                        yield RecipeList(
                            recipe_book=self.recipe_book,
                            id="recipe-list"
                        )

                    # Right: Recipe details and crafting
                    with Vertical(id="recipe-details-panel"):
                        yield Static("⚗️ Alchemy Laboratory", classes="panel-title")
                        yield RecipeDetailsWidget(id="recipe-details")
                        yield CraftingControlsWidget(id="crafting-controls")
                        yield ResultsDisplay(id="results-display")

            # Experimentation Tab
            with TabPane("Experimentation", id="experiment"):
                with Horizontal():
                    # Left: Ingredient mixer
                    with Vertical(id="mixer-panel"):
                        yield Static("🧪 Custom Mix", classes="panel-title")
                        yield AlchemyMixer(id="alchemy-mixer")

                    # Right: Predicted outcomes and experiment button
                    with Vertical(id="experiment-panel"):
                        yield Static("🔮 Predictions", classes="panel-title")
                        yield PredictionDisplay(id="prediction-display")
                        yield ExperimentControls(id="experiment-controls")
                        yield ResultsDisplay(id="experiment-results")

        yield Footer()

    def on_mount(self) -> None:
        """Handle screen mount."""
        # Set up initial state
        recipe_list = self.query_one("#recipe-list", RecipeList)
        recipe_list.focus()

    def on_recipe_list_recipe_selected(self, message) -> None:
        """Handle recipe selection from the list.

        Args:
            message: Recipe selection message with recipe attribute
        """
        self.selected_recipe = message.recipe
        self._update_recipe_details()

    def _update_recipe_details(self) -> None:
        """Update the recipe details display."""
        if not self.selected_recipe:
            return

        details_widget = self.query_one("#recipe-details", RecipeDetailsWidget)
        details_widget.update_recipe(
            recipe=self.selected_recipe,
            alchemist_level=self.alchemist_level,
            equipment_bonus=self.equipment_bonus,
            available_resources=self.available_resources,
            available_equipment=self.available_equipment,
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: Button press event
        """
        button_id = event.button.id

        if button_id == "craft-button":
            self._attempt_craft()
        elif button_id == "craft-10x-button":
            self._attempt_craft(quantity=10)
        elif button_id == "experiment-button":
            self._attempt_experiment()

    def _attempt_craft(self, quantity: int = 1) -> None:
        """Attempt to craft the selected recipe.

        Args:
            quantity: Number of times to craft
        """
        if not self.selected_recipe:
            self._show_message("No recipe selected!")
            return

        # Check if can attempt
        can_attempt, reason = self.selected_recipe.can_attempt(
            alchemist_level=self.alchemist_level,
            available_resources=self.available_resources,
            available_equipment=self.available_equipment,
        )

        if not can_attempt:
            self._show_message(f"Cannot craft: {reason}")
            return

        # Get input purities (simplified - would get from resources)
        input_purities = {
            ingredient: 75.0  # Placeholder - would get from actual resources
            for ingredient in self.selected_recipe.ingredients
        }

        # Attempt crafting
        result = self.selected_recipe.attempt_craft(
            alchemist_level=self.alchemist_level,
            input_purities=input_purities,
            equipment_bonus=self.equipment_bonus,
            equipment_purity_bonus=self.equipment_purity_bonus,
            quantity_multiplier=quantity,
        )

        # Record the attempt
        self.recipe_book.record_craft(self.selected_recipe.name, result)

        # Update resources (would integrate with game state)
        self._consume_ingredients(result.ingredients_consumed)

        if result.success:
            self._add_output(result.output, result.output_quantity, result.output_purity)

        # Display result
        self._show_result(result)

    def _attempt_experiment(self) -> None:
        """Attempt experimental mixing."""
        mixer = self.query_one("#alchemy-mixer", AlchemyMixer)
        ingredients = mixer.get_ingredients()

        # Check if total is 100%
        total = sum(ingredients.values())
        if abs(total - 100.0) > 0.01:
            self._show_message(f"Total must equal 100% (currently {total:.1f}%)")
            return

        # Attempt discovery
        discovered = self.recipe_book.attempt_discovery(ingredients)

        if discovered:
            self._show_message(f"🎉 Discovered new recipe: {discovered}!")
            # Switch to known recipes tab and select the new recipe
            tabs = self.query_one(TabbedContent)
            tabs.active = "known"
        else:
            # Still consume some ingredients and give small XP
            self._show_message("No recipe discovered. Keep experimenting!")

    def _consume_ingredients(self, ingredients: dict) -> None:
        """Consume ingredients from available resources.

        Args:
            ingredients: Dict of ingredient to amount consumed
        """
        # Placeholder - would integrate with actual game state
        for ingredient, amount in ingredients.items():
            if ingredient in self.available_resources:
                self.available_resources[ingredient] -= amount

    def _add_output(self, emotion: str, quantity: Decimal, purity: float) -> None:
        """Add crafted output to resources.

        Args:
            emotion: Type of emotion produced
            quantity: Amount produced
            purity: Purity of output
        """
        # Placeholder - would integrate with actual game state
        if emotion not in self.available_resources:
            self.available_resources[emotion] = Decimal("0")
        self.available_resources[emotion] += quantity

    def _show_message(self, message: str) -> None:
        """Display a message to the player.

        Args:
            message: Message to display
        """
        results = self.query_one("#results-display", ResultsDisplay)
        results.show_message(message)

    def _show_result(self, result: CraftingResult) -> None:
        """Display crafting result.

        Args:
            result: The crafting result to display
        """
        results = self.query_one("#results-display", ResultsDisplay)
        results.show_result(result)


class RecipeDetailsWidget(Static):
    """Widget to display detailed recipe information."""

    def __init__(self, **kwargs):
        """Initialize the widget."""
        super().__init__(**kwargs)
        self.recipe: Optional[Recipe] = None
        self.success_rate: float = 0.0

    def update_recipe(
        self,
        recipe: Recipe,
        alchemist_level: int,
        equipment_bonus: float,
        available_resources: dict,
        available_equipment: list,
    ) -> None:
        """Update displayed recipe.

        Args:
            recipe: Recipe to display
            alchemist_level: Player's alchemist level
            equipment_bonus: Equipment success bonus
            available_resources: Available resources
            available_equipment: Available equipment
        """
        self.recipe = recipe

        # Calculate success rate
        # Get purities (simplified)
        input_purities = {ing: 75.0 for ing in recipe.ingredients}
        self.success_rate = recipe.calculate_success_rate(
            alchemist_level, equipment_bonus, input_purities
        )

        # Check if can attempt
        can_attempt, reason = recipe.can_attempt(
            alchemist_level, available_resources, available_equipment
        )

        # Build display
        lines = [
            f"Recipe: {recipe.name}",
            f"Difficulty: {recipe.difficulty.value.title()}",
            "",
            "Required Ingredients:",
        ]

        for ingredient, percentage in recipe.ingredients.items():
            have = available_resources.get(ingredient, Decimal("0"))
            lines.append(f"  {percentage:5.1f}% {ingredient:15} (Have: {have})")

        lines.extend([
            "",
            f"Output: {recipe.output_quantity} {recipe.output}",
            f"Success Rate: {self.success_rate*100:.1f}%",
            f"Min Purity Required: {recipe.min_purity_required:.0f}%",
        ])

        if not can_attempt:
            lines.append("")
            lines.append(f"⚠️  {reason}")

        lines.append("")
        lines.append(f"Description: {recipe.description}")

        self.update("\n".join(lines))


class CraftingControlsWidget(Static):
    """Widget with crafting control buttons."""

    def compose(self) -> ComposeResult:
        """Create crafting buttons."""
        with Horizontal(classes="button-row"):
            yield Button("Craft", id="craft-button", variant="primary")
            yield Button("Craft 10x", id="craft-10x-button", variant="default")


class PredictionDisplay(Static):
    """Display predicted outcomes for experimental mixing."""

    def update_predictions(self, ingredients: dict) -> None:
        """Update prediction display based on ingredients.

        Args:
            ingredients: Dict of emotion to percentage
        """
        # Simplified prediction logic
        lines = [
            "Possible Outcomes:",
            "",
            "  65% - Unknown Result",
            "  20% - Contaminated Mix",
            "  10% - Recipe Discovery",
            "  5%  - Catastrophic Failure",
        ]

        self.update("\n".join(lines))


class ExperimentControls(Static):
    """Controls for experimental mixing."""

    def compose(self) -> ComposeResult:
        """Create experiment controls."""
        with Horizontal(classes="button-row"):
            yield Button("Experiment!", id="experiment-button", variant="warning")
            yield Button("Reset", id="reset-mixer-button", variant="default")


class ResultsDisplay(Static):
    """Display crafting/experiment results."""

    def __init__(self, **kwargs):
        """Initialize the widget."""
        super().__init__(**kwargs)
        self.update("Ready to craft...")

    def show_message(self, message: str) -> None:
        """Show a simple message.

        Args:
            message: Message to display
        """
        self.update(message)

    def show_result(self, result: CraftingResult) -> None:
        """Show crafting result.

        Args:
            result: Crafting result to display
        """
        lines = [
            "═" * 40,
            result.message,
            "",
        ]

        if result.success:
            lines.extend([
                f"✓ Produced: {result.output_quantity} {result.output}",
                f"✓ Purity: {result.output_purity:.1f}%",
                f"✓ XP Gained: +{result.xp_gained}",
            ])

            if result.side_products:
                lines.append("✓ Bonus:")
                for product, qty in result.side_products.items():
                    lines.append(f"    {qty} {product}")
        else:
            lines.append(f"✗ Failure Type: {result.failure_type.value.title()}")
            if result.xp_gained > 0:
                lines.append(f"✓ XP Gained: +{result.xp_gained}")

        lines.extend([
            "",
            "Ingredients Consumed:",
        ])
        for ingredient, amount in result.ingredients_consumed.items():
            lines.append(f"  - {amount} {ingredient}")

        lines.append("═" * 40)

        self.update("\n".join(lines))
