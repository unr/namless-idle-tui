"""Production and generation systems for Emotion Merchant.

This module handles:
- Passive resource generation per tick
- Producer buildings that generate resources
- Storage overflow handling
- Purity degradation over time
- Upgrade system for storage and production

The production engine is the heart of the idle game mechanics, managing all
resource generation, storage, and quality maintenance systems.
"""

from decimal import Decimal
from typing import TYPE_CHECKING, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

if TYPE_CHECKING:
    from .state import GameStateManager

from .resources import EmotionTier, EMOTION_CONFIGS


class StorageUpgrade(Enum):
    """Storage upgrade tiers.

    Each tier provides increased capacity and reduced purity degradation,
    culminating in the Infinite Void which eliminates all storage constraints.
    """

    BASIC_VESSELS = 1  # +50% capacity
    REINFORCED = 2  # +100% capacity, -10% degradation
    CRYSTAL = 3  # +200% capacity, -25% degradation
    QUANTUM = 4  # +500% capacity, -50% degradation
    INFINITE_VOID = 5  # Infinite capacity, no degradation


@dataclass
class StorageUpgradeConfig:
    """Configuration for storage upgrades.

    Attributes:
        level: The storage upgrade tier
        name: Display name for the upgrade
        capacity_multiplier: Multiplier applied to base storage capacity
        degradation_reduction: Percentage reduction in purity decay (0.0-1.0)
        cost_multiplier: Cost scaling factor for this upgrade tier
    """

    level: StorageUpgrade
    name: str
    capacity_multiplier: float
    degradation_reduction: float
    cost_multiplier: float


# Complete storage upgrade configurations based on game design
STORAGE_UPGRADES: Dict[StorageUpgrade, StorageUpgradeConfig] = {
    StorageUpgrade.BASIC_VESSELS: StorageUpgradeConfig(
        level=StorageUpgrade.BASIC_VESSELS,
        name="Basic Vessels",
        capacity_multiplier=1.5,
        degradation_reduction=0.0,
        cost_multiplier=1.0,
    ),
    StorageUpgrade.REINFORCED: StorageUpgradeConfig(
        level=StorageUpgrade.REINFORCED,
        name="Reinforced Containers",
        capacity_multiplier=2.0,
        degradation_reduction=0.1,
        cost_multiplier=2.5,
    ),
    StorageUpgrade.CRYSTAL: StorageUpgradeConfig(
        level=StorageUpgrade.CRYSTAL,
        name="Crystal Storage",
        capacity_multiplier=3.0,
        degradation_reduction=0.25,
        cost_multiplier=10.0,
    ),
    StorageUpgrade.QUANTUM: StorageUpgradeConfig(
        level=StorageUpgrade.QUANTUM,
        name="Quantum Containment",
        capacity_multiplier=6.0,
        degradation_reduction=0.5,
        cost_multiplier=50.0,
    ),
    StorageUpgrade.INFINITE_VOID: StorageUpgradeConfig(
        level=StorageUpgrade.INFINITE_VOID,
        name="Infinite Void",
        capacity_multiplier=float("inf"),
        degradation_reduction=1.0,
        cost_multiplier=250.0,
    ),
}


@dataclass
class Producer:
    """A producer building that generates resources.

    Producers are the primary source of passive income in the game.
    Each tier of emotion can have multiple producers working simultaneously,
    with efficiency bonuses and global multipliers applying to output.

    Attributes:
        tier: The emotion tier this producer generates
        count: Number of producers owned
        efficiency: Production efficiency multiplier (base 1.0)
    """

    tier: EmotionTier
    count: int = 0
    efficiency: float = 1.0

    def get_production_rate(self, global_multiplier: Decimal = Decimal("1")) -> Decimal:
        """Calculate production per second for this producer.

        Formula: base_rate × count × efficiency × global_multiplier

        Args:
            global_multiplier: Global production bonus (from prestige, upgrades, etc.)

        Returns:
            Production rate in resources per second
        """
        if self.count == 0:
            return Decimal("0")

        config = EMOTION_CONFIGS[self.tier]
        base_rate = config.production_rate * self.count
        return base_rate * Decimal(str(self.efficiency)) * global_multiplier

    def get_cost_for_next(self) -> Decimal:
        """Calculate the cost to buy the next producer.

        Uses exponential scaling: base_cost × 1.15^count

        Returns:
            Cost in the previous tier's currency
        """
        config = EMOTION_CONFIGS[self.tier]
        return config.base_cost * Decimal(str(1.15**self.count))


