# Strategy 3: Entity-Component Animation System

## Overview

A professional Entity-Component-System (ECS) architecture where sprites, animations, physics, and rendering are all separate **components** attached to **entities**. This provides maximum flexibility and reusability at the cost of implementation complexity.

This is the most powerful but also most complex approach - only use if you need a full game engine architecture.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    IdleGame (App)                        │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Horizontal Container (70/30)               │ │
│  │  ┌──────────────────┐  ┌──────────────────────┐   │ │
│  │  │   ECSCanvas      │  │  ActionsPanel        │   │ │
│  │  │   (70% width)    │  │  (30% width)         │   │ │
│  │  │                  │  │                      │   │ │
│  │  │ ┌──────────────┐ │  │  - Stats             │   │ │
│  │  │ │    World     │ │  │  - Actions           │   │ │
│  │  │ │              │ │  │  - Upgrades          │   │ │
│  │  │ │  [Entities]  │ │  │                      │   │ │
│  │  │ │              │ │  │                      │   │ │
│  │  │ │  Entity 1:   │ │  │                      │   │ │
│  │  │ │  - Transform │ │  │                      │   │ │
│  │  │ │  - Animation │ │  │                      │   │ │
│  │  │ │  - Render    │ │  │                      │   │ │
│  │  │ │              │ │  │                      │   │ │
│  │  │ │  Entity 2:   │ │  │                      │   │ │
│  │  │ │  - Transform │ │  │                      │   │ │
│  │  │ │  - Animation │ │  │                      │   │ │
│  │  │ │  - Physics   │ │  │                      │   │ │
│  │  │ │  - Render    │ │  │                      │   │ │
│  │  │ └──────────────┘ │  │                      │   │ │
│  │  │                  │  │                      │   │ │
│  │  │  Systems:        │  │                      │   │ │
│  │  │  - AnimationSys  │  │                      │   │ │
│  │  │  - PhysicsSys    │  │                      │   │ │
│  │  │  - RenderSys     │  │                      │   │ │
│  │  └──────────────────┘  └──────────────────────┘   │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## Key Concepts

### 1. Entity

An entity is just an ID with attached components:

```python
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from uuid import uuid4

@dataclass
class Entity:
    """An entity is a container for components."""
    
    id: str = field(default_factory=lambda: str(uuid4()))
    components: Dict[str, Any] = field(default_factory=dict)
    tags: set[str] = field(default_factory=set)
    active: bool = True
    
    def add_component(self, component_type: str, component: Any) -> None:
        """Add a component to this entity."""
        self.components[component_type] = component
    
    def get_component(self, component_type: str) -> Optional[Any]:
        """Get a component from this entity."""
        return self.components.get(component_type)
    
    def has_component(self, component_type: str) -> bool:
        """Check if entity has a component."""
        return component_type in self.components
    
    def remove_component(self, component_type: str) -> None:
        """Remove a component from this entity."""
        if component_type in self.components:
            del self.components[component_type]
    
    def has_tag(self, tag: str) -> bool:
        """Check if entity has a tag."""
        return tag in self.tags
    
    def add_tag(self, tag: str) -> None:
        """Add tag to entity."""
        self.tags.add(tag)
```

### 2. Components

Components are pure data structures:

```python
from dataclasses import dataclass
from typing import List

@dataclass
class Transform:
    """Position and movement."""
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0  # For future use
    scale: float = 1.0     # For future use

@dataclass
class Animation:
    """Animation state and clips."""
    current_clip: str = "idle"
    clips: Dict[str, "AnimationClip"] = field(default_factory=dict)
    frame_index: int = 0
    time_accumulator: float = 0.0
    playing: bool = True
    loop: bool = True

@dataclass
class AnimationClip:
    """An animation clip with frames."""
    name: str
    frames: List[str]
    fps: int = 10
    loop: bool = True
    
    @property
    def frame_duration(self) -> float:
        return 1.0 / self.fps
    
    @property
    def frame_count(self) -> int:
        return len(self.frames)

@dataclass
class SpriteRenderer:
    """Rendering information."""
    visible: bool = True
    layer: int = 0  # Z-order
    opacity: float = 1.0

@dataclass
class Lifetime:
    """Auto-destroy after time."""
    duration: float
    elapsed: float = 0.0
    
    @property
    def is_expired(self) -> bool:
        return self.elapsed >= self.duration
    
    @property
    def progress(self) -> float:
        """0.0 to 1.0 progress through lifetime."""
        return min(self.elapsed / self.duration, 1.0)
```

