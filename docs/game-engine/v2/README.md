# Game Engine v2: Sprite Animation Systems

## Overview

This documentation covers three strategies for implementing **animated sprite rendering** in your Textual-based incremental game. Unlike v1 (focused on 60fps text rendering), v2 focuses on **sprite-based animations** with support for both ASCII art and pixel art (Unicode blocks).

## Key Differences from v1

| Aspect | v1 (Text-focused) | v2 (Sprite-focused) |
|--------|-------------------|---------------------|
| **Primary Goal** | 60fps text/numbers | Animated sprites |
| **Content Type** | Floating text | Pixel/ASCII art |
| **FPS Target** | 60fps required | 10-30fps sufficient |
| **Animation** | Physics-based motion | Frame-based sprites |
| **Complexity** | Performance-critical | Content-creation focused |

## The Three Strategies

### Strategy 1: Sprite Sheet Animation System ⭐ RECOMMENDED

Frame-based sprite animations using sprite sheets. Like classic 8-bit games in your terminal.

**Best for:** 
- Retro-style incremental games
- Clear, readable sprite animations
- Quick content creation

**Implementation time:** 2-3 days

[Read full documentation →](./strategy1-sprite-sheets/README.md)

---

### Strategy 2: Layered Composition System

Multiple rendering layers with state-based animations and blending.

**Best for:**
- Complex scenes with depth
- Parallax scrolling
- Particle effects overlays

**Implementation time:** 3-4 days

[Read full documentation →](./strategy2-layered-composition/README.md)

---

### Strategy 3: Entity-Component Animation System

Professional ECS architecture with animation components and state machines.

**Best for:**
- Complex game mechanics
- Reusable animation system
- Long-term scalability

**Implementation time:** 5-7 days

[Read full documentation →](./strategy3-entity-component/README.md)

## Quick Comparison

| Criteria | Strategy 1 | Strategy 2 | Strategy 3 |
|----------|-----------|-----------|-----------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Animation Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Content Creation** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Flexibility** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Learning Curve** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |

[See detailed comparison →](./COMPARISON.md)

## Example Sprite Animations

### ASCII Art Sprite (Strategy 1)
```
Coin spinning animation:
Frame 1: O
Frame 2: ()
Frame 3: ||
Frame 4: ()
Frame 5: O
```

### Pixel Art Sprite (Unicode Blocks)
```
Character idle:
  ▄█▄
  █▀█
  ▀ ▀

Character walking:
  ▄█▄     ▄█▄
  █▀█  →  █▀█
 ▀  ▀     ▀▀
```

### Multi-layer Scene (Strategy 2)
```
Layer 3 (UI):     [❤❤❤] [💰 1.2K]
Layer 2 (Sprite):      🧙 (animated mage)
Layer 1 (Effect):     ✨ (sparkles)
Layer 0 (BG):     ▓▓▓▓▓▓▓ (dungeon wall)
```

## Recommended Workflow

### Phase 1: Choose Your Strategy
1. Read [COMPARISON.md](./COMPARISON.md)
2. Consider your art style (ASCII vs pixel art)
3. Evaluate complexity needs
4. Pick Strategy 1 for most cases

### Phase 2: Design Sprites
1. Define what sprites you need (character, items, effects)
2. Choose ASCII or Unicode block style
3. Create sprite sheets (use tools or hand-draw)
4. Plan animation cycles (idle, action, special)

### Phase 3: Implement System
1. Follow the implementation guide for your chosen strategy
2. Start with static sprites first
3. Add animation frame cycling
4. Integrate with game state
5. Test and polish

### Phase 4: Create Content
1. Build sprite library
2. Create animation variations
3. Add particle effects
4. Polish timing and transitions

## Sprite Creation Tools

### ASCII Art Tools
- **Text editors** - VS Code, Vim (simple drawings)
- **ASCII Art Studio** - Desktop tool for complex art
- **asciiflow.com** - Web-based diagram/art tool
- **GIMP + aalib** - Convert images to ASCII

