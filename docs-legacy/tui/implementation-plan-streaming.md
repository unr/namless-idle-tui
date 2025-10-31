# Streaming TUI Implementation Plan (ttyd + Ratatui)

## Project Overview
Build an incremental idle game with a TUI interface streamed to web browsers using ttyd and Ratatui (Rust).

## Core Requirements
- Load game with a counter starting at 0
- Counter increments over time (idle mechanic)
- Persist state between sessions
- Calculate offline progression when returning

## Architecture

```
Browser (xterm.js) ↔ WebSocket ↔ ttyd ↔ Ratatui Game (Rust)
                                            ↓
                                     SQLite/PostgreSQL
```

## Project Structure

```
idle-game-streaming/
├── game/                   # Rust TUI game
│   ├── src/
│   │   ├── main.rs        # Entry point & TUI setup
│   │   ├── game.rs        # Game logic & state
│   │   ├── ui.rs          # Ratatui UI components
│   │   ├── numbers.rs     # Big number handling
│   │   └── persistence.rs # Save/load system
│   └── Cargo.toml
├── server/                 # Go server for user management
│   ├── main.go            # ttyd spawner & auth
│   ├── sessions.go        # Session management
│   └── go.mod
├── web/                    # Frontend
│   ├── index.html         # xterm.js interface
│   └── static/
└── docker-compose.yml      # Development setup
```

## Phase 1: Core Game Engine (Week 1)

### 1.1 Setup Rust Project

```toml
# Cargo.toml
[package]
name = "idle-game"
version = "0.1.0"
edition = "2021"

[dependencies]
ratatui = "0.26"
crossterm = "0.27"
tokio = { version = "1", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
sqlx = { version = "0.7", features = ["runtime-tokio", "sqlite"] }
chrono = "0.4"
num-bigint = "0.4"
num-traits = "0.2"
num-format = "0.4"
rust_decimal = "1.33"
rust_decimal_macros = "1.33"
```

### 1.2 Big Number Implementation

```rust
// src/numbers.rs
use rust_decimal::prelude::*;
use rust_decimal_macros::dec;
use serde::{Serialize, Deserialize};
use std::fmt;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GameNumber {
    mantissa: Decimal,  // 1.234
    exponent: i32,      // 10^6
}

impl GameNumber {
    pub fn new(value: f64) -> Self {
        if value == 0.0 {
            return GameNumber { 
                mantissa: dec!(0), 
                exponent: 0 
            };
        }
        
        let exp = value.abs().log10().floor() as i32;
        let mant = value / 10f64.powi(exp);
        
        GameNumber {
            mantissa: Decimal::from_f64_retain(mant).unwrap_or(dec!(0)),
            exponent: exp,
        }
    }
    
    pub fn add(&self, other: &GameNumber) -> GameNumber {
        // Align exponents and add
        let exp_diff = self.exponent - other.exponent;
        if exp_diff.abs() > 15 {
            // One number is insignificant
            if self.exponent > other.exponent { 
                self.clone() 
            } else { 
                other.clone() 
            }
        } else {
            // Actual addition logic
            let aligned_mantissa = if exp_diff > 0 {
                self.mantissa + other.mantissa / Decimal::from(10_i32.pow(exp_diff as u32))
            } else {
                self.mantissa / Decimal::from(10_i32.pow((-exp_diff) as u32)) + other.mantissa
            };
            
            // Normalize
            GameNumber::normalize(aligned_mantissa, self.exponent.max(other.exponent))
        }
    }
    
    pub fn multiply_f64(&self, scalar: f64) -> GameNumber {
        let new_mantissa = self.mantissa * Decimal::from_f64_retain(scalar).unwrap_or(dec!(1));
        GameNumber::normalize(new_mantissa, self.exponent)
    }
    
    fn normalize(mut mantissa: Decimal, mut exponent: i32) -> GameNumber {
        while mantissa.abs() >= dec!(10) {
            mantissa /= dec!(10);
            exponent += 1;
        }
        while mantissa.abs() < dec!(1) && mantissa != dec!(0) {
            mantissa *= dec!(10);
            exponent -= 1;
        }
        GameNumber { mantissa, exponent }
    }
    
    pub fn format(&self) -> String {
        if self.exponent < 6 {
            // Show full number for small values
            let value = self.mantissa * Decimal::from(10_i32.pow(self.exponent as u32));
            format!("{:.2}", value)
        } else {
            // Scientific notation with suffixes
            let suffixes = vec![
                "", "K", "M", "B", "T", "Qa", "Qi", "Sx", "Sp", "Oc", "No", "Dc",
                "Ud", "Dd", "Td", "Qad", "Qid", "Sxd", "Spd", "Od", "Nd", "Vg"
            ];
            let suffix_index = (self.exponent / 3) as usize;
            if suffix_index < suffixes.len() {
                let adjusted_mantissa = self.mantissa * Decimal::from(10_i32.pow((self.exponent % 3) as u32));
                format!("{:.2}{}", adjusted_mantissa, suffixes[suffix_index])
            } else {
                format!("{:.2}e{}", self.mantissa, self.exponent)
            }
        }
    }
}
```

