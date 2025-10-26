from decimal import Decimal, getcontext
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

getcontext().prec = 50  # Precision for large numbers

@dataclass
class GameNumber:
    """Wrapper for Decimal to handle idle game numbers"""
    value: Decimal = field(default_factory=lambda: Decimal(0))
    
    def add(self, amount: Decimal) -> 'GameNumber':
        return GameNumber(self.value + amount)
    
    def multiply(self, factor: Decimal) -> 'GameNumber':
        return GameNumber(self.value * factor)
    
    def format(self) -> str:
        """Format for display with suffixes"""
        if self.value < 1000:
            return f"{self.value:.0f}"
        
        suffixes = ['', 'K', 'M', 'B', 'T', 'Qa', 'Qi', 'Sx', 'Sp', 'Oc', 'No', 'Dc']
        magnitude = 0
        num = float(self.value)
        
        while abs(num) >= 1000 and magnitude < len(suffixes) - 1:
            magnitude += 1
            num /= 1000.0
        
        return f"{num:.2f}{suffixes[magnitude]}"

@dataclass
class GameState:
    """Core game state"""
    counter: GameNumber = field(default_factory=GameNumber)
    click_power: GameNumber = field(default_factory=lambda: GameNumber(Decimal(10)))
    auto_increment: GameNumber = field(default_factory=lambda: GameNumber(Decimal(1)))
    last_update: datetime = field(default_factory=datetime.now)
    last_save: datetime = field(default_factory=datetime.now)
    
    def calculate_offline_earnings(self, seconds_offline: float) -> GameNumber:
        """Calculate earnings while game was closed"""
        return self.auto_increment.multiply(Decimal(str(seconds_offline)))
    
    def update(self, current_time: datetime) -> GameNumber:
        """Update state and return increment amount"""
        time_delta = (current_time - self.last_update).total_seconds()
        increment = self.auto_increment.multiply(Decimal(str(time_delta)))
        self.counter = self.counter.add(increment.value)
        self.last_update = current_time
        return increment
    
    def click(self) -> GameNumber:
        """Handle manual click"""
        self.counter = self.counter.add(self.click_power.value)
        return self.click_power