### Unicode Block Art
- **Playscii** - Dedicated pixel/ASCII art editor
- **Rex Paint** - Roguelike-focused ASCII editor
- **Custom Python scripts** - Convert images to blocks

## Art Styles Supported

### Pure ASCII (7-bit characters)
```
Character:     Tree:      Coin:
   O           ^_^         $
  /|\           |          
  / \          /|\         
```
**Pros:** Maximum compatibility, retro aesthetic  
**Cons:** Limited detail

### Extended ASCII (8-bit)
```
Character:     Castle:    Potion:
   ☺           ╔═╗         ▒
  ─┼─          ║ ║        ╱│╲
   ┴           ╚═╝         └┘
```
**Pros:** More symbols, box drawing  
**Cons:** Encoding issues

### Unicode Blocks (Pixel Art)
```
Character:     Tree:      Chest:
  ▄█▄         ▓▓▓        ╔═══╗
  █▀█          █         ║▓▓▓║
  ▀ ▀         ███        ╚═══╝
```
**Pros:** Rich detail, color support  
**Cons:** Requires Unicode support

### Unicode Emoji
```
Mage: 🧙  Coin: 💰  Fire: 🔥  Tree: 🌳
```
**Pros:** Colorful, expressive  
**Cons:** Terminal dependent, limited control

## Integration with Idle Game

All strategies integrate with your existing game state:

```python
class IdleGame(App):
    def compose(self) -> ComposeResult:
        with Horizontal():
            # 70% - Sprite canvas
            yield SpriteCanvas(self.game_state)
            
            # 30% - Actions panel
            yield ActionsPanel(self.game_state)
    
    def on_counter_increment(self, increment: GameNumber):
        """Trigger sprite animation."""
        canvas = self.query_one(SpriteCanvas)
        canvas.play_animation("coin_collect")
        canvas.spawn_sprite("floating_number", increment)
```

## Performance Considerations

### Frame Rate Guidelines
- **10 FPS** - Sufficient for idle animations
- **15 FPS** - Smooth for most sprite animations
- **30 FPS** - Very smooth, higher CPU usage

### Optimization Tips
1. Only animate visible sprites
2. Use sprite pooling for common animations
3. Cache rendered frames
4. Limit simultaneous animations to 20-30
5. Use dirty rectangle rendering

## File Organization

```
src/idle_game/
├── sprites/
│   ├── __init__.py
│   ├── sprite_sheet.py       # Load/manage sprite data
│   ├── animated_sprite.py    # Animation logic
│   ├── sprite_renderer.py    # Rendering to canvas
│   └── assets/
│       ├── characters/
│       │   ├── mage.txt      # Sprite definitions
│       │   └── knight.txt
│       ├── items/
│       │   ├── coin.txt
│       │   └── potion.txt
│       └── effects/
│           ├── sparkle.txt
│           └── smoke.txt
├── widgets/
│   ├── sprite_canvas.py      # Main game canvas
│   └── actions_panel.py      # Side panel
└── app.py
```

## Common Sprite Patterns

### Idle Animation
Character breathing or swaying (2-4 frames, slow cycle)

### Action Animation
Button press, item collect (4-8 frames, one-shot)

### Loop Animation
Environmental effects like fire, water (4-12 frames, continuous)

### State Transitions
Switching between idle/active states (smooth blending)

## Next Steps

1. ✅ Read [COMPARISON.md](./COMPARISON.md) for detailed analysis
2. ✅ Choose your strategy (recommend Strategy 1)
3. ✅ Read the strategy's README and implementation guide
4. ✅ Design your sprite assets
5. ✅ Implement the core sprite system
6. ✅ Create sprite content
7. ✅ Integrate with game mechanics
8. ✅ Polish and optimize

## Support

Each strategy folder contains:
- **README.md** - Architecture and design
- **implementation.md** - Step-by-step implementation guide
- **examples/** - Code examples and sprite assets
- **BEST_PRACTICES.md** - Tips and patterns

**Start here:** [COMPARISON.md](./COMPARISON.md) to choose your strategy.
