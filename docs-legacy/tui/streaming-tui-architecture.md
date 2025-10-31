# Streaming TUI Apps to Web: Architecture Guide

## Your Use Case

**Goal:** Each authenticated user visits website → launches their own isolated TUI game instance → streams back to their browser

This is actually a **very viable and performant architecture** for your incremental/idle game! Here's everything you need to know.

---

## ✅ YES, This Is Cheap & Performant

### Why This Works Well

1. **TUI apps are lightweight** - Text-based interfaces use minimal bandwidth (~1-10KB/s per user)
2. **Idle games are low-frequency** - Most updates are timers/counters, not high-speed action
3. **Server resources are predictable** - Each TUI process uses ~5-50MB RAM
4. **Horizontal scaling is simple** - Add more servers as users grow

### Cost Estimation (AWS/DigitalOcean)

| Concurrent Users | Server Specs | Monthly Cost | Per-User Cost |
|------------------|--------------|--------------|---------------|
| 10 users | 1GB RAM VPS | $6/mo | $0.60/user |
| 50 users | 2GB RAM VPS | $12/mo | $0.24/user |
| 200 users | 4GB RAM VPS | $24/mo | $0.12/user |
| 1000 users | 3x 8GB RAM | $150/mo | $0.15/user |

**Extremely cheap** - You can run hundreds of concurrent players on a single cheap VPS.

---

## 🏗️ Architecture Options

### Option 1: GoTTY/ttyd + Process Spawning (RECOMMENDED)

**How it works:**
```
User visits game.com
    ↓
Nginx reverse proxy authenticates user
    ↓
Spawns: ttyd --port RANDOM --once /path/to/your-tui-game --user-id USER_ID
    ↓
Nginx forwards WebSocket to ttyd instance
    ↓
Browser displays terminal via xterm.js
```

**Tech Stack:**
- **ttyd** or **GoTTY** - Terminal to WebSocket bridge (10k+ stars, battle-tested)
- **xterm.js** - Browser terminal renderer (used by VS Code, Jupyter, etc.)
- **Nginx** - Reverse proxy for auth + routing
- **Systemd/Supervisor** - Process manager to spawn/clean up instances

**Code Example:**

```go
// Simple Go server that spawns ttyd per user
package main

import (
    "fmt"
    "net/http"
    "os/exec"
    "sync"
)

type GameServer struct {
    sessions map[string]*exec.Cmd
    mu       sync.Mutex
}

func (gs *GameServer) LaunchGame(w http.ResponseWriter, r *http.Request) {
    userID := r.Header.Get("X-User-ID") // From auth middleware
    
    gs.mu.Lock()
    defer gs.mu.Unlock()
    
    // Check if user already has session
    if _, exists := gs.sessions[userID]; exists {
        http.Redirect(w, r, "/game/"+userID, http.StatusFound)
        return
    }
    
    // Generate random port for this user's game
    port := generatePort()
    
    // Spawn ttyd with user's game instance
    cmd := exec.Command("ttyd",
        "--port", port,
        "--once",                    // Exit after one client disconnects
        "--credential", "user:pass", // Or use auth header
        "./idle-game",               // Your TUI game binary
        "--user-id", userID,         // Pass user ID to game
    )
    
    if err := cmd.Start(); err != nil {
        http.Error(w, "Failed to start game", 500)
        return
    }
    
    gs.sessions[userID] = cmd
    
    // Wait for game to start, then redirect
    time.Sleep(500 * time.Millisecond)
    http.Redirect(w, r, fmt.Sprintf("http://localhost:%s", port), http.StatusFound)
}
```

**Pros:**
- ✅ **Mature & stable** - ttyd has 10k+ stars, used in production
- ✅ **Language agnostic** - Works with ANY TUI app (Rust, Go, Python, C++)
- ✅ **Built-in features** - SSL, auth, reconnection, file upload, etc.
- ✅ **Minimal code** - Your game doesn't need to know about WebSockets
- ✅ **Perfect isolation** - Each user gets their own OS process

