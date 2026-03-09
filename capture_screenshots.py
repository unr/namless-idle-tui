"""Script to capture screenshots of the game at different progression stages."""

import time
from textual.pilot import Pilot
from src.idle_game.app import IdleGameApp

async def capture_screenshots():
    """Run the game and capture screenshots at key moments."""
    app = IdleGameApp()

    async with app.run_test() as pilot:
        # Screenshot 1: Initial game state
        await pilot.pause(0.5)
        app.save_screenshot("docs/screenshots/01_initial_game.svg")
        print("✓ Captured: Initial game state")

        # Click the harvest button 15 times to get 75 smiles
        for _ in range(15):
            await pilot.click("#harvest_btn")
            await pilot.pause(0.05)

        await pilot.pause(0.5)
        app.save_screenshot("docs/screenshots/02_after_clicking.svg")
        print("✓ Captured: After harvesting smiles")

        # Wait for tutorial customer to trigger (should happen at 10+ smiles)
        await pilot.pause(2.0)
        app.save_screenshot("docs/screenshots/03_tutorial_customer.svg")
        print("✓ Captured: Tutorial customer notification")

        # Let some time pass for passive production
        await pilot.pause(3.0)
        app.save_screenshot("docs/screenshots/04_passive_production.svg")
        print("✓ Captured: Passive production")

        # Open the shop screen
        await pilot.press("m")
        await pilot.pause(0.5)
        app.save_screenshot("docs/screenshots/05_shop_screen.svg")
        print("✓ Captured: Shop screen")

        # Go back to main game
        await pilot.press("escape")
        await pilot.pause(0.3)

        # Open prestige screen
        await pilot.press("r")
        await pilot.pause(0.5)
        app.save_screenshot("docs/screenshots/06_prestige_screen.svg")
        print("✓ Captured: Prestige screen")

        # Go back
        await pilot.press("escape")
        await pilot.pause(0.3)

        print("\n✅ All screenshots captured successfully!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(capture_screenshots())
