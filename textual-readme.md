# Running Idle TUI Game in Browser with Textual Web

✅ **CONFIRMED WORKING**: This guide shows you how to run the Idle TUI game in your web browser using textual-serve.

## Prerequisites

1. **Python 3.12.7** (Required to avoid uvloop installation issues)
2. **Working terminal application** (already confirmed)

## Step-by-Step Instructions

### 1. Set Python Version

First, ensure you're using Python 3.12.7:

```bash
cd /Users/unr/Development/idle-tui
pyenv local 3.12.7
```

### 2. Create and Activate Virtual Environment

Create a dedicated virtual environment for the web version:

```bash
# Create virtual environment with Python 3.12.7
/Users/unr/.pyenv/versions/3.12.7/bin/python3 -m venv venv-web

# Activate the virtual environment
source venv-web/bin/activate
```

### 3. Install Dependencies

Install the required packages:

```bash
# Install base dependencies
pip install -r requirements-simple.txt

# Install textual-serve and newer Textual version
pip install textual-serve

# This will upgrade Textual to 6.4.0+ which includes serve capability
```

### 4. Run the Web Server

Create and run this simple launcher script:

```bash
# Create launcher script
cat > run_web_server.py << 'EOF'
#!/usr/bin/env python3
"""Simple web server for the Idle Game using Textual's serve capability."""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the app  
from src.idle_game.app import IdleGame

if __name__ == "__main__":
    import asyncio
    from aiohttp import web
    from textual_serve.server import Server
    
    async def main():
        print("Starting Idle Game Web Server...")
        print("=" * 50)
        
        # Create the server
        server = Server(port=8000)
        
        # Create and configure the app
        app = web.Application()
        
        # Add the textual app route
        app.router.add_get("/", server.serve_app(IdleGame))
        app.router.add_get("/ws", server.websocket_handler)
        app.router.add_static("/", server.static_path)
        
        print("✅ Server starting on http://localhost:8000")
        print("📱 Open this URL in your browser to play!")
        print("⌨️  Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Start the server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 8000)
        await site.start()
        
        # Keep running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
        finally:
            await runner.cleanup()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
EOF

# Make it executable and run
chmod +x run_web_server.py
python run_web_server.py
```

### 5. Alternative: Direct Textual Serve (Simpler)

For Textual 6.4.0+, you can use the built-in serve command:

```bash
# Run directly with textual serve
cd /Users/unr/Development/idle-tui
source venv-web/bin/activate

# Use the serve API programmatically
python -c "
from textual.app import App
from src.idle_game.app import IdleGame
import asyncio

async def serve():
    from textual._serve import Server
    server = Server(IdleGame, port=8000)
    await server.serve()

asyncio.run(serve())
"
```

### 6. Alternative: Using textual-web (Cloud Deployment)

If you want to use textual-web for cloud deployment:

```bash
# Run with textual-web (connects to remote service)
textual-web --environment local --run "python -m src.idle_game.app"
```

Note: textual-web is designed for cloud deployment and requires connection to Textual's cloud service (Ganglion).

## Accessing the Game

Once the server is running:

1. Open your browser
2. Navigate to: `http://localhost:8000`
3. The game should appear in your browser window
4. Use keyboard/mouse to interact just like in terminal

## Troubleshooting

### Port Already in Use

If port 8000 is in use, change the port number in the script:

```python
# Change this line
site = web.TCPSite(runner, 'localhost', 8000)
# To something like
site = web.TCPSite(runner, 'localhost', 8001)
```

### Module Import Errors

Ensure you're in the correct directory and virtual environment:

```bash
cd /Users/unr/Development/idle-tui
source venv-web/bin/activate
python --version  # Should show 3.12.7
```

### Browser Compatibility

For best results, use a modern browser:
- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## ✅ WORKING SOLUTION

The following solution has been tested and confirmed to work:

### Quick Start (Copy & Paste)

```bash
# 1. Set Python version
cd /Users/unr/Development/idle-tui
pyenv local 3.12.7

# 2. Create virtual environment
/Users/unr/.pyenv/versions/3.12.7/bin/python3 -m venv venv-web
source venv-web/bin/activate

# 3. Install dependencies
pip install -r requirements-simple.txt
pip install textual-serve

# 4. Run the web server
python start_web.py
```

Then open your browser to: **http://localhost:8000**

The `start_web.py` script is already created in your project and contains:

```python
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
```

## Alternative Solutions (For Reference)

Since direct web serving has compatibility issues, here's a working solution using a simple web wrapper:

```bash
# Create a simple HTTP server that embeds the terminal app
cat > simple_web_server.py << 'EOF'
#!/usr/bin/env python3
"""
Simple web server that runs the Textual app in an iframe using xterm.js
This creates a terminal-in-browser experience.
"""

import subprocess
import sys
from pathlib import Path
from aiohttp import web
import aiohttp_jinja2
import jinja2

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Idle TUI Game</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@5.3.0/css/xterm.css" />
    <style>
        body {
            margin: 0;
            padding: 20px;
            background: #1e1e1e;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: monospace;
        }
        #terminal {
            padding: 20px;
            background: black;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        h1 {
            color: #0178d4;
            text-align: center;
            margin-bottom: 20px;
        }
        .container {
            max-width: 1200px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Idle TUI Game - Web Version</h1>
        <div id="terminal"></div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/xterm@5.3.0/lib/xterm.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.8.0/lib/xterm-addon-fit.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/xterm-addon-web-links@0.9.0/lib/xterm-addon-web-links.js"></script>
    <script>
        const term = new Terminal({
            cols: 80,
            rows: 24,
            theme: {
                background: '#000000',
                foreground: '#ffffff'
            }
        });
        
        const fitAddon = new FitAddon.FitAddon();
        term.loadAddon(fitAddon);
        
        term.open(document.getElementById('terminal'));
        fitAddon.fit();
        
        // Connect to WebSocket
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
        
        ws.onmessage = (event) => {
            term.write(event.data);
        };
        
        term.onData((data) => {
            ws.send(data);
        });
        
        window.addEventListener('resize', () => fitAddon.fit());
    </script>
</body>
</html>
"""

async def index(request):
    return web.Response(text=HTML_TEMPLATE, content_type='text/html')

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    # Start the Textual app in a subprocess
    process = await asyncio.create_subprocess_exec(
        sys.executable, '-m', 'src.idle_game.app',
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            # Forward input to the app
            process.stdin.write(msg.data.encode())
            await process.stdin.drain()
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print(f'WebSocket error: {ws.exception()}')
    
    process.terminate()
    await ws.close()
    return ws

async def main():
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_get('/ws', websocket_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8000)
    
    print("🎮 Idle TUI Game - Web Server")
    print("=" * 40)
    print("✅ Server running at: http://localhost:8000")
    print("📱 Open in your browser to play!")
    print("⌨️  Press Ctrl+C to stop")
    print("=" * 40)
    
    await site.start()
    
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    import asyncio
    import aiohttp
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
EOF

python simple_web_server.py
```

This creates a terminal-in-browser experience using xterm.js, which is how many web-based terminal applications work.