**Cons:**
- ⚠️ Each user = 1 process (~20-50MB RAM overhead from ttyd + your app)
- ⚠️ Port management required (though can use Unix sockets)

---

### Option 2: Custom WebSocket Server with PTY

**How it works:**
```
User visits game.com
    ↓
WebSocket connection to your server
    ↓
Server spawns: ptyProcess = spawn("your-game", ["--user", userId])
    ↓
Pipe: PTY ↔ WebSocket ↔ Browser (xterm.js)
```

**Tech Stack:**
- **node-pty** (Node.js) or **pty** (Go) - Create pseudo-terminals
- **gorilla/websocket** (Go) or **ws** (Node) - WebSocket server
- **xterm.js** - Browser renderer

**Code Example (Go):**

```go
package main

import (
    "github.com/creack/pty"
    "github.com/gorilla/websocket"
    "net/http"
    "os/exec"
)

var upgrader = websocket.Upgrader{
    CheckOrigin: func(r *http.Request) bool { return true },
}

func gameHandler(w http.ResponseWriter, r *http.Request) {
    // Upgrade HTTP to WebSocket
    conn, _ := upgrader.Upgrade(w, r, nil)
    defer conn.Close()
    
    // Get user from auth middleware
    userID := r.Context().Value("user_id").(string)
    
    // Spawn TUI game in PTY
    cmd := exec.Command("./idle-game", "--user", userID)
    ptmx, _ := pty.Start(cmd)
    defer ptmx.Close()
    
    // Goroutine: PTY → WebSocket
    go func() {
        buf := make([]byte, 1024)
        for {
            n, _ := ptmx.Read(buf)
            conn.WriteMessage(websocket.BinaryMessage, buf[:n])
        }
    }()
    
    // Main loop: WebSocket → PTY
    for {
        _, msg, _ := conn.ReadMessage()
        ptmx.Write(msg)
    }
}
```

**Pros:**
- ✅ **Full control** - Customize everything (auth, rate limiting, metrics)
- ✅ **Lower overhead** - No extra ttyd process
- ✅ **Easier scaling** - One server handles many WebSockets

**Cons:**
- ⚠️ **More code to maintain** - You handle reconnection, resizing, etc.
- ⚠️ **No built-in features** - SSL, auth, file transfer all DIY

---

### Option 3: Container Per User (Overkill for Your Use Case)

**Architecture:**
```
User → API Server → Docker/K8s spawns container → ttyd in container → User's browser
```

**Pros:**
- ✅ Maximum isolation
- ✅ Easy resource limits

**Cons:**
- ❌ **Expensive** - Containers add overhead (~100-200MB per user)
- ❌ **Slower startup** - 2-5 seconds vs instant for processes
- ❌ **Complex infrastructure** - Need orchestration

**Verdict:** NOT recommended for idle game. Only useful if users can run arbitrary code.

---

## 🔥 Recommended Architecture for Your Idle Game

### Tech Stack

1. **Backend:** Go or Rust
2. **TUI Framework:** Ratatui (Rust) or Bubble Tea (Go)
3. **Terminal Streamer:** ttyd or custom Go WebSocket server
4. **Frontend:** xterm.js (just a `<div id="terminal"></div>`)
5. **Auth:** JWT tokens in cookies/headers
6. **Database:** PostgreSQL for save games
7. **Deployment:** Single VPS → scale to multiple behind load balancer