class ProductionEngine:
    """Manages all production and generation systems.

    The ProductionEngine is responsible for:
    - Calculating and applying passive resource generation
    - Managing producer buildings and their costs
    - Handling storage upgrades and capacity
    - Applying purity degradation over time
    - Computing offline progression gains

    This is the core idle game loop manager.
    """

    def __init__(self, state_manager: "GameStateManager") -> None:
        """Initialize the production engine.

        Args:
            state_manager: Reference to the game state manager
        """
        self.state_manager = state_manager
        self.producers: Dict[EmotionTier, Producer] = {}
        self.storage_levels: Dict[EmotionTier, StorageUpgrade] = {}
        self._accumulated_time: float = 0.0

        # Initialize producers for each tier
        for tier in EmotionTier:
            self.producers[tier] = Producer(tier=tier)

    def tick(self, delta_seconds: float) -> None:
        """Process one tick of production.

        This is called regularly (typically 10 times per second) to:
        1. Generate resources from producers
        2. Apply storage limits
        3. Degrade purity over time

        Args:
            delta_seconds: Time elapsed since last tick
        """
        state = self.state_manager.state

        # Accumulate fractional time for more accurate calculations
        self._accumulated_time += delta_seconds

        for tier in EmotionTier:
            resource = state.resources[tier]
            if not resource.unlocked:
                continue

            producer = self.producers[tier]
            if producer.count == 0:
                continue

            # Calculate production
            production = producer.get_production_rate(state.global_multiplier)
            amount_to_add = production * Decimal(str(delta_seconds))

            # Apply storage limits (state_manager handles capping)
            self.state_manager.add_resource(tier, amount_to_add)

            # Apply purity degradation
            self._apply_purity_decay(tier, delta_seconds)

    def _apply_purity_decay(self, tier: EmotionTier, delta_seconds: float) -> None:
        """Apply purity degradation over time.

        Base decay: -0.1% per minute in storage
        Modified by storage upgrade level

        Args:
            tier: The emotion tier to apply decay to
            delta_seconds: Time elapsed since last decay application
        """
        resource = self.state_manager.state.resources[tier]
        if resource.amount <= 0:
            return

        # Base decay rate: 0.1% per minute = 0.001667% per second
        # Purity is stored as 0-100 scale, so we keep percentage points
        base_decay_per_second = 0.1 / 60.0  # 0.1% per minute

        # Apply storage upgrade reduction
        upgrade_level = self.storage_levels.get(tier)
        if upgrade_level:
            config = STORAGE_UPGRADES[upgrade_level]
            base_decay_per_second *= 1.0 - config.degradation_reduction

        # Calculate total decay amount
        decay_amount = base_decay_per_second * delta_seconds

        # Apply decay (purity is 0.0-100.0 scale)
        resource.purity = max(0.0, resource.purity - decay_amount)

    def buy_producer(self, tier: EmotionTier) -> bool:
        """Buy a producer for the given tier.

        Costs scale exponentially with each purchase (1.15^count).
        Payment is made in the previous tier's currency.
        Buying the first producer auto-unlocks that tier.

        Args:
            tier: The emotion tier to buy a producer for

        Returns:
            True if purchase was successful, False if insufficient funds
        """
        producer = self.producers[tier]

        # Calculate cost with exponential scaling
        cost = producer.get_cost_for_next()

        # Determine payment tier (one tier below what's being bought)
        # Smiles (tier 0) can only be produced by clicking, not bought
        if tier == EmotionTier.SMILES:
            return False

        payment_tier = EmotionTier(tier.value - 1)

        # Attempt purchase
        if self.state_manager.spend_resource(payment_tier, cost):
            producer.count += 1
            self.state_manager.state.resources[tier].producers = producer.count

            # Auto-unlock the tier if first producer
            if producer.count == 1:
                self.state_manager.unlock_resource(tier)

            return True
        return False

    def get_producer_cost(self, tier: EmotionTier) -> Decimal:
        """Get current cost to buy next producer.

        Args:
            tier: The emotion tier to check cost for

        Returns:
            Cost in the previous tier's currency
        """
        producer = self.producers[tier]
        return producer.get_cost_for_next()

    def get_producer_count(self, tier: EmotionTier) -> int:
        """Get the number of producers owned for a tier.

        Args:
            tier: The emotion tier to check

        Returns:
            Number of producers owned
        """
        return self.producers[tier].count

    def set_producer_efficiency(self, tier: EmotionTier, efficiency: float) -> None:
        """Set the efficiency multiplier for a producer.

        Used by upgrades and temporary boosts.

        Args:
            tier: The emotion tier to modify
            efficiency: New efficiency multiplier (1.0 = 100%)
        """
        self.producers[tier].efficiency = max(0.0, efficiency)

    def upgrade_storage(self, tier: EmotionTier) -> bool:
        """Upgrade storage for a tier.

        Progressively increases capacity and reduces degradation.
        Cannot upgrade beyond Infinite Void level.

        Args:
            tier: The emotion tier to upgrade storage for

        Returns:
            True if upgrade was successful, False if already at max or insufficient funds
        """
        current_level = self.storage_levels.get(tier)

        # Check if already at max level
        if current_level == StorageUpgrade.INFINITE_VOID:
            return False

        # Determine next level
        next_level_value = 1 if current_level is None else current_level.value + 1
        if next_level_value > 5:
            return False

        next_level = StorageUpgrade(next_level_value)
        next_config = STORAGE_UPGRADES[next_level]

        # Calculate upgrade cost (cost increases with tier and upgrade level)
        base_cost = EMOTION_CONFIGS[tier].base_cost
        upgrade_cost = base_cost * Decimal(str(next_config.cost_multiplier))

        # Payment is in the same tier's currency
        if not self.state_manager.spend_resource(tier, upgrade_cost):
            return False

        # Apply upgrade
        self.storage_levels[tier] = next_level
        base_storage = EMOTION_CONFIGS[tier].base_storage

        # Handle infinite capacity
        if next_level == StorageUpgrade.INFINITE_VOID:
            new_capacity = EMOTION_CONFIGS[tier].max_storage
        else:
            new_capacity = int(base_storage * next_config.capacity_multiplier)

        self.state_manager.state.resources[tier].storage_capacity = new_capacity
        return True

    def get_storage_upgrade_cost(self, tier: EmotionTier) -> Optional[Decimal]:
        """Get the cost of the next storage upgrade for a tier.

        Args:
            tier: The emotion tier to check

        Returns:
            Cost of next upgrade, or None if already at max level
        """
        current_level = self.storage_levels.get(tier)

        if current_level == StorageUpgrade.INFINITE_VOID:
            return None

        next_level_value = 1 if current_level is None else current_level.value + 1
        if next_level_value > 5:
            return None

        next_level = StorageUpgrade(next_level_value)
        next_config = STORAGE_UPGRADES[next_level]

        base_cost = EMOTION_CONFIGS[tier].base_cost
        return base_cost * Decimal(str(next_config.cost_multiplier))

    def get_storage_level(self, tier: EmotionTier) -> Optional[StorageUpgrade]:
        """Get the current storage upgrade level for a tier.

        Args:
            tier: The emotion tier to check

        Returns:
            Current storage upgrade level, or None if not upgraded
        """
        return self.storage_levels.get(tier)

    def get_total_production_rate(self, tier: EmotionTier) -> Decimal:
        """Get total production rate for a tier including all bonuses.

        Args:
            tier: The emotion tier to calculate for

        Returns:
            Total production rate per second
        """
        if tier not in self.producers:
            return Decimal("0")

        producer = self.producers[tier]
        return producer.get_production_rate(self.state_manager.state.global_multiplier)

    def calculate_offline_gains(self, offline_seconds: float) -> Dict[EmotionTier, Decimal]:
        """Calculate resources gained while offline.

        Offline progression mechanics:
        - Default efficiency: 50% (can be upgraded)
        - Respects storage capacity limits
        - Does NOT apply purity degradation (would be too punishing)

        Args:
            offline_seconds: Time elapsed while player was offline

        Returns:
            Dictionary mapping tiers to resources gained
        """
        gains: Dict[EmotionTier, Decimal] = {}

        # Offline efficiency (50% default, upgradeable)
        offline_efficiency = Decimal("0.5")

        # Could be modified by upgrades:
        # offline_efficiency = self.state_manager.state.offline_efficiency

        for tier in EmotionTier:
            resource = self.state_manager.state.resources[tier]
            if not resource.unlocked:
                continue

            producer = self.producers[tier]
            if producer.count == 0:
                continue

            # Calculate potential production
            rate = producer.get_production_rate(self.state_manager.state.global_multiplier)
            potential = rate * Decimal(str(offline_seconds)) * offline_efficiency

            # Cap at available storage space
            space = Decimal(resource.storage_capacity) - resource.amount
            actual_gain = min(potential, max(Decimal("0"), space))

            if actual_gain > 0:
                gains[tier] = actual_gain

        return gains

    def apply_offline_gains(self, offline_seconds: float) -> Dict[EmotionTier, Decimal]:
        """Calculate and apply offline gains to game state.

        Args:
            offline_seconds: Time elapsed while player was offline

        Returns:
            Dictionary of resources actually gained (for display to player)
        """
        gains = self.calculate_offline_gains(offline_seconds)

        for tier, amount in gains.items():
            self.state_manager.add_resource(tier, amount)

        return gains

    def get_production_info(self, tier: EmotionTier) -> Dict[str, Any]:
        """Get comprehensive production information for a tier.

        Useful for UI display and debugging.

        Args:
            tier: The emotion tier to get info for

        Returns:
            Dictionary containing production statistics
        """
        producer = self.producers[tier]
        resource = self.state_manager.state.resources[tier]
        storage_level = self.storage_levels.get(tier)

        return {
            "tier": tier,
            "unlocked": resource.unlocked,
            "producer_count": producer.count,
            "efficiency": producer.efficiency,
            "production_rate": self.get_total_production_rate(tier),
            "next_cost": self.get_producer_cost(tier),
            "storage_capacity": resource.storage_capacity,
            "storage_level": storage_level,
            "storage_upgrade_cost": self.get_storage_upgrade_cost(tier),
            "purity": resource.purity,
            "amount": resource.amount,
        }

    def reset(self) -> None:
        """Reset the production engine to initial state.

        Used for prestige or new game.
        Preserves any prestige bonuses through state_manager.
        """
        for tier in EmotionTier:
            self.producers[tier] = Producer(tier=tier)

        self.storage_levels.clear()
        self._accumulated_time = 0.0

    def save_state(self) -> Dict[str, Any]:
        """Serialize production engine state for saving.

        Returns:
            Dictionary containing serializable state data
        """
        return {
            "producers": {
                tier.name: {
                    "count": producer.count,
                    "efficiency": producer.efficiency,
                }
                for tier, producer in self.producers.items()
            },
            "storage_levels": {
                tier.name: level.value for tier, level in self.storage_levels.items()
            },
        }

    def load_state(self, state_data: Dict[str, Any]) -> None:
        """Restore production engine state from saved data.

        Args:
            state_data: Dictionary containing saved state data
        """
        # Load producer data
        if "producers" in state_data:
            for tier_name, producer_data in state_data["producers"].items():
                try:
                    tier = EmotionTier[tier_name]
                    self.producers[tier].count = producer_data.get("count", 0)
                    self.producers[tier].efficiency = producer_data.get("efficiency", 1.0)
                except (KeyError, ValueError):
                    # Skip invalid tier names
                    continue

        # Load storage upgrade data
        if "storage_levels" in state_data:
            for tier_name, level_value in state_data["storage_levels"].items():
                try:
                    tier = EmotionTier[tier_name]
                    level = StorageUpgrade(level_value)
                    self.storage_levels[tier] = level

                    # Reapply storage capacity
                    config = STORAGE_UPGRADES[level]
                    base_storage = EMOTION_CONFIGS[tier].base_storage
                    if level == StorageUpgrade.INFINITE_VOID:
                        new_capacity = EMOTION_CONFIGS[tier].max_storage
                    else:
                        new_capacity = int(base_storage * config.capacity_multiplier)
                    self.state_manager.state.resources[tier].storage_capacity = new_capacity
                except (KeyError, ValueError):
                    # Skip invalid data
                    continue
