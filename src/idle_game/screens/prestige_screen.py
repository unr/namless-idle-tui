"""Prestige screen for emotional rebirth system."""

from decimal import Decimal
from typing import Optional

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer, Center
from textual.widgets import Header, Footer, Static, Button, Label
from textual.message import Message

from ..models.game_state import GameState


class PrestigeScreen(Screen):
    """Screen for prestige (emotional rebirth) system."""

    CSS = """
    PrestigeScreen {
        layout: vertical;
    }

    #prestige_header {
        dock: top;
        height: 5;
        background: $warning;
        color: $text;
        content-align: center middle;
        text-style: bold;
    }

    #prestige_container {
        height: 1fr;
        overflow-y: auto;
        padding: 2;
    }

    .prestige_section {
        border: solid $primary;
        padding: 1 2;
        margin: 1 0;
        background: $panel;
    }

    .section_title {
        text-style: bold underline;
        color: $accent;
        margin: 0 0 1 0;
    }

    .stat_line {
        color: $text-muted;
        margin: 0 0 0 2;
    }

    .highlight {
        color: $success;
        text-style: bold;
    }

    .warning {
        color: $error;
        text-style: bold;
    }

    .ed_display {
        text-align: center;
        text-style: bold;
        color: $accent;
        background: $boost;
        padding: 1;
        margin: 1 0;
    }

    #button_container {
        height: auto;
        layout: horizontal;
        align: center middle;
        padding: 1;
    }

    #prestige_btn {
        width: 30;
        margin: 0 1;
    }

    #cancel_btn {
        width: 20;
        margin: 0 1;
    }

    .requirement_failed {
        color: $error;
        text-style: bold;
    }

    .requirement_met {
        color: $success;
    }
    """

    BINDINGS = [
        ("escape", "back", "Back to Game"),
        ("q", "quit", "Quit"),
    ]

    class PrestigeConfirmed(Message):
        """Message sent when prestige is confirmed."""
        pass

    def __init__(self, game_state: GameState):
        super().__init__()
        self.game_state = game_state

    def compose(self) -> ComposeResult:
        """Compose the prestige screen UI."""
        yield Header()

        # Title
        yield Static(
            "✨ EMOTIONAL REBIRTH ✨\n"
            "\"You have felt everything. Now, feel it all again, anew.\"",
            id="prestige_header"
        )

        # Content
        with ScrollableContainer(id="prestige_container"):
            yield Container(id="prestige_content")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the prestige display."""
        self.refresh_prestige_info()

    def refresh_prestige_info(self) -> None:
        """Refresh the prestige information display."""
        try:
            container = self.query_one("#prestige_content", Container)
            container.remove_children()

            # Check requirements
            can_prestige, requirements_text = self._check_prestige_requirements()

            # Requirements section
            requirements_section = Vertical(classes="prestige_section")
            requirements_section.mount(Static("REQUIREMENTS:", classes="section_title"))
            requirements_section.mount(Static(requirements_text))
            container.mount(requirements_section)

            # Calculate ED gain
            ed_gain = self._calculate_ed_gain()

            # ED Gain section
            ed_section = Vertical(classes="prestige_section")
            ed_section.mount(Static("EMOTIONAL DEPTH GAINED:", classes="section_title"))
            ed_section.mount(Static(
                f"\n🌟 You will gain {ed_gain} Emotional Depth 🌟\n",
                classes="ed_display"
            ))
            ed_section.mount(Static(
                f"   Based on: {len(self.game_state.recipes_discovered)} recipes × "
                f"{self._get_average_satisfaction():.1f}% satisfaction × "
                f"{float(self.game_state.ethical_score):.1f}% ethics",
                classes="stat_line"
            ))
            container.mount(ed_section)

            # Current bonuses section
            bonuses_section = Vertical(classes="prestige_section")
            bonuses_section.mount(Static("CURRENT PRESTIGE BONUSES:", classes="section_title"))

            total_ed = self.game_state.emotional_depth
            production_bonus = total_ed * 3  # +3% per ED
            purity_bonus = total_ed * 0.5  # +0.5% per ED
            storage_bonus = total_ed * 2  # +2% per ED

            bonuses_section.mount(Static(
                f"   Total Emotional Depth: {total_ed}\n"
                f"   Production: +{production_bonus:.1f}%\n"
                f"   Purity: +{purity_bonus:.1f}%\n"
                f"   Storage: +{storage_bonus:.1f}%",
                classes="stat_line"
            ))
            container.mount(bonuses_section)

            # What you'll lose section
            lose_section = Vertical(classes="prestige_section")
            lose_section.mount(Static("YOU WILL LOSE:", classes="section_title"))
            lose_section.mount(Static(
                "   ✗ All resources (reset to 0)\n"
                "   ✗ All buildings (reset to 0)\n"
                "   ✗ All upgrades (must repurchase)\n"
                "   ✗ Click/production statistics\n",
                classes="warning"
            ))
            container.mount(lose_section)

            # What you'll keep section
            keep_section = Vertical(classes="prestige_section")
            keep_section.mount(Static("YOU WILL KEEP:", classes="section_title"))
            keep_section.mount(Static(
                "   ✓ Recipe knowledge\n"
                "   ✓ Emotional Depth (permanent bonuses)\n"
                "   ✓ Prestige count\n"
                "   ✓ Ethical score\n",
                classes="highlight"
            ))
            container.mount(keep_section)

            # Buttons
            button_container = Horizontal(id="button_container")

            if can_prestige:
                prestige_btn = Button(
                    "🌟 Emotional Rebirth 🌟",
                    variant="warning",
                    id="prestige_btn"
                )
                button_container.mount(prestige_btn)
            else:
                disabled_btn = Button(
                    "Requirements Not Met",
                    variant="error",
                    id="prestige_btn",
                    disabled=True
                )
                button_container.mount(disabled_btn)

            cancel_btn = Button("Cancel", variant="default", id="cancel_btn")
            button_container.mount(cancel_btn)

            container.mount(button_container)

        except Exception as e:
            pass  # Silently fail if not mounted

    def _check_prestige_requirements(self) -> tuple[bool, str]:
        """Check if player meets prestige requirements.

        Returns:
            Tuple of (can_prestige, requirements_text)
        """
        # For MVP, simplified requirements
        min_recipes = 3  # Need at least 3 recipes
        min_customers = 10  # Need to serve 10 customers

        recipes = len(self.game_state.recipes_discovered)
        customers = self.game_state.customers_served

        recipes_met = recipes >= min_recipes
        customers_met = customers >= min_customers

        recipes_class = "requirement_met" if recipes_met else "requirement_failed"
        customers_class = "requirement_met" if customers_met else "requirement_failed"

        requirements_text = (
            f"   {'✓' if recipes_met else '✗'} Discover {min_recipes}+ recipes "
            f"(Current: {recipes})\n"
            f"   {'✓' if customers_met else '✗'} Serve {min_customers}+ customers "
            f"(Current: {customers})\n"
        )

        can_prestige = recipes_met and customers_met
        return can_prestige, requirements_text

    def _calculate_ed_gain(self) -> int:
        """Calculate how much ED the player will gain."""
        recipes = len(self.game_state.recipes_discovered)
        satisfaction = self._get_average_satisfaction()
        ethics = float(self.game_state.ethical_score)

        # ED = (Recipes × Average Satisfaction × Ethical Score) / 100
        ed_gain = int((recipes * satisfaction * ethics) / 100.0)

        # Minimum 1 ED if they meet requirements
        if ed_gain == 0 and recipes > 0:
            ed_gain = 1

        return ed_gain

    def _get_average_satisfaction(self) -> float:
        """Get average customer satisfaction.

        For MVP, we'll use a placeholder value since we don't track satisfaction history yet.
        """
        # Placeholder: base it on ethical score and customers served
        if self.game_state.customers_served == 0:
            return 50.0

        # Simple heuristic: higher ethics = better satisfaction
        base_satisfaction = float(self.game_state.ethical_score)

        return min(100.0, max(0.0, base_satisfaction))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "prestige_btn":
            # Confirm prestige
            can_prestige, _ = self._check_prestige_requirements()

            if can_prestige:
                # Perform prestige
                ed_gained = self.game_state.reset_for_prestige()

                self.app.notify(
                    f"✨ Emotional Rebirth Complete! +{ed_gained} Emotional Depth!",
                    title="Prestige!",
                    severity="information",
                    timeout=8
                )

                # Go back to game
                self.app.pop_screen()
            else:
                self.app.notify(
                    "You do not meet the requirements for prestige.",
                    severity="error",
                    timeout=3
                )

        elif event.button.id == "cancel_btn":
            self.app.pop_screen()

    def action_back(self) -> None:
        """Return to game screen."""
        self.app.pop_screen()

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()
