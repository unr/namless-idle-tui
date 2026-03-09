"""Resource model representing emotion amounts, storage, and purity."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class Resource:
    """Represents a quantity of an emotion with storage and purity tracking.

    Attributes:
        amount: Current quantity of this emotion
        storage_capacity: Maximum amount that can be stored
        purity: Quality percentage (0-100)
        producer_count: Number of buildings/producers generating this emotion
    """
    amount: Decimal = Decimal("0")
    storage_capacity: int = 100
    purity: float = 100.0
    producer_count: int = 0

    def add(self, quantity: Decimal, incoming_purity: float = 100.0) -> Decimal:
        """Add resources, handling overflow and purity mixing.

        Args:
            quantity: Amount to add
            incoming_purity: Purity of incoming resources

        Returns:
            Amount that was actually added (may be less due to capacity)
        """
        if quantity <= 0:
            return Decimal("0")

        # Calculate available space
        available_space = Decimal(self.storage_capacity) - self.amount

        if available_space <= 0:
            # Storage full - purity damage from overflow
            self.purity = max(0.0, self.purity - 10.0)
            return Decimal("0")

        # Add what we can fit
        amount_to_add = min(quantity, available_space)

        # Mix purities weighted by amounts
        if self.amount > 0:
            total_amount = self.amount + amount_to_add
            self.purity = float(
                (Decimal(self.purity) * self.amount + Decimal(incoming_purity) * amount_to_add)
                / total_amount
            )
        else:
            self.purity = incoming_purity

        self.amount += amount_to_add

        # Handle overflow damage
        if quantity > available_space:
            overflow_penalty = min(5.0, float((quantity - available_space) / quantity) * 10.0)
            self.purity = max(0.0, self.purity - overflow_penalty)

        return amount_to_add

    def remove(self, quantity: Decimal) -> Decimal:
        """Remove resources if available.

        Args:
            quantity: Amount to remove

        Returns:
            Amount that was actually removed
        """
        if quantity <= 0:
            return Decimal("0")

        amount_to_remove = min(quantity, self.amount)
        self.amount -= amount_to_remove

        # Reset purity to 100% if empty
        if self.amount == 0:
            self.purity = 100.0

        return amount_to_remove

    def degrade_purity(self, delta_seconds: float) -> None:
        """Apply time-based purity degradation.

        Args:
            delta_seconds: Time elapsed since last degradation
        """
        if self.amount > 0:
            # -0.1% per minute = -0.00166% per second
            degradation_rate = 0.001666  # per second
            self.purity = max(0.0, self.purity - (degradation_rate * delta_seconds * 60))

    @property
    def is_full(self) -> bool:
        """Check if storage is at or above 95% capacity."""
        return self.amount >= Decimal(self.storage_capacity) * Decimal("0.95")

    @property
    def is_empty(self) -> bool:
        """Check if storage is empty."""
        return self.amount == 0

    @property
    def fill_percentage(self) -> float:
        """Get storage fill percentage (0-100)."""
        if self.storage_capacity == 0:
            return 0.0
        return min(100.0, float(self.amount) / self.storage_capacity * 100)

    @property
    def purity_tier(self) -> str:
        """Get purity quality tier name."""
        if self.purity >= 100.0:
            return "Pure"
        elif self.purity >= 75.0:
            return "Clean"
        elif self.purity >= 50.0:
            return "Mixed"
        elif self.purity >= 25.0:
            return "Contaminated"
        else:
            return "Corrupted"

    @property
    def purity_symbols(self) -> str:
        """Get visual purity indicators (diamonds)."""
        diamond_count = int(self.purity / 20)
        return "◊" * max(1, diamond_count)