### Full Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser (User)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  xterm.js renders terminal                           │  │
│  │  WebSocket connection to game server                 │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ WebSocket (WSS)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Game Server (VPS)                          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Nginx (Reverse Proxy)                              │  │
│  │  - SSL Termination                                  │  │
│  │  - Rate Limiting                                    │  │
│  │  - Auth Check (JWT)                                 │  │
│  └───┬─────────────────────────────────────────────────┘  │
│      │                                                     │
│  ┌───▼──────────────────────────────────────────────────┐ │
│  │  Game Launcher Service (Go/Rust)                     │ │
│  │  - Spawn ttyd + TUI game per user                    │ │
│  │  - Manage user sessions                              │ │
│  │  - Clean up on disconnect                            │ │
│  └───┬──────────────────────────────────────────────────┘ │
│      │                                                     │
│  ┌───▼──────────────────────────────────────────────────┐ │
│  │  Per-User Game Instances                             │ │
│  │  [ttyd] → [idle-game --user alice]                   │ │
│  │  [ttyd] → [idle-game --user bob]                     │ │
│  │  [ttyd] → [idle-game --user charlie]                 │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  PostgreSQL (Game Saves)                             │ │
│  │  - User progress, resources, upgrades                │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 💰 Cost Analysis

### Bandwidth Costs

A TUI game typically sends:
- **Idle updates:** 100-500 bytes/second (timers, counters)
- **Menu navigation:** 1-2KB per screen change
- **Graphs/ASCII art:** 5-10KB for complex displays

**Estimated bandwidth per user:**
- Average: 2-5KB/s
- Peak: 10-20KB/s (menu navigation)
- **Per hour:** 7-18MB
- **Per month (active player, 50hrs):** 350-900MB

**For 100 concurrent users:**
- Bandwidth: 200-500KB/s = 1.5-4TB/month
- Cost: $0-40/mo (most VPS include 1-2TB free)

### Compute Costs

**Per TUI game instance:**
- RAM: 10-30MB (idle game is lightweight)
- CPU: 0.1-2% (mostly sleeping, updating once per second)

**Server capacity:**
- 2GB VPS: 50-100 concurrent users
- 4GB VPS: 100-200 concurrent users
- 8GB VPS: 200-500 concurrent users

**Example: 100 active players on 2GB VPS**
- Cost: $12-18/month
- Per-player cost: $0.12-0.18/month
- **Less than a penny per player per day!**

---

## 🚀 Implementation Plan

### Phase 1: MVP (Week 1-2)

1. Build TUI game with Ratatui/Bubble Tea
2. Test locally with ttyd: `ttyd ./your-game`
3. Create simple HTML page with xterm.js
4. Deploy to cheap VPS, test with friends

### Phase 2: Multi-User (Week 3-4)

1. Add user authentication (JWT)
2. Build game launcher service (spawn ttyd per user)
3. Add Nginx reverse proxy
4. Implement save game system (PostgreSQL)

### Phase 3: Production (Week 5+)

1. Add session management (reconnection, timeouts)
2. Monitoring & alerts (CPU, RAM, active users)
3. Auto-scaling script (spin up new VPS when >80% capacity)
4. Backup system for save games

---

## 📊 Real-World Examples

### Systems Using This Architecture

1. **CoderPad** - Streaming code execution terminals to browsers
2. **Replit** - 10M+ users, terminal in browser
3. **Katacoda** - Interactive terminal lessons
4. **Azure Cloud Shell** - Microsoft's web-based terminal

### Open Source Projects

- **ttyd:** 10k+ stars, production-ready
- **GoTTY:** 19k+ stars, Go-based alternative
- **xterm.js:** 15k+ stars, used by VS Code

---

## 🔐 Security Considerations

### Must-Haves

1. **Authentication:** JWT tokens, session cookies
2. **SSL/TLS:** Encrypt all WebSocket traffic
3. **Rate Limiting:** Prevent abuse (max 1 instance per user)
4. **Process Isolation:** Use Linux namespaces or containers
5. **Resource Limits:** `ulimit` to prevent runaway processes
6. **Timeouts:** Auto-kill idle sessions after 30min

### Example Security Config

