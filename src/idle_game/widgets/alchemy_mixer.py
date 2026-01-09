"""Alchemy mixer widget for selecting and combining ingredients.

This widget provides an interface for players to select emotion ingredients
and adjust their percentages for experimental mixing.
"""

from typing import Dict, List
from decimal import Decimal

from textual.app import ComposeResult
from textual.widgets import Static, Label, Input, Button
from textual.containers import Vertical, Horizontal, Container
from textual.reactive import reactive
from textual.message import Message


class IngredientSlider(Static):
    """Widget for adjusting a single ingredient's percentage."""

    percentage: reactive[float] = reactive(0.0)

    def __init__(
        self,
        emotion_type: str,
        initial_value: float = 0.0,
        **kwargs
    ):
        """Initialize the ingredient slider.

        Args:
            emotion_type: Type of emotion (e.g., "Joy", "Sadness")
            initial_value: Initial percentage value
            **kwargs: Additional widget arguments
        """
        super().__init__(**kwargs)
        self.emotion_type = emotion_type
        self.percentage = initial_value

    def compose(self) -> ComposeResult:
        """Create the slider layout."""
        with Horizontal(classes="ingredient-row"):
            yield Label(f"{self.emotion_type}:", classes="ingredient-label")
            yield Input(
                value=str(self.percentage),
                placeholder="0-100",
                id=f"input-{self.emotion_type}",
                classes="percentage-input"
            )
            yield Label("%", classes="percent-symbol")
            yield Static(self._render_bar(), id=f"bar-{self.emotion_type}", classes="percentage-bar")

    def _render_bar(self) -> str:
        """Render a visual percentage bar.

        Returns:
            String representation of percentage bar
        """
        filled = int(self.percentage / 10)
        empty = 10 - filled
        return f"[{'█' * filled}{'░' * empty}]"

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input value changes.

        Args:
            event: Input change event
        """
        if event.input.id != f"input-{self.emotion_type}":
            return

        try:
            value = float(event.value) if event.value else 0.0
            # Clamp to 0-100
            value = max(0.0, min(100.0, value))
            self.percentage = value

            # Update the bar
            bar = self.query_one(f"#bar-{self.emotion_type}", Static)
            bar.update(self._render_bar())

            # Notify parent
            self.post_message(self.PercentageChanged(self.emotion_type, self.percentage))

        except ValueError:
            # Invalid input, ignore
            pass

    def set_percentage(self, value: float) -> None:
        """Programmatically set the percentage.

        Args:
            value: New percentage value (0-100)
        """
        value = max(0.0, min(100.0, value))
        self.percentage = value

        # Update input
        input_widget = self.query_one(f"#input-{self.emotion_type}", Input)
        input_widget.value = f"{value:.1f}"

        # Update bar
        bar = self.query_one(f"#bar-{self.emotion_type}", Static)
        bar.update(self._render_bar())

    class PercentageChanged(Message):
        """Message posted when percentage changes."""

        def __init__(self, emotion_type: str, percentage: float):
            """Initialize the message.

            Args:
                emotion_type: Type of emotion
                percentage: New percentage value
            """
            super().__init__()
            self.emotion_type = emotion_type
            self.percentage = percentage


class AlchemyMixer(Static):
    """Widget for mixing emotion ingredients."""

    # Available emotion types for mixing
    EMOTION_TYPES = [
        "Joy",
        "Sadness",
        "Anger",
        "Fear",
        "Love",
        "Disgust",
        "Determination",
        "Nostalgia",
        "Hope",
        "Empathy",
    ]

    total_percentage: reactive[float] = reactive(0.0)

    def __init__(
        self,
        available_emotions: List[str] = None,
        **kwargs
    ):
        """Initialize the alchemy mixer.

        Args:
            available_emotions: List of available emotions (defaults to all)
            **kwargs: Additional widget arguments
        """
        super().__init__(**kwargs)
        self.available_emotions = available_emotions or self.EMOTION_TYPES
        self.sliders: Dict[str, IngredientSlider] = {}

    def compose(self) -> ComposeResult:
        """Create the mixer layout."""
        with Vertical(classes="mixer-container"):
            yield Static("Ingredient Mixer", classes="mixer-title")
            yield Static("Adjust percentages to create custom mixes", classes="mixer-subtitle")

            # Ingredient sliders
            with Vertical(id="sliders-container"):
                for emotion in self.available_emotions:
                    slider = IngredientSlider(emotion, classes="ingredient-slider")
                    self.sliders[emotion] = slider
                    yield slider

            # Total display
            yield Horizontal(
                Label("Total:", classes="total-label"),
                Static("0.0%", id="total-display", classes="total-value"),
                classes="total-row"
            )

            # Quick action buttons
            with Horizontal(classes="mixer-buttons"):
                yield Button("Equal Split", id="btn-equal-split", variant="default")
                yield Button("Random", id="btn-random", variant="default")
                yield Button("Clear", id="btn-clear", variant="default")

            # Help text
            yield Static(
                "💡 Tip: Total must equal 100% to craft. Mix ingredients to discover new recipes!",
                classes="help-text"
            )

    def on_ingredient_slider_percentage_changed(self, message: IngredientSlider.PercentageChanged) -> None:
        """Handle slider percentage changes.

        Args:
            message: Percentage change message
        """
        self._update_total()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: Button press event
        """
        button_id = event.button.id

        if button_id == "btn-equal-split":
            self._equal_split()
        elif button_id == "btn-random":
            self._random_mix()
        elif button_id == "btn-clear":
            self._clear_all()

    def _update_total(self) -> None:
        """Update the total percentage display."""
        total = sum(slider.percentage for slider in self.sliders.values())
        self.total_percentage = total

        # Update display
        total_display = self.query_one("#total-display", Static)
        total_text = f"{total:.1f}%"

        # Color code based on validity
        if abs(total - 100.0) < 0.01:
            total_text = f"[green]{total_text} ✓[/green]"
        elif total > 100.0:
            total_text = f"[red]{total_text} ⚠[/red]"
        else:
            total_text = f"[yellow]{total_text}[/yellow]"

        total_display.update(total_text)

    def _equal_split(self) -> None:
        """Split percentage equally among non-zero sliders."""
        # Get sliders with non-zero values
        active_sliders = [
            slider for slider in self.sliders.values()
            if slider.percentage > 0
        ]

        if not active_sliders:
            # If none are active, use first 3
            active_sliders = list(self.sliders.values())[:3]

        # Split equally
        percentage = 100.0 / len(active_sliders)
        for slider in active_sliders:
            slider.set_percentage(percentage)

        # Clear others
        for slider in self.sliders.values():
            if slider not in active_sliders:
                slider.set_percentage(0.0)

        self._update_total()

    def _random_mix(self) -> None:
        """Create a random mix with 2-4 ingredients."""
        import random

        # Clear all first
        for slider in self.sliders.values():
            slider.set_percentage(0.0)

        # Pick 2-4 random ingredients
        num_ingredients = random.randint(2, 4)
        selected = random.sample(list(self.sliders.values()), num_ingredients)

        # Generate random percentages that sum to 100
        percentages = []
        remaining = 100.0
        for i in range(num_ingredients - 1):
            # Random percentage of remaining
            pct = random.uniform(10, remaining - 10 * (num_ingredients - i - 1))
            percentages.append(pct)
            remaining -= pct
        percentages.append(remaining)

        # Shuffle to randomize which gets which percentage
        random.shuffle(percentages)

        # Apply to selected sliders
        for slider, pct in zip(selected, percentages):
            slider.set_percentage(pct)

        self._update_total()

    def _clear_all(self) -> None:
        """Clear all ingredient percentages."""
        for slider in self.sliders.values():
            slider.set_percentage(0.0)
        self._update_total()

    def get_ingredients(self) -> Dict[str, float]:
        """Get current ingredient mix.

        Returns:
            Dict mapping emotion type to percentage
        """
        return {
            emotion: slider.percentage
            for emotion, slider in self.sliders.items()
            if slider.percentage > 0
        }

    def set_ingredients(self, ingredients: Dict[str, float]) -> None:
        """Set ingredient percentages.

        Args:
            ingredients: Dict mapping emotion type to percentage
        """
        # Clear all first
        for slider in self.sliders.values():
            slider.set_percentage(0.0)

        # Set specified ingredients
        for emotion, percentage in ingredients.items():
            if emotion in self.sliders:
                self.sliders[emotion].set_percentage(percentage)

        self._update_total()

    def is_valid_mix(self) -> bool:
        """Check if current mix is valid (sums to 100%).

        Returns:
            True if total is 100%, False otherwise
        """
        return abs(self.total_percentage - 100.0) < 0.01

    def get_active_emotions(self) -> List[str]:
        """Get list of emotions with non-zero percentages.

        Returns:
            List of emotion types
        """
        return [
            emotion for emotion, slider in self.sliders.items()
            if slider.percentage > 0
        ]
