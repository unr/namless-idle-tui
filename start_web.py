#!/usr/bin/env python3
"""
Start the Idle Game in a web browser using textual-serve.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path so imports work
sys.path.insert(0, str(Path(__file__).parent))

# Import textual-serve components  
from textual_serve.server import Server

if __name__ == "__main__":
    print("🎮 Starting Idle TUI Game Web Server")
    print("=" * 50)
    print("📱 Server will start on: http://localhost:8000")
    print("⌨️  Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Create and run the server
    # The Server takes a command string that will be executed
    server = Server(
        command="python -m src.idle_game.app",
        port=8000,
        host="localhost",
        title="Idle TUI Game"
    )
    
    try:
        server.serve()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTry running with:")
        print("  python -m src.idle_game.app  # For terminal version")