### 3. Systems

Systems operate on entities with specific components:

```python
from typing import List
from abc import ABC, abstractmethod

class System(ABC):
    """Base class for systems."""
    
    @abstractmethod
    def update(self, entities: List[Entity], dt: float) -> None:
        """Update entities."""
        pass

class AnimationSystem(System):
    """Updates animation components."""
    
    def update(self, entities: List[Entity], dt: float) -> None:
        """Update all animation components."""
        for entity in entities:
            if not entity.active:
                continue
            
            anim = entity.get_component('animation')
            if not anim or not anim.playing:
                continue
            
            # Get current clip
            clip = anim.clips.get(anim.current_clip)
            if not clip:
                continue
            
            # Update frame
            anim.time_accumulator += dt
            
            while anim.time_accumulator >= clip.frame_duration:
                anim.time_accumulator -= clip.frame_duration
                anim.frame_index += 1
                
                # Handle loop/completion
                if anim.frame_index >= clip.frame_count:
                    if clip.loop:
                        anim.frame_index = 0
                    else:
                        anim.frame_index = clip.frame_count - 1
                        anim.playing = False

class RenderSystem(System):
    """Renders sprites to buffer."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.buffer = [[' ' for _ in range(width)] for _ in range(height)]
    
    def clear_buffer(self) -> None:
        """Clear render buffer."""
        for y in range(self.height):
            for x in range(self.width):
                self.buffer[y][x] = ' '
    
    def update(self, entities: List[Entity], dt: float) -> None:
        """Render all entities."""
        # Clear buffer
        self.clear_buffer()
        
        # Sort by layer
        visible_entities = [
            e for e in entities
            if e.active
            and e.has_component('transform')
            and e.has_component('animation')
            and e.has_component('renderer')
            and e.get_component('renderer').visible
        ]
        
        sorted_entities = sorted(
            visible_entities,
            key=lambda e: e.get_component('renderer').layer
        )
        
        # Render each entity
        for entity in sorted_entities:
            self._render_entity(entity)
    
    def _render_entity(self, entity: Entity) -> None:
        """Render single entity to buffer."""
        transform = entity.get_component('transform')
        anim = entity.get_component('animation')
        
        # Get current frame
        clip = anim.clips.get(anim.current_clip)
        if not clip:
            return
        
        frame = clip.frames[anim.frame_index]
        lines = frame.strip().split('\n')
        
        # Draw to buffer
        for y_off, line in enumerate(lines):
            y = int(transform.y) + y_off
            if not (0 <= y < self.height):
                continue
            
            for x_off, char in enumerate(line):
                x = int(transform.x) + x_off
                if not (0 <= x < self.width):
                    continue
                
                if char != ' ':
                    self.buffer[y][x] = char
    
    def get_line(self, y: int) -> str:
        """Get rendered line."""
        if 0 <= y < self.height:
            return ''.join(self.buffer[y])
        return ' ' * self.width

class LifetimeSystem(System):
    """Manages entity lifetimes."""
    
    def update(self, entities: List[Entity], dt: float) -> None:
        """Update lifetimes and mark expired entities."""
        for entity in entities:
            lifetime = entity.get_component('lifetime')
            if not lifetime:
                continue
            
            lifetime.elapsed += dt
            
            if lifetime.is_expired:
                entity.active = False
```

### 4. World

The world manages entities and systems:

```python
class World:
    """Manages entities and systems."""
    
    def __init__(self):
        self.entities: List[Entity] = []
        self.systems: List[System] = []
    
    def create_entity(self, tags: set[str] = None) -> Entity:
        """Create a new entity."""
        entity = Entity(tags=tags or set())
        self.entities.append(entity)
        return entity
    
    def destroy_entity(self, entity: Entity) -> None:
        """Remove an entity."""
        if entity in self.entities:
            self.entities.remove(entity)
    
    def add_system(self, system: System) -> None:
        """Add a system."""
        self.systems.append(system)
    
    def update(self, dt: float) -> None:
        """Update all systems."""
        # Update systems
        for system in self.systems:
            system.update(self.entities, dt)
        
        # Remove inactive entities
        self.entities = [e for e in self.entities if e.active]
    
    def get_entities_with_tag(self, tag: str) -> List[Entity]:
        """Get all entities with a tag."""
        return [e for e in self.entities if e.has_tag(tag)]
    
    def get_entities_with_component(self, component_type: str) -> List[Entity]:
        """Get all entities with a component."""
        return [e for e in self.entities if e.has_component(component_type)]
```