### 1.3 Game State & Logic

```rust
// src/game.rs
use crate::numbers::GameNumber;
use serde::{Serialize, Deserialize};
use chrono::{DateTime, Utc};
use std::time::Duration;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GameState {
    pub user_id: String,
    pub counter: GameNumber,
    pub rate_per_second: GameNumber,
    pub last_save: DateTime<Utc>,
    pub total_time_played: Duration,
    pub upgrades: Vec<Upgrade>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Upgrade {
    pub id: String,
    pub name: String,
    pub cost: GameNumber,
    pub effect: GameNumber,
    pub owned: u32,
}

impl GameState {
    pub fn new(user_id: String) -> Self {
        GameState {
            user_id,
            counter: GameNumber::new(0.0),
            rate_per_second: GameNumber::new(1.0),
            last_save: Utc::now(),
            total_time_played: Duration::from_secs(0),
            upgrades: Self::init_upgrades(),
        }
    }
    
    fn init_upgrades() -> Vec<Upgrade> {
        vec![
            Upgrade {
                id: "clicker".to_string(),
                name: "Auto Clicker".to_string(),
                cost: GameNumber::new(10.0),
                effect: GameNumber::new(1.0),
                owned: 0,
            },
            Upgrade {
                id: "multiplier".to_string(),
                name: "Multiplier".to_string(),
                cost: GameNumber::new(100.0),
                effect: GameNumber::new(2.0),
                owned: 0,
            },
        ]
    }
    
    pub fn calculate_offline_progress(&mut self) {
        let now = Utc::now();
        let elapsed = now.signed_duration_since(self.last_save);
        let seconds = elapsed.num_seconds() as f64;
        
        // Calculate offline earnings with diminishing returns
        let effective_seconds = seconds.min(3600.0 * 8.0); // Cap at 8 hours
        let offline_multiplier = 0.5; // 50% efficiency while offline
        
        let earnings = self.rate_per_second
            .multiply_f64(effective_seconds * offline_multiplier);
        
        self.counter = self.counter.add(&earnings);
        self.last_save = now;
    }
    
    pub fn tick(&mut self, delta_seconds: f64) {
        let earnings = self.rate_per_second.multiply_f64(delta_seconds);
        self.counter = self.counter.add(&earnings);
        self.total_time_played = self.total_time_played
            .saturating_add(Duration::from_secs_f64(delta_seconds));
    }
    
    pub fn buy_upgrade(&mut self, upgrade_id: &str) -> Result<(), String> {
        let upgrade_idx = self.upgrades
            .iter()
            .position(|u| u.id == upgrade_id)
            .ok_or("Upgrade not found")?;
        
        let upgrade = &self.upgrades[upgrade_idx];
        
        // Check affordability (simplified for now)
        // In production, implement GameNumber comparison
        
        // Apply purchase
        self.upgrades[upgrade_idx].owned += 1;
        
        // Recalculate rate
        self.recalculate_rate();
        
        Ok(())
    }
    
    fn recalculate_rate(&mut self) {
        let mut base_rate = GameNumber::new(1.0);
        
        for upgrade in &self.upgrades {
            let contribution = upgrade.effect
                .multiply_f64(upgrade.owned as f64);
            base_rate = base_rate.add(&contribution);
        }
        
        self.rate_per_second = base_rate;
    }
}
```

### 1.4 Persistence Layer