```nginx
# Nginx config for secure game streaming
location /game {
    # Require authentication
    auth_request /auth;
    
    # Rate limiting
    limit_req zone=game_start burst=5;
    
    # WebSocket upgrade
    proxy_pass http://game_launcher:8080;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    
    # Timeouts
    proxy_read_timeout 1800s; # 30 minutes max
}
```

---

## 🎯 Performance Optimization Tips

### 1. Reduce Terminal Redraws

Only update portions of the screen that changed:

```rust
// Bad: Redraws entire screen every tick
terminal.draw(|f| render_entire_game(f))?;

// Good: Only redraw changed widgets
if resources_changed {
    terminal.draw(|f| render_resources(f))?;
}
```

### 2. Batch Updates

```rust
// Send updates once per second instead of every change
let mut dirty = false;
loop {
    if game.tick() {
        dirty = true;
    }
    if dirty && last_render.elapsed() > Duration::from_secs(1) {
        terminal.draw(|f| render(f))?;
        dirty = false;
    }
}
```

### 3. Use Efficient Data Structures

For big numbers in idle games:

```rust
use num_bigint::BigUint; // Rust
// or
import "math/big"         // Go
```

### 4. Compress WebSocket Messages

```javascript
// In xterm.js
term.options.experimentalCharAtlas = 'dynamic';
term.options.disableStdin = false;
```

---

## 📦 Complete Starter Code

### Minimal Go Server + ttyd

```go
package main

import (
    "fmt"
    "log"
    "net/http"
    "os/exec"
    "strconv"
    "sync"
)

var (
    sessions = make(map[string]int) // userID -> port
    mu       sync.Mutex
    nextPort = 8081
)

func main() {
    http.HandleFunc("/launch", launchGameHandler)
    http.HandleFunc("/", serveHTML)
    log.Fatal(http.ListenAndServe(":8080", nil))
}

func launchGameHandler(w http.ResponseWriter, r *http.Request) {
    userID := r.URL.Query().Get("user")
    if userID == "" {
        http.Error(w, "user required", 400)
        return
    }
    
    mu.Lock()
    port, exists := sessions[userID]
    if !exists {
        port = nextPort
        nextPort++
        
        // Spawn ttyd + your game
        go exec.Command("ttyd",
            "-p", strconv.Itoa(port),
            "-o", // Once (exit after disconnect)
            "./idle-game", "--user", userID,
        ).Run()
        
        sessions[userID] = port
    }
    mu.Unlock()
    
    // Redirect to ttyd
    http.Redirect(w, r, fmt.Sprintf("http://localhost:%d", port), 302)
}

func serveHTML(w http.ResponseWriter, r *http.Request) {
    fmt.Fprint(w, `<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@5/css/xterm.css"/>
    <script src="https://cdn.jsdelivr.net/npm/xterm@5/lib/xterm.js"></script>
</head>
<body>
    <h1>Idle Game</h1>
    <button onclick="launch()">Launch Game</button>
    <div id="terminal"></div>
    <script>
        function launch() {
            const user = prompt("Username:");
            window.location = "/launch?user=" + user;
        }
    </script>
</body>
</html>`)
}
```

---

## 🏁 Conclusion

**YES**, streaming TUI apps to users is:
- ✅ **Cheap** (~$0.10-0.20 per user per month)
- ✅ **Performant** (handles 100s of users per cheap VPS)
- ✅ **Battle-tested** (used by VS Code, Replit, Azure, etc.)
- ✅ **Simple** (ttyd + xterm.js = 90% done)

**For your incremental/idle game, this architecture is perfect.** You get:
- Real TUI experience with Ratatui/Bubble Tea
- Web accessibility for users
- Isolated instances per player
- Extremely low operating costs

### Next Step: **Build MVP with ttyd + your TUI game**

Start simple:
```bash
# 1. Build your TUI game
cargo build --release  # or: go build

# 2. Test with ttyd locally
ttyd ./target/release/your-game

# 3. Open browser to http://localhost:7681
# 4. See it work!
```

Then gradually add auth, multi-user, and save games.