## ECS Canvas Widget

```python
from textual.widget import Widget
from textual.strip import Strip
from textual.segment import Segment

class ECSCanvas(Widget):
    """Canvas using Entity-Component-System."""
    
    DEFAULT_CSS = """
    ECSCanvas {
        width: 100%;
        height: 100%;
        background: $surface;
        border: solid $primary;
    }
    """
    
    def __init__(self, game_state, **kwargs):
        super().__init__(**kwargs)
        self.game_state = game_state
        self.world = None
        self.render_system = None
        self.update_rate = 15
    
    def on_mount(self) -> None:
        """Initialize ECS."""
        # Create world
        self.world = World()
        
        # Add systems
        self.world.add_system(AnimationSystem())
        self.world.add_system(LifetimeSystem())
        self.render_system = RenderSystem(self.size.width, self.size.height)
        self.world.add_system(self.render_system)
        
        # Create initial entities
        self.create_character()
        
        # Start update loop
        self.set_interval(1.0 / self.update_rate, self.update_world)
    
    def create_character(self) -> Entity:
        """Create player character entity."""
        entity = self.world.create_entity(tags={'player', 'character'})
        
        # Add components
        entity.add_component('transform', Transform(
            x=self.size.width // 2,
            y=self.size.height // 2
        ))
        
        # Create animation clips
        idle_clip = AnimationClip(
            name='idle',
            frames=CHARACTER_IDLE_FRAMES,
            fps=4,
            loop=True
        )
        
        animation = Animation()
        animation.clips['idle'] = idle_clip
        animation.current_clip = 'idle'
        entity.add_component('animation', animation)
        
        entity.add_component('renderer', SpriteRenderer(layer=10))
        
        return entity
    
    def create_effect(self, x: int, y: int, effect_type: str) -> Entity:
        """Create effect entity."""
        entity = self.world.create_entity(tags={'effect'})
        
        entity.add_component('transform', Transform(x=x, y=y))
        
        # Animation
        clip = AnimationClip(
            name=effect_type,
            frames=EFFECT_FRAMES[effect_type],
            fps=15,
            loop=False
        )
        animation = Animation(loop=False)
        animation.clips[effect_type] = clip
        animation.current_clip = effect_type
        entity.add_component('animation', animation)
        
        entity.add_component('renderer', SpriteRenderer(layer=20))
        entity.add_component('lifetime', Lifetime(duration=1.0))
        
        return entity
    
    def update_world(self) -> None:
        """Update ECS world."""
        dt = 1.0 / self.update_rate
        self.world.update(dt)
        self.refresh()
    
    def render_line(self, y: int) -> Strip:
        """Render line from ECS."""
        line = self.render_system.get_line(y)
        return Strip([Segment(line)], len(line))
```

## Example: Creating Entities

```python
# Create animated coin
coin = world.create_entity(tags={'collectible', 'coin'})
coin.add_component('transform', Transform(x=10, y=10))

coin_clip = AnimationClip('spin', COIN_FRAMES, fps=12, loop=False)
anim = Animation()
anim.clips['spin'] = coin_clip
anim.current_clip = 'spin'
coin.add_component('animation', anim)

coin.add_component('renderer', SpriteRenderer(layer=15))
coin.add_component('lifetime', Lifetime(duration=2.0))
```

## Pros and Cons

### Pros ✅
- Maximum flexibility and reusability
- Clean separation of concerns
- Easy to add new component types
- Systems are testable in isolation
- Scalable to complex games
- Industry-standard architecture
- Easy to extend with new behaviors

### Cons ❌
- Most complex to implement (5-7 days)
- Steeper learning curve
- More boilerplate code
- Can be overkill for simple games
- Harder to debug (data scattered across components)
- Performance overhead (component lookups)

## When to Use

Choose this strategy if:
- ✅ Building a complex game engine
- ✅ Need maximum flexibility
- ✅ Plan to extend system significantly
- ✅ Team has ECS experience
- ✅ Want professional architecture
- ✅ Need reusable components across many entity types

## Next Steps

See [implementation.md](./implementation.md) for step-by-step implementation guide.
See [examples/](./examples/) for working code samples.