```rust
// src/persistence.rs
use sqlx::{SqlitePool, migrate::MigrateDatabase};
use crate::game::GameState;
use std::error::Error;

pub struct Persistence {
    pool: SqlitePool,
}

impl Persistence {
    pub async fn new(database_url: &str) -> Result<Self, Box<dyn Error>> {
        // Create database if it doesn't exist
        if !sqlx::Sqlite::database_exists(database_url).await? {
            sqlx::Sqlite::create_database(database_url).await?;
        }
        
        let pool = SqlitePool::connect(database_url).await?;
        
        // Run migrations
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS game_saves (
                user_id TEXT PRIMARY KEY,
                state_json TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            "#
        ).execute(&pool).await?;
        
        Ok(Persistence { pool })
    }
    
    pub async fn save(&self, state: &GameState) -> Result<(), Box<dyn Error>> {
        let json = serde_json::to_string(state)?;
        
        sqlx::query(
            r#"
            INSERT INTO game_saves (user_id, state_json, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET 
                state_json = excluded.state_json,
                updated_at = CURRENT_TIMESTAMP
            "#
        )
        .bind(&state.user_id)
        .bind(json)
        .execute(&self.pool)
        .await?;
        
        Ok(())
    }
    
    pub async fn load(&self, user_id: &str) -> Result<Option<GameState>, Box<dyn Error>> {
        let row: Option<(String,)> = sqlx::query_as(
            "SELECT state_json FROM game_saves WHERE user_id = ?"
        )
        .bind(user_id)
        .fetch_optional(&self.pool)
        .await?;
        
        match row {
            Some((json,)) => {
                let mut state: GameState = serde_json::from_str(&json)?;
                state.calculate_offline_progress();
                Ok(Some(state))
            }
            None => Ok(None)
        }
    }
}
```

### 1.5 TUI Implementation

```rust
// src/ui.rs
use ratatui::{
    layout::{Constraint, Direction, Layout, Rect},
    style::{Color, Modifier, Style},
    text::{Line, Span, Text},
    widgets::{Block, Borders, Gauge, List, ListItem, Paragraph},
    Frame,
};
use crate::game::GameState;

pub fn draw_ui(frame: &mut Frame, state: &GameState) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Min(3),     // Header
            Constraint::Min(5),     // Main counter
            Constraint::Min(3),     // Rate display
            Constraint::Min(10),    // Upgrades
            Constraint::Min(3),     // Stats
        ])
        .split(frame.size());
    
    // Header
    let header = Paragraph::new(format!("Idle Game - User: {}", state.user_id))
        .style(Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD))
        .block(Block::default().borders(Borders::ALL).title("Game"));
    frame.render_widget(header, chunks[0]);
    
    // Main Counter
    let counter_text = vec![
        Line::from(vec![
            Span::raw("Resources: "),
            Span::styled(
                state.counter.format(),
                Style::default()
                    .fg(Color::Yellow)
                    .add_modifier(Modifier::BOLD)
            ),
        ]),
    ];
    let counter = Paragraph::new(counter_text)
        .block(Block::default().borders(Borders::ALL).title("Counter"))
        .alignment(ratatui::layout::Alignment::Center);
    frame.render_widget(counter, chunks[1]);
    
    // Rate Display
    let rate_text = format!("{}/sec", state.rate_per_second.format());
    let rate = Paragraph::new(rate_text)
        .block(Block::default().borders(Borders::ALL).title("Production"))
        .alignment(ratatui::layout::Alignment::Center);
    frame.render_widget(rate, chunks[2]);
    
    // Upgrades List
    let upgrades: Vec<ListItem> = state
        .upgrades
        .iter()
        .map(|u| {
            let line = format!(
                "{} ({}x) - Cost: {} - +{}/s each",
                u.name,
                u.owned,
                u.cost.format(),
                u.effect.format()
            );
            ListItem::new(Line::from(line))
        })
        .collect();
    
    let upgrades_list = List::new(upgrades)
        .block(Block::default().borders(Borders::ALL).title("Upgrades [Press 1-9 to buy]"))
        .highlight_style(Style::default().add_modifier(Modifier::BOLD))
        .highlight_symbol(">> ");
    frame.render_widget(upgrades_list, chunks[3]);
    
    // Stats
    let stats = Paragraph::new(format!(
        "Time Played: {:02}:{:02}:{:02} | Autosave every 10s | Press 'q' to quit",
        state.total_time_played.as_secs() / 3600,
        (state.total_time_played.as_secs() % 3600) / 60,
        state.total_time_played.as_secs() % 60
    ))
    .block(Block::default().borders(Borders::ALL).title("Info"));
    frame.render_widget(stats, chunks[4]);
}
```

