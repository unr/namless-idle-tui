"""Upgrade definitions and management for the shop system."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional
from enum import Enum


class UpgradeCategory(Enum):
    """Categories of upgrades."""
    PRODUCTION = "production"
    CLICKING = "clicking"
    STORAGE = "storage"
    OFFLINE = "offline"
    AUTOMATION = "automation"


@dataclass
class UpgradeDefinition:
    """Definition of an upgrade available in the shop."""
    id: str
    name: str
    description: str
    category: UpgradeCategory
    base_cost: Decimal
    cost_currency: str  # Which emotion is used to buy this
    cost_scaling: float  # Multiplier per level
    max_level: int  # 0 = infinite
    effect_per_level: float  # How much the effect increases per level
    icon: str  # Display icon


# Define all available upgrades
UPGRADE_DEFINITIONS: Dict[str, UpgradeDefinition] = {
    "click_power": UpgradeDefinition(
        id="click_power",
        name="Stronger Smiles",
        description="Increase manual click harvesting power",
        category=UpgradeCategory.CLICKING,
        base_cost=Decimal("100"),
        cost_currency="smiles",
        cost_scaling=1.5,
        max_level=0,  # Infinite
        effect_per_level=0.2,  # +20% per level
        icon="💪"
    ),
    "production_boost": UpgradeDefinition(
        id="production_boost",
        name="Production Efficiency",
        description="Increase all passive production rates",
        category=UpgradeCategory.PRODUCTION,
        base_cost=Decimal("500"),
        cost_currency="smiles",
        cost_scaling=1.8,
        max_level=0,
        effect_per_level=0.1,  # +10% per level
        icon="⚡"
    ),
    "storage_expansion": UpgradeDefinition(
        id="storage_expansion",
        name="Better Vessels",
        description="Increase storage capacity for all emotions",
        category=UpgradeCategory.STORAGE,
        base_cost=Decimal("1000"),
        cost_currency="smiles",
        cost_scaling=2.0,
        max_level=0,
        effect_per_level=0.25,  # +25% per level
        icon="📦"
    ),
    "offline_efficiency": UpgradeDefinition(
        id="offline_efficiency",
        name="Persistent Emotions",
        description="Improve offline progression efficiency",
        category=UpgradeCategory.OFFLINE,
        base_cost=Decimal("5000"),
        cost_currency="joy",
        cost_scaling=2.5,
        max_level=10,  # Max 10 levels
        effect_per_level=0.05,  # +5% per level
        icon="⏰"
    ),
    "auto_clicker": UpgradeDefinition(
        id="auto_clicker",
        name="Automatic Harvester",
        description="Automatically click once per second",
        category=UpgradeCategory.AUTOMATION,
        base_cost=Decimal("10000"),
        cost_currency="joy",
        cost_scaling=1.0,  # Doesn't scale, one-time purchase
        max_level=1,  # Only buy once
        effect_per_level=1.0,  # Binary on/off
        icon="🤖"
    ),
}


class UpgradeManager:
    """Manages player's purchased upgrades."""

    def __init__(self):
        """Initialize the upgrade manager."""
        self.purchased_upgrades: Dict[str, int] = {}  # upgrade_id -> level

    def get_upgrade_level(self, upgrade_id: str) -> int:
        """Get the current level of an upgrade.

        Args:
            upgrade_id: ID of the upgrade

        Returns:
            Current level (0 if not purchased)
        """
        return self.purchased_upgrades.get(upgrade_id, 0)

    def can_afford_upgrade(self, upgrade_id: str, resources: Dict[str, Decimal]) -> bool:
        """Check if player can afford to buy the next level.

        Args:
            upgrade_id: ID of the upgrade
            resources: Current resource amounts {emotion_type: amount}

        Returns:
            True if affordable
        """
        if upgrade_id not in UPGRADE_DEFINITIONS:
            return False

        upgrade_def = UPGRADE_DEFINITIONS[upgrade_id]
        current_level = self.get_upgrade_level(upgrade_id)

        # Check max level
        if upgrade_def.max_level > 0 and current_level >= upgrade_def.max_level:
            return False

        # Calculate cost for next level
        cost = self.calculate_upgrade_cost(upgrade_id)
        currency = upgrade_def.cost_currency

        # Check if player has enough currency
        return resources.get(currency, Decimal("0")) >= cost

    def calculate_upgrade_cost(self, upgrade_id: str) -> Decimal:
        """Calculate the cost for the next level of an upgrade.

        Args:
            upgrade_id: ID of the upgrade

        Returns:
            Cost in the upgrade's currency
        """
        if upgrade_id not in UPGRADE_DEFINITIONS:
            return Decimal("999999999")

        upgrade_def = UPGRADE_DEFINITIONS[upgrade_id]
        current_level = self.get_upgrade_level(upgrade_id)

        # Cost = base_cost * (cost_scaling ^ current_level)
        cost = upgrade_def.base_cost * Decimal(str(upgrade_def.cost_scaling ** current_level))
        return cost

    def purchase_upgrade(self, upgrade_id: str) -> bool:
        """Attempt to purchase the next level of an upgrade.

        This only updates the level, the caller must deduct resources.

        Args:
            upgrade_id: ID of the upgrade

        Returns:
            True if purchase successful
        """
        if upgrade_id not in UPGRADE_DEFINITIONS:
            return False

        upgrade_def = UPGRADE_DEFINITIONS[upgrade_id]
        current_level = self.get_upgrade_level(upgrade_id)

        # Check max level
        if upgrade_def.max_level > 0 and current_level >= upgrade_def.max_level:
            return False

        # Increase level
        self.purchased_upgrades[upgrade_id] = current_level + 1
        return True

    def get_total_effect(self, upgrade_id: str) -> float:
        """Get the total effect of an upgrade at its current level.

        Args:
            upgrade_id: ID of the upgrade

        Returns:
            Total multiplier or bonus
        """
        if upgrade_id not in UPGRADE_DEFINITIONS:
            return 0.0

        upgrade_def = UPGRADE_DEFINITIONS[upgrade_id]
        current_level = self.get_upgrade_level(upgrade_id)

        # Total effect = effect_per_level * current_level
        return upgrade_def.effect_per_level * current_level

    def get_total_multiplier(self, upgrade_id: str) -> float:
        """Get the total multiplier from an upgrade (1.0 + total_effect).

        Args:
            upgrade_id: ID of the upgrade

        Returns:
            Multiplier (1.0 = no bonus, 1.5 = +50%)
        """
        return 1.0 + self.get_total_effect(upgrade_id)

    def to_dict(self) -> Dict:
        """Serialize to dictionary for saving."""
        return {
            "purchased_upgrades": self.purchased_upgrades.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'UpgradeManager':
        """Deserialize from dictionary."""
        manager = cls()
        manager.purchased_upgrades = data.get("purchased_upgrades", {})
        return manager
