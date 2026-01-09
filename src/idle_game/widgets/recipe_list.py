"""Recipe list widget for displaying discovered recipes.

This widget shows all discovered recipes organized by difficulty tier,
with filtering and sorting options.
"""

from typing import List, Optional

from textual.app import ComposeResult
from textual.widgets import Static, ListView, ListItem, Label, Button
from textual.containers import Vertical, Horizontal, Container, ScrollableContainer
from textual.reactive import reactive
from textual.message import Message

from ..models.recipe import Recipe, RecipeBook, RecipeProgress
from ..data.recipes import RecipeDifficulty


class RecipeListItem(ListItem):
    """A single recipe item in the list."""

    def __init__(
        self,
        recipe: Recipe,
        progress: RecipeProgress,
        **kwargs
    ):
        """Initialize the recipe list item.

        Args:
            recipe: Recipe to display
            progress: Player's progress with this recipe
            **kwargs: Additional widget arguments
        """
        super().__init__(**kwargs)
        self.recipe = recipe
        self.progress = progress

    def compose(self) -> ComposeResult:
        """Create the list item layout."""
        with Horizontal(classes="recipe-item-container"):
            # Recipe name and difficulty
            with Vertical(classes="recipe-info"):
                yield Label(
                    f"{self.recipe.name}",
                    classes="recipe-name"
                )
                yield Label(
                    f"[dim]{self.recipe.difficulty.value.title()}[/dim]",
                    classes="recipe-difficulty"
                )

            # Stats
            with Vertical(classes="recipe-stats"):
                yield Label(
                    f"Success: {self.recipe.base_success_rate*100:.0f}%",
                    classes="recipe-stat"
                )
                yield Label(
                    f"Crafted: {self.progress.times_crafted}x",
                    classes="recipe-stat"
                )

            # Best purity achieved
            if self.progress.best_purity_achieved > 0:
                purity_stars = self._purity_to_stars(self.progress.best_purity_achieved)
                yield Label(
                    f"Best: {purity_stars}",
                    classes="recipe-purity"
                )

    def _purity_to_stars(self, purity: float) -> str:
        """Convert purity percentage to diamond display.

        Args:
            purity: Purity percentage (0-100)

        Returns:
            String with diamond symbols
        """
        if purity >= 100:
            return "◊◊◊◊◊"
        elif purity >= 80:
            return "◊◊◊◊"
        elif purity >= 60:
            return "◊◊◊"
        elif purity >= 40:
            return "◊◊"
        else:
            return "◊"