### 1.6 Main Application

```rust
// src/main.rs
mod game;
mod ui;
mod numbers;
mod persistence;

use std::{error::Error, time::{Duration, Instant}};
use crossterm::{
    event::{self, DisableMouseCapture, EnableMouseCapture, Event, KeyCode},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{backend::CrosstermBackend, Terminal};
use game::GameState;
use persistence::Persistence;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // Parse command line args
    let user_id = std::env::args()
        .nth(1)
        .unwrap_or_else(|| "default_user".to_string());
    
    // Initialize persistence
    let db_path = format!("sqlite:game_{}.db", user_id);
    let persistence = Persistence::new(&db_path).await?;
    
    // Load or create game state
    let mut game_state = persistence
        .load(&user_id)
        .await?
        .unwrap_or_else(|| GameState::new(user_id));
    
    // Setup terminal
    enable_raw_mode()?;
    let mut stdout = std::io::stdout();
    execute!(stdout, EnterAlternateScreen, EnableMouseCapture)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;
    
    // Game loop
    let mut last_tick = Instant::now();
    let mut last_save = Instant::now();
    let tick_rate = Duration::from_millis(100); // 10 FPS
    let save_interval = Duration::from_secs(10);
    
    loop {
        // Draw UI
        terminal.draw(|f| ui::draw_ui(f, &game_state))?;
        
        // Handle input with timeout
        if event::poll(tick_rate)? {
            if let Event::Key(key) = event::read()? {
                match key.code {
                    KeyCode::Char('q') => break,
                    KeyCode::Char('1') => {
                        let _ = game_state.buy_upgrade("clicker");
                    }
                    KeyCode::Char('2') => {
                        let _ = game_state.buy_upgrade("multiplier");
                    }
                    _ => {}
                }
            }
        }
        
        // Update game state
        let now = Instant::now();
        let delta = now.duration_since(last_tick).as_secs_f64();
        game_state.tick(delta);
        last_tick = now;
        
        // Autosave
        if now.duration_since(last_save) >= save_interval {
            persistence.save(&game_state).await?;
            last_save = now;
        }
    }
    
    // Cleanup
    persistence.save(&game_state).await?;
    disable_raw_mode()?;
    execute!(
        terminal.backend_mut(),
        LeaveAlternateScreen,
        DisableMouseCapture
    )?;
    terminal.show_cursor()?;
    
    Ok(())
}
```

## Phase 2: Server & Streaming (Week 2)

### 2.1 Go Server Implementation

