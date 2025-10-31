import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from src.idle_game.models import GameNumber, GameState


def test_game_number_formatting():
    assert GameNumber(Decimal("0")).format() == "0"
    assert GameNumber(Decimal("999")).format() == "999"
    assert GameNumber(Decimal("1000")).format() == "1.00K"
    assert GameNumber(Decimal("1500000")).format() == "1.50M"
    assert GameNumber(Decimal("1234567890")).format() == "1.23B"


def test_game_number_operations():
    num1 = GameNumber(Decimal("100"))
    num2 = num1.add(Decimal("50"))
    assert num2.value == Decimal("150")

    num3 = num1.multiply(Decimal("2.5"))
    assert num3.value == Decimal("250")


def test_offline_calculation():
    state = GameState(counter=GameNumber(Decimal("1000")), auto_increment=GameNumber(Decimal("5")))

    # Simulate 60 seconds offline
    earnings = state.calculate_offline_earnings(60)
    assert earnings.value == Decimal("300")  # 5 * 60


def test_click_mechanics():
    state = GameState(counter=GameNumber(Decimal("100")), click_power=GameNumber(Decimal("10")))

    increment = state.click()
    assert increment.value == Decimal("10")
    assert state.counter.value == Decimal("110")


def test_auto_update():
    state = GameState(counter=GameNumber(Decimal("100")), auto_increment=GameNumber(Decimal("2")))

    # Simulate 5 seconds passing
    future_time = state.last_update + timedelta(seconds=5)
    increment = state.update(future_time)

    assert increment.value == Decimal("10")  # 2 * 5
    assert state.counter.value == Decimal("110")
