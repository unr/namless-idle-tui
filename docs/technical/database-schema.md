# Database Schema

## Current Implementation

### SQLite Database
- Location: `data/game.db`
- Single file, local storage
- Async access via aiosqlite
- Auto-created on first run

### Current Schema

```sql
CREATE TABLE game_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    counter TEXT NOT NULL,          -- Decimal as string
    click_power TEXT NOT NULL,      -- Decimal as string  
    auto_increment TEXT NOT NULL,   -- Decimal as string
    last_update TIMESTAMP NOT NULL,
    last_save TIMESTAMP NOT NULL
);
```

## Planned Schema Extensions

### Core Tables

```sql
-- Main game state (extended)
CREATE TABLE game_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    prestige_count INTEGER DEFAULT 0,
    emotional_depth TEXT DEFAULT '0',
    ethical_score REAL DEFAULT 50.0,
    shop_reputation REAL DEFAULT 3.0,
    total_customers_served INTEGER DEFAULT 0,
    game_phase TEXT DEFAULT 'tutorial',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_update TIMESTAMP NOT NULL,
    last_save TIMESTAMP NOT NULL
);

-- Emotion resources
CREATE TABLE emotions (
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL UNIQUE,     -- 'smiles', 'joy', 'sadness', etc
    amount TEXT NOT NULL,           -- Decimal as string
    storage_current INTEGER,
    storage_max INTEGER,
    purity REAL DEFAULT 100.0,      -- 0-100 percentage
    unlocked BOOLEAN DEFAULT FALSE,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Production buildings
CREATE TABLE buildings (
    id INTEGER PRIMARY KEY,
    emotion_type TEXT NOT NULL,
    tier INTEGER NOT NULL,
    count INTEGER DEFAULT 0,
    base_cost TEXT NOT NULL,
    production_rate TEXT NOT NULL,
    UNIQUE(emotion_type, tier)
);

-- Customer records
CREATE TABLE customers (
    id TEXT PRIMARY KEY,            -- UUID
    name TEXT NOT NULL,
    visits INTEGER DEFAULT 1,
    total_spent TEXT DEFAULT '0',
    satisfaction_avg REAL,
    dependency_level REAL DEFAULT 0.0,
    story_arc_id TEXT,
    last_visit TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Individual transactions
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT NOT NULL,
    emotion_sold TEXT NOT NULL,
    amount_sold TEXT NOT NULL,
    price_paid TEXT NOT NULL,
    purity_sold REAL,
    satisfaction REAL,
    ethical_impact INTEGER,        -- -100 to +100
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Recipe discoveries
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    ingredients JSON NOT NULL,      -- {emotion: percentage}
    output_emotion TEXT NOT NULL,
    output_amount TEXT NOT NULL,
    discovered BOOLEAN DEFAULT FALSE,
    times_crafted INTEGER DEFAULT 0,
    best_purity REAL DEFAULT 0.0,
    discovered_at TIMESTAMP
);

-- Story progression
CREATE TABLE story_arcs (
    id TEXT PRIMARY KEY,
    customer_id TEXT,
    arc_type TEXT NOT NULL,
    current_stage INTEGER DEFAULT 1,
    total_stages INTEGER,
    choices_made JSON,              -- Array of choice ids
    completed BOOLEAN DEFAULT FALSE,
    outcome TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Meta progression
CREATE TABLE unlocks (
    id INTEGER PRIMARY KEY,
    unlock_type TEXT NOT NULL,      -- 'emotion', 'recipe', 'feature'
    unlock_id TEXT NOT NULL,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    prestige_level INTEGER,
    UNIQUE(unlock_type, unlock_id)
);

-- Settings
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Data Models (Python)

```python
@dataclass
class EmotionData:
    type: str
    amount: Decimal
    storage_current: int
    storage_max: int
    purity: float
    unlocked: bool
    
@dataclass  
class CustomerData:
    id: str
    name: str
    visits: int
    total_spent: Decimal
    satisfaction_avg: float
    dependency_level: float
    story_arc_id: Optional[str]
    
@dataclass
class RecipeData:
    name: str
    ingredients: Dict[str, float]
    output_emotion: str
    output_amount: Decimal
    discovered: bool
    times_crafted: int
    best_purity: float
```

## Migration Strategy

### Version Management
```sql
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Migration Files
```
migrations/
├── 001_initial_schema.sql
├── 002_add_emotions_table.sql
├── 003_add_customers_table.sql
├── 004_add_recipes_table.sql
└── 005_add_prestige_fields.sql
```

### Migration Code
```python
async def migrate_database(db_path: str):
    current_version = await get_schema_version()
    migrations = get_pending_migrations(current_version)
    
    for migration in migrations:
        await execute_migration(migration)
        await update_schema_version(migration.version)
```

## Save File Format

### JSON Export Structure
```json
{
    "version": "1.0.0",
    "timestamp": "2024-01-01T00:00:00Z",
    "game_state": {
        "prestige_count": 0,
        "emotional_depth": "0",
        "ethical_score": 50.0
    },
    "emotions": [
        {
            "type": "smiles",
            "amount": "12345",
            "purity": 87.5
        }
    ],
    "customers": [],
    "recipes": [],
    "settings": {}
}
```

## Performance Optimizations

### Indexes
```sql
CREATE INDEX idx_customers_last_visit ON customers(last_visit);
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX idx_emotions_type ON emotions(type);
CREATE INDEX idx_recipes_discovered ON recipes(discovered);
```

### Query Optimization
- Batch inserts for transactions
- Prepared statements for frequent queries
- Connection pooling (future web version)
- WAL mode for concurrent access

### Data Cleanup
```sql
-- Archive old transactions (>30 days)
INSERT INTO transactions_archive 
SELECT * FROM transactions 
WHERE timestamp < datetime('now', '-30 days');

DELETE FROM transactions 
WHERE timestamp < datetime('now', '-30 days');
```

## Backup Strategy

### Auto-Backup
```python
async def auto_backup():
    # Every hour of gameplay
    if time_played % 3600 == 0:
        backup_path = f"data/backups/game_{timestamp}.db"
        await copy_database(current_db, backup_path)
        
    # Keep only last 10 backups
    await cleanup_old_backups(keep=10)
```

### Manual Backup
```bash
# Create backup
cp data/game.db data/game_backup_$(date +%Y%m%d_%H%M%S).db

# Restore backup
cp data/game_backup_20240101_120000.db data/game.db
```

## Future: Web Sync

### Cloud Save Schema
```sql
CREATE TABLE cloud_saves (
    user_id TEXT NOT NULL,
    save_id TEXT PRIMARY KEY,
    save_data JSON NOT NULL,
    platform TEXT NOT NULL,        -- 'web', 'terminal'
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_user_saves (user_id, updated_at)
);
```

### Sync Strategy
1. Local changes tracked with timestamps
2. Merge conflicts resolved by newest
3. Full sync on login
4. Delta sync during play
5. Offline queue for failed syncs

## Security Considerations

### Data Validation
- Decimal strings validated before storage
- JSON fields sanitized
- SQL injection prevention via parameters
- File permissions restricted

### Encryption (Future)
```python
# For sensitive data (if added)
encrypted_data = encrypt(json.dumps(data), user_key)
store_encrypted(encrypted_data)
```

### Anti-Cheat (Web Version)
- Server-side validation
- Rate limiting
- Anomaly detection
- Hash verification of game state