```go
// server/main.go
package main

import (
    "database/sql"
    "fmt"
    "log"
    "net/http"
    "os"
    "os/exec"
    "sync"
    "time"
    
    _ "github.com/mattn/go-sqlite3"
    "github.com/gorilla/mux"
    "github.com/golang-jwt/jwt/v4"
)

type Server struct {
    db       *sql.DB
    sessions map[string]*Session
    mu       sync.RWMutex
    port     int
}

type Session struct {
    UserID    string
    Port      int
    Process   *exec.Cmd
    StartedAt time.Time
}

func main() {
    server := &Server{
        sessions: make(map[string]*Session),
        port:     9000,
    }
    
    // Initialize database
    db, err := sql.Open("sqlite3", "./users.db")
    if err != nil {
        log.Fatal(err)
    }
    server.db = db
    
    // Create users table
    _, err = db.Exec(`
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    `)
    if err != nil {
        log.Fatal(err)
    }
    
    // Setup routes
    router := mux.NewRouter()
    router.HandleFunc("/api/auth", server.handleAuth).Methods("POST")
    router.HandleFunc("/api/launch", server.handleLaunch).Methods("POST")
    router.HandleFunc("/api/status", server.handleStatus).Methods("GET")
    router.PathPrefix("/").Handler(http.FileServer(http.Dir("./web")))
    
    // Start cleanup goroutine
    go server.cleanupSessions()
    
    log.Println("Server starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", router))
}

func (s *Server) handleLaunch(w http.ResponseWriter, r *http.Request) {
    // Extract user from JWT
    userID := r.Context().Value("user_id").(string)
    
    s.mu.Lock()
    defer s.mu.Unlock()
    
    // Check if session exists
    if session, exists := s.sessions[userID]; exists {
        // Return existing session
        json.NewEncoder(w).Encode(map[string]interface{}{
            "port": session.Port,
            "url":  fmt.Sprintf("ws://localhost:%d", session.Port),
        })
        return
    }
    
    // Allocate new port
    port := s.port
    s.port++
    
    // Launch ttyd with game
    cmd := exec.Command("ttyd",
        "-p", fmt.Sprintf("%d", port),
        "-o", // Exit after disconnect
        "-t", "titleFixed=Idle Game",
        "./game/target/release/idle-game",
        userID, // Pass user ID as argument
    )
    
    if err := cmd.Start(); err != nil {
        http.Error(w, "Failed to launch game", 500)
        return
    }
    
    // Store session
    s.sessions[userID] = &Session{
        UserID:    userID,
        Port:      port,
        Process:   cmd,
        StartedAt: time.Now(),
    }
    
    // Wait for ttyd to start
    time.Sleep(500 * time.Millisecond)
    
    // Return connection info
    json.NewEncoder(w).Encode(map[string]interface{}{
        "port": port,
        "url":  fmt.Sprintf("ws://localhost:%d", port),
    })
}

func (s *Server) cleanupSessions() {
    ticker := time.NewTicker(30 * time.Second)
    for range ticker.C {
        s.mu.Lock()
        for userID, session := range s.sessions {
            // Check if process is still running
            if session.Process.ProcessState != nil && session.Process.ProcessState.Exited() {
                delete(s.sessions, userID)
                continue
            }
            
            // Kill sessions older than 30 minutes of inactivity
            if time.Since(session.StartedAt) > 30*time.Minute {
                session.Process.Process.Kill()
                delete(s.sessions, userID)
            }
        }
        s.mu.Unlock()
    }
}
```

### 2.2 Web Frontend

```html
<!-- web/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Idle Game</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@5/css/xterm.css">
    <style>
        body {
            background: #1e1e1e;
            color: #fff;
            font-family: monospace;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }
        
        #terminal-container {
            width: 80vw;
            height: 70vh;
            background: #000;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 0 20px rgba(0,255,0,0.3);
        }
        
        #controls {
            margin: 20px;
        }
        
        button {
            background: #00ff00;
            color: #000;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            border-radius: 3px;
            margin: 0 10px;
        }
        
        button:hover {
            background: #00cc00;
        }
        
        #status {
            margin-top: 10px;
            color: #00ff00;
        }
    </style>
</head>
<body>
    <h1>🎮 Idle Game Terminal</h1>
    
    <div id="controls">
        <button onclick="connect()">Launch Game</button>
        <button onclick="disconnect()">Disconnect</button>
        <button onclick="toggleFullscreen()">Fullscreen</button>
    </div>
    
    <div id="status">Status: Not connected</div>
    
    <div id="terminal-container"></div>
    
    <script src="https://cdn.jsdelivr.net/npm/xterm@5/lib/xterm.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/xterm-addon-web-links@0.8.0/lib/xterm-addon-web-links.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.7.0/lib/xterm-addon-fit.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/xterm-addon-attach@0.8.0/lib/xterm-addon-attach.js"></script>
    
    <script>
        let terminal;
        let socket;
        let attachAddon;
        
        async function connect() {
            // Get auth token
            const token = localStorage.getItem('auth_token') || 'demo_token';
            
            // Launch game on server
            const response = await fetch('/api/launch', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            // Initialize terminal if needed
            if (!terminal) {
                terminal = new Terminal({
                    cursorBlink: true,
                    fontSize: 14,
                    fontFamily: 'Cascadia Code, Menlo, monospace',
                    theme: {
                        background: '#000000',
                        foreground: '#00ff00',
                        cursor: '#00ff00',
                        selection: '#00ff00'
                    }
                });
                
                const fitAddon = new FitAddon.FitAddon();
                terminal.loadAddon(fitAddon);
                
                terminal.open(document.getElementById('terminal-container'));
                fitAddon.fit();
                
                window.addEventListener('resize', () => fitAddon.fit());
            }
            
            // Connect WebSocket
            socket = new WebSocket(data.url);
            
            socket.onopen = () => {
                document.getElementById('status').textContent = 'Status: Connected';
                
                // Attach terminal to WebSocket
                attachAddon = new AttachAddon.AttachAddon(socket);
                terminal.loadAddon(attachAddon);
            };
            
            socket.onclose = () => {
                document.getElementById('status').textContent = 'Status: Disconnected';
                if (attachAddon) {
                    attachAddon.dispose();
                }
            };
            
            socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                document.getElementById('status').textContent = 'Status: Connection error';
            };
        }
        
        function disconnect() {
            if (socket) {
                socket.close();
                socket = null;
            }
        }
        
        function toggleFullscreen() {
            const container = document.getElementById('terminal-container');
            if (!document.fullscreenElement) {
                container.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        }
        
        // Auto-connect on load
        window.addEventListener('load', () => {
            setTimeout(connect, 500);
        });
    </script>
</body>
</html>
```

