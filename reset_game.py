#!/usr/bin/env python3
"""
Simple script to reset the idle game progression by deleting the database.
"""

import os
import sys
from pathlib import Path

def reset_game():
    """Delete the game database to reset progression."""
    db_path = Path("data/game.db")
    
    if db_path.exists():
        try:
            # Ask for confirmation
            response = input("⚠️  This will delete all your game progress. Are you sure? (yes/no): ")
            if response.lower() in ['yes', 'y']:
                db_path.unlink()
                print("✅ Game reset successfully! Start fresh next time you play.")
            else:
                print("❌ Reset cancelled.")
        except Exception as e:
            print(f"Error resetting game: {e}")
            sys.exit(1)
    else:
        print("ℹ️  No save data found. Game is already fresh!")

if __name__ == "__main__":
    reset_game()