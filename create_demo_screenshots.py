"""Create demo screenshots by progressing game state programmatically."""

from decimal import Decimal
from src.idle_game.models.game_state import GameState
from src.idle_game.engine.game_loop import GameLoop
from src.idle_game.app import IdleGameApp


async def create_screenshots():
    """Create screenshots at different game stages."""
    import asyncio

    # Screenshot 1: Fresh game start
    print("Creating screenshot 1: Fresh start...")
    app = IdleGameApp()
    async with app.run_test() as pilot:
        await pilot.pause(1.0)
        app.save_screenshot("docs/screenshots/01_game_start.svg")
    print("✓ Captured: Fresh game start")

    # Screenshot 2: After some clicking (mid-tutorial)
    print("\nCreating screenshot 2: After clicking...")
    app = IdleGameApp()
    # Manually advance game state
    for _ in range(20):
        app.game_state.perform_click()

    async with app.run_test() as pilot:
        await pilot.pause(1.0)
        app.save_screenshot("docs/screenshots/02_after_clicking.svg")
    print("✓ Captured: After clicking")

    # Screenshot 3: With Joy unlocked
    print("\nCreating screenshot 3: Joy unlocked...")
    app = IdleGameApp()
    # Set up game state with Joy unlocked
    for _ in range(3):
        app.game_state.perform_click()
    app.game_state.unlock_emotion("joy")
    app.game_state.get_resource("joy").amount = Decimal("25")
    app.game_state.get_resource("joy").producer_count = 1
    app.game_state.get_resource("smiles").amount = Decimal("150")

    async with app.run_test() as pilot:
        await pilot.pause(1.0)
        app.save_screenshot("docs/screenshots/03_joy_unlocked.svg")
    print("✓ Captured: Joy unlocked")

    # Screenshot 4: Shop screen
    print("\nCreating screenshot 4: Shop screen...")
    app = IdleGameApp()
    app.game_state.get_resource("smiles").amount = Decimal("500")
    app.game_state.get_resource("joy").amount = Decimal("100")

    async with app.run_test() as pilot:
        await pilot.pause(0.5)
        await pilot.press("m")  # Open shop
        await pilot.pause(1.0)
        app.save_screenshot("docs/screenshots/04_shop_screen.svg")
    print("✓ Captured: Shop screen")

    # Screenshot 5: Prestige screen
    print("\nCreating screenshot 5: Prestige screen...")
    app = IdleGameApp()
    app.game_state.get_resource("smiles").amount = Decimal("10000")
    app.game_state.customers_served = 15
    app.game_state.recipes_discovered = {"basic_joy", "pure_love", "calm_serenity"}
    app.game_state.ethical_score = Decimal("75.0")

    async with app.run_test() as pilot:
        await pilot.pause(0.5)
        await pilot.press("r")  # Open prestige
        await pilot.pause(1.0)
        app.save_screenshot("docs/screenshots/05_prestige_screen.svg")
    print("✓ Captured: Prestige screen")

    # Screenshot 6: Advanced game state
    print("\nCreating screenshot 6: Advanced gameplay...")
    app = IdleGameApp()
    app.game_state.unlock_emotion("joy")
    app.game_state.unlock_emotion("love")
    app.game_state.unlock_emotion("nostalgia")
    app.game_state.get_resource("smiles").amount = Decimal("5000")
    app.game_state.get_resource("smiles").producer_count = 0
    app.game_state.get_resource("joy").amount = Decimal("1200")
    app.game_state.get_resource("joy").producer_count = 3
    app.game_state.get_resource("love").amount = Decimal("45")
    app.game_state.get_resource("love").producer_count = 1
    app.game_state.total_clicks = 247
    app.game_state.customers_served = 8

    async with app.run_test() as pilot:
        await pilot.pause(1.0)
        app.save_screenshot("docs/screenshots/06_advanced_gameplay.svg")
    print("✓ Captured: Advanced gameplay")

    print("\n✅ All screenshots created successfully!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(create_screenshots())