## Phase 3: Production Deployment

### 3.1 Docker Configuration

```dockerfile
# Dockerfile.game
FROM rust:1.75 as builder
WORKDIR /app
COPY game/ .
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y \
    libsqlite3-0 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/target/release/idle-game /usr/local/bin/
CMD ["idle-game"]
```

```dockerfile
# Dockerfile.server
FROM golang:1.21 as builder
WORKDIR /app
COPY server/ .
RUN go build -o server

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y \
    ttyd \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/server /usr/local/bin/
COPY web/ /web/
CMD ["server"]
```

### 3.2 Nginx Configuration

```nginx
# nginx.conf
upstream game_server {
    server localhost:8080;
}

server {
    listen 80;
    server_name idlegame.com;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=game_launch:10m rate=1r/s;
    limit_conn_zone $binary_remote_addr zone=game_conn:10m;
    
    location / {
        proxy_pass http://game_server;
        proxy_http_version 1.1;
        
        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # Timeouts
        proxy_read_timeout 1800s;  # 30 minutes
        proxy_send_timeout 1800s;
    }
    
    location /api/launch {
        limit_req zone=game_launch burst=5;
        limit_conn game_conn 1;  # 1 connection per IP
        proxy_pass http://game_server;
    }
}
```

## Performance Optimizations

### Number Handling Best Practices

1. **Use Fixed-Point Arithmetic**: For numbers below 10^15, use i64/u64
2. **Switch to Scientific Notation**: Above 10^15, use mantissa+exponent
3. **Lazy Evaluation**: Only calculate what's visible on screen
4. **Batch Updates**: Group multiple operations before normalizing
5. **Cache Formatted Strings**: Don't reformat numbers every frame

### Rendering Optimizations

1. **Differential Updates**: Only redraw changed widgets
2. **Frame Rate Limiting**: 10 FPS is plenty for idle games
3. **Viewport Culling**: Don't render off-screen elements
4. **Text Caching**: Pre-render static text elements

### Network Optimizations

1. **Compression**: Enable WebSocket compression
2. **Batch Messages**: Send updates in chunks
3. **Delta Encoding**: Only send changes, not full state
4. **Reconnection**: Implement automatic reconnection with state sync

## Monitoring & Scaling

### Metrics to Track

- Active sessions per server
- Memory usage per session
- WebSocket bandwidth usage
- Session duration distribution
- Offline progression calculations

### Auto-Scaling Strategy

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: idle-game
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: game-server
        image: idlegame:latest
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: idle-game-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: idle-game
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 70
```

## Testing Strategy

1. **Unit Tests**: Game logic, number handling
2. **Integration Tests**: Save/load, offline progression
3. **Load Tests**: Simulate 100+ concurrent users
4. **Soak Tests**: Run for 24+ hours to check for memory leaks
5. **Chaos Tests**: Random disconnections, server restarts

## Security Considerations

1. **Input Validation**: Sanitize all user inputs
2. **Rate Limiting**: Prevent spam and abuse
3. **Resource Limits**: Cap CPU/memory per session
4. **Secure WebSockets**: Use WSS in production
5. **Session Timeout**: Auto-disconnect idle sessions

## Estimated Timeline

- **Week 1**: Core game mechanics, TUI, number system
- **Week 2**: Server, WebSocket streaming, persistence
- **Week 3**: Production deployment, monitoring
- **Week 4**: Performance optimization, scaling tests

## Cost Projection

For 1000 concurrent users:
- **Infrastructure**: $50-100/month (3-5 VPS instances)
- **Database**: $10/month (Managed PostgreSQL)
- **CDN/Bandwidth**: $20/month
- **Total**: ~$80-130/month ($0.08-0.13 per user)