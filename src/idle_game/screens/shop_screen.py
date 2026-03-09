"""Shop screen for purchasing upgrades."""

from decimal import Decimal
from typing import Optional

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Header, Footer, Static, Button, Label
from textual.message import Message

from ..models.game_state import GameState
from ..models.upgrades import UPGRADE_DEFINITIONS, UpgradeDefinition


class UpgradeButton(Static):
    """Widget for a single upgrade item."""

    DEFAULT_CSS = """
    UpgradeButton {
        height: auto;
        border: solid $primary;
        padding: 1;
        margin: 0 0 1 0;
        background: $panel;
    }

    UpgradeButton:hover {
        background: $boost;
        border: solid $accent;
    }

    UpgradeButton.affordable {
        border: solid $success;
    }

    UpgradeButton.maxed {
        border: solid $warning-darken-2;
        background: $surface-darken-1;
    }

    .upgrade_header {
        text-style: bold;
        color: $text;
    }

    .upgrade_description {
        color: $text-muted;
        margin: 1 0;
    }

    .upgrade_cost {
        color: $success;
    }

    .upgrade_cost_expensive {
        color: $error;
    }

    .upgrade_effect {
        color: $accent;
        text-style: italic;
    }

    .maxed_label {
        color: $warning;
        text-style: bold;
    }
    """

    def __init__(
        self,
        upgrade_def: UpgradeDefinition,
        current_level: int,
        cost: Decimal,
        can_afford: bool,
        is_maxed: bool
    ):
        super().__init__()
        self.upgrade_def = upgrade_def
        self.current_level = current_level
        self.cost = cost
        self.can_afford = can_afford
        self.is_maxed = is_maxed

        # Apply CSS classes
        if is_maxed:
            self.add_class("maxed")
        elif can_afford:
            self.add_class("affordable")

    def render(self) -> str:
        """Render the upgrade button."""
        upgrade = self.upgrade_def

        # Header line
        header = f"{upgrade.icon} {upgrade.name} (Level {self.current_level})"

        # Description
        description = f"   {upgrade.description}"

        # Effect line
        total_effect = upgrade.effect_per_level * self.current_level
        next_effect = upgrade.effect_per_level * (self.current_level + 1)
        effect_line = f"   Effect: +{total_effect:.0%} → +{next_effect:.0%}"

        # Cost line
        if self.is_maxed:
            cost_line = "   MAX LEVEL REACHED"
        else:
            cost_class = "affordable" if self.can_afford else "expensive"
            cost_line = f"   Cost: {self.cost:,.0f} {upgrade.cost_currency.title()}"

        # Max level info
        max_info = ""
        if upgrade.max_level > 0:
            max_info = f"   (Max: {upgrade.max_level})"

        lines = [header, description, effect_line, cost_line]
        if max_info and not self.is_maxed:
            lines.append(max_info)

        return "\n".join(lines)

    def on_click(self) -> None:
        """Handle click - emit custom message."""
        if not self.is_maxed:
            self.post_message(ShopScreen.UpgradePurchased(self.upgrade_def.id))


class ShopScreen(Screen):
    """Screen for purchasing upgrades."""

    CSS = """
    ShopScreen {
        layout: vertical;
    }

    #shop_header {
        dock: top;
        height: 3;
        background: $primary;
        color: $text;
        content-align: center middle;
        text-style: bold;
    }

    #shop_container {
        height: 1fr;
        overflow-y: auto;
        padding: 1;
    }

    #stats_bar {
        dock: bottom;
        height: 3;
        background: $surface;
        layout: horizontal;
        padding: 0 2;
    }

    .stat_item {
        width: 1fr;
        content-align: center middle;
    }
    """

    BINDINGS = [
        ("escape", "back", "Back to Game"),
        ("q", "quit", "Quit"),
    ]

    class UpgradePurchased(Message):
        """Message sent when an upgrade is purchased."""
        def __init__(self, upgrade_id: str):
            super().__init__()
            self.upgrade_id = upgrade_id

    def __init__(self, game_state: GameState):
        super().__init__()
        self.game_state = game_state

    def compose(self) -> ComposeResult:
        """Compose the shop screen UI."""
        yield Header()

        # Title
        yield Static("🏪 SHOP - UPGRADES & PERKS", id="shop_header")

        # Upgrade list
        with ScrollableContainer(id="shop_container"):
            yield Container(id="upgrades_list")

        # Stats bar
        with Horizontal(id="stats_bar"):
            yield Static("Smiles: 0", id="smiles_stat", classes="stat_item")
            yield Static("Joy: 0", id="joy_stat", classes="stat_item")
            yield Static("Love: 0", id="love_stat", classes="stat_item")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the shop display."""
        self.refresh_shop()

    def refresh_shop(self) -> None:
        """Refresh the shop display with current prices and affordability."""
        try:
            container = self.query_one("#upgrades_list", Container)
            container.remove_children()

            # Get current resources
            resource_amounts = {
                emotion_type: resource.amount
                for emotion_type, resource in self.game_state.resources.items()
            }

            # Add each upgrade
            for upgrade_id, upgrade_def in UPGRADE_DEFINITIONS.items():
                current_level = self.game_state.upgrade_manager.get_upgrade_level(upgrade_id)
                cost = self.game_state.upgrade_manager.calculate_upgrade_cost(upgrade_id)

                # Check if maxed
                is_maxed = (
                    upgrade_def.max_level > 0
                    and current_level >= upgrade_def.max_level
                )

                # Check if can afford
                can_afford = self.game_state.upgrade_manager.can_afford_upgrade(
                    upgrade_id,
                    resource_amounts
                )

                # Create upgrade button
                upgrade_button = UpgradeButton(
                    upgrade_def=upgrade_def,
                    current_level=current_level,
                    cost=cost,
                    can_afford=can_afford,
                    is_maxed=is_maxed
                )

                container.mount(upgrade_button)

            # Update resource stats
            self.update_resource_stats()

        except Exception:
            pass  # Silently fail if not mounted

    def update_resource_stats(self) -> None:
        """Update the resource display at the bottom."""
        try:
            smiles = self.game_state.get_resource("smiles")
            joy = self.game_state.get_resource("joy")
            love = self.game_state.get_resource("love")

            smiles_stat = self.query_one("#smiles_stat", Static)
            joy_stat = self.query_one("#joy_stat", Static)
            love_stat = self.query_one("#love_stat", Static)

            smiles_stat.update(f"☺ Smiles: {smiles.amount:,.0f}")
            joy_stat.update(f"❤ Joy: {joy.amount:,.0f}")
            love_stat.update(f"💕 Love: {love.amount:,.0f}")

        except Exception:
            pass

    def on_shop_screen_upgrade_purchased(self, message: UpgradePurchased) -> None:
        """Handle upgrade purchase attempt."""
        success = self.game_state.purchase_upgrade(message.upgrade_id)

        if success:
            upgrade_def = UPGRADE_DEFINITIONS[message.upgrade_id]
            new_level = self.game_state.upgrade_manager.get_upgrade_level(message.upgrade_id)

            self.app.notify(
                f"✓ Purchased {upgrade_def.name} (Level {new_level})!",
                title="Upgrade Purchased",
                severity="information",
                timeout=3
            )

            # Refresh shop to show new prices
            self.refresh_shop()
        else:
            self.app.notify(
                "✗ Cannot purchase upgrade (insufficient resources or max level)",
                severity="error",
                timeout=3
            )

    def action_back(self) -> None:
        """Return to game screen."""
        self.app.pop_screen()

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()