class DifficultyFilter(Static):
    """Widget for filtering recipes by difficulty."""

    selected_difficulty: reactive[Optional[str]] = reactive(None)

    def compose(self) -> ComposeResult:
        """Create the filter buttons."""
        with Horizontal(classes="filter-row"):
            yield Label("Filter:", classes="filter-label")
            yield Button("All", id="filter-all", variant="primary", classes="filter-btn")
            yield Button("Basic", id="filter-basic", variant="default", classes="filter-btn")
            yield Button("Advanced", id="filter-advanced", variant="default", classes="filter-btn")
            yield Button("Master", id="filter-master", variant="default", classes="filter-btn")
            yield Button("Legendary", id="filter-legendary", variant="default", classes="filter-btn")
            yield Button("Secret", id="filter-secret", variant="default", classes="filter-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle filter button presses.

        Args:
            event: Button press event
        """
        button_id = event.button.id

        if button_id == "filter-all":
            self.selected_difficulty = None
        elif button_id.startswith("filter-"):
            difficulty = button_id.replace("filter-", "")
            self.selected_difficulty = difficulty

        # Update button styles
        for button in self.query(Button):
            if button.id == button_id:
                button.variant = "primary"
            else:
                button.variant = "default"

        # Notify parent
        self.post_message(self.DifficultySelected(self.selected_difficulty))

    class DifficultySelected(Message):
        """Message posted when difficulty filter changes."""

        def __init__(self, difficulty: Optional[str]):
            """Initialize the message.

            Args:
                difficulty: Selected difficulty or None for all
            """
            super().__init__()
            self.difficulty = difficulty


class RecipeList(Static):
    """Widget displaying discovered recipes with filtering."""

    selected_recipe: reactive[Optional[Recipe]] = reactive(None)
    filter_difficulty: reactive[Optional[str]] = reactive(None)

    def __init__(
        self,
        recipe_book: RecipeBook,
        **kwargs
    ):
        """Initialize the recipe list.

        Args:
            recipe_book: The player's recipe book
            **kwargs: Additional widget arguments
        """
        super().__init__(**kwargs)
        self.recipe_book = recipe_book

    def compose(self) -> ComposeResult:
        """Create the recipe list layout."""
        with Vertical(classes="recipe-list-container"):
            # Discovery counter
            counts = self.recipe_book.get_discovery_count()
            discovered, total = counts["total"]
            yield Static(
                f"Discovered: {discovered}/{total}",
                id="discovery-counter",
                classes="discovery-counter"
            )

            # Difficulty breakdown
            with Vertical(id="difficulty-breakdown", classes="difficulty-breakdown"):
                for difficulty in ["basic", "advanced", "master", "legendary", "secret"]:
                    disc, tot = counts.get(difficulty, (0, 0))
                    if tot > 0:
                        progress_bar = self._render_progress_bar(disc, tot)
                        yield Static(
                            f"[{difficulty.upper():9}] {progress_bar} {disc:2}/{tot:2}",
                            classes="difficulty-stat"
                        )

            # Filter buttons
            yield DifficultyFilter(id="difficulty-filter")

            # Recipe list
            with ScrollableContainer(id="recipe-scroll-container"):
                yield ListView(
                    id="recipe-listview",
                    classes="recipe-listview"
                )

            # Help text
            yield Static(
                "↑↓: Navigate • Enter: Select • Tab: Filter",
                classes="help-text"
            )

    def _render_progress_bar(self, current: int, total: int) -> str:
        """Render a progress bar.

        Args:
            current: Current value
            total: Total value

        Returns:
            String representation of progress bar
        """
        if total == 0:
            return "[░░░░░░░░░░]"

        filled = int((current / total) * 10)
        empty = 10 - filled
        return f"[{'█' * filled}{'░' * empty}]"

    def on_mount(self) -> None:
        """Handle mount event."""
        self._populate_list()

    def _populate_list(self) -> None:
        """Populate the recipe list with discovered recipes."""
        listview = self.query_one("#recipe-listview", ListView)
        listview.clear()

        # Get discovered recipes
        recipes = self.recipe_book.get_discovered_recipes()

        # Apply difficulty filter
        if self.filter_difficulty:
            recipes = [
                r for r in recipes
                if r.difficulty.value == self.filter_difficulty
            ]

        # Sort by difficulty, then name
        difficulty_order = {
            RecipeDifficulty.BASIC: 0,
            RecipeDifficulty.ADVANCED: 1,
            RecipeDifficulty.MASTER: 2,
            RecipeDifficulty.LEGENDARY: 3,
            RecipeDifficulty.SECRET: 4,
        }
        recipes.sort(key=lambda r: (difficulty_order.get(r.difficulty, 99), r.name))

        # Add to list
        for recipe in recipes:
            progress = self.recipe_book.get_recipe_progress(recipe.name)
            if progress and progress.discovered:
                item = RecipeListItem(recipe, progress)
                listview.append(item)

        # If no recipes, show message
        if not recipes:
            if self.filter_difficulty:
                listview.append(
                    ListItem(
                        Label(f"No {self.filter_difficulty} recipes discovered yet")
                    )
                )
            else:
                listview.append(
                    ListItem(
                        Label("No recipes discovered yet. Try experimenting!")
                    )
                )

    def on_difficulty_filter_difficulty_selected(
        self,
        message: DifficultyFilter.DifficultySelected
    ) -> None:
        """Handle difficulty filter changes.

        Args:
            message: Filter selection message
        """
        self.filter_difficulty = message.difficulty
        self._populate_list()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle recipe selection.

        Args:
            event: List selection event
        """
        if isinstance(event.item, RecipeListItem):
            self.selected_recipe = event.item.recipe
            self.post_message(self.RecipeSelected(event.item.recipe))

    def refresh_list(self) -> None:
        """Refresh the recipe list (call after new discoveries)."""
        # Update counter
        counts = self.recipe_book.get_discovery_count()
        discovered, total = counts["total"]
        counter = self.query_one("#discovery-counter", Static)
        counter.update(f"Discovered: {discovered}/{total}")

        # Update difficulty breakdown
        breakdown = self.query_one("#difficulty-breakdown", Vertical)
        breakdown.remove_children()

        for difficulty in ["basic", "advanced", "master", "legendary", "secret"]:
            disc, tot = counts.get(difficulty, (0, 0))
            if tot > 0:
                progress_bar = self._render_progress_bar(disc, tot)
                breakdown.mount(Static(
                    f"[{difficulty.upper():9}] {progress_bar} {disc:2}/{tot:2}",
                    classes="difficulty-stat"
                ))

        # Refresh the list
        self._populate_list()

    def get_selected_recipe(self) -> Optional[Recipe]:
        """Get the currently selected recipe.

        Returns:
            Selected recipe or None
        """
        return self.selected_recipe

    class RecipeSelected(Message):
        """Message posted when a recipe is selected."""

        def __init__(self, recipe: Recipe):
            """Initialize the message.

            Args:
                recipe: The selected recipe
            """
            super().__init__()
            self.recipe = recipe


class RecipeTooltip(Static):
    """Tooltip showing detailed recipe information."""

    def __init__(self, recipe: Recipe, **kwargs):
        """Initialize the tooltip.

        Args:
            recipe: Recipe to display
            **kwargs: Additional widget arguments
        """
        super().__init__(**kwargs)
        self.recipe = recipe

    def compose(self) -> ComposeResult:
        """Create the tooltip layout."""
        with Vertical(classes="recipe-tooltip"):
            yield Label(f"📜 {self.recipe.name}", classes="tooltip-title")
            yield Label(self.recipe.description, classes="tooltip-description")

            yield Label("\nIngredients:", classes="tooltip-section")
            for ingredient, percentage in self.recipe.ingredients.items():
                yield Label(f"  • {percentage}% {ingredient}", classes="tooltip-ingredient")

            yield Label("\nOutput:", classes="tooltip-section")
            yield Label(
                f"  • {self.recipe.output_quantity} {self.recipe.output}",
                classes="tooltip-output"
            )

            if self.recipe.data.side_products:
                yield Label("\nBonus Products:", classes="tooltip-section")
                for product, qty in self.recipe.data.side_products.items():
                    yield Label(f"  • {qty} {product}", classes="tooltip-bonus")

            yield Label("\nRequirements:", classes="tooltip-section")
            yield Label(
                f"  • Success Rate: {self.recipe.base_success_rate*100:.0f}%",
                classes="tooltip-stat"
            )
            yield Label(
                f"  • Min Purity: {self.recipe.min_purity_required:.0f}%",
                classes="tooltip-stat"
            )
            if self.recipe.data.alchemist_level > 0:
                yield Label(
                    f"  • Alchemist Level: {self.recipe.data.alchemist_level}",
                    classes="tooltip-stat"
                )
            if self.recipe.data.special_equipment:
                yield Label(
                    f"  • Equipment: {', '.join(self.recipe.data.special_equipment)}",
                    classes="tooltip-stat"
                )
