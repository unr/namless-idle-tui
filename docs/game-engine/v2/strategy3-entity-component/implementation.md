# Implementation Guide - Strategy 3: Entity-Component System

## Overview

Implementing a full ECS architecture. This is complex - only proceed if you need this level of flexibility. Time: 5-7 days.

## Phase 1: Core ECS (Day 1-3)

### Step 1: Entity and Components

```python
# src/idle_game/ecs/entity.py
from dataclasses import dataclass, field
from typing import Dict, Any, Set
from uuid import uuid4

@dataclass
class Entity:
    id: str = field(default_factory=lambda: str(uuid4()))
    components: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    active: bool = True
    
    def add(self, comp_type: str, comp: Any) -> None:
        self.components[comp_type] = comp
    
    def get(self, comp_type: str) -> Any:
        return self.components.get(comp_type)
    
    def has(self, comp_type: str) -> bool:
        return comp_type in self.components

# src/idle_game/ecs/components.py
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Transform:
    x: float = 0.0
    y: float = 0.0

@dataclass
class AnimationClip:
    name: str
    frames: List[str]
    fps: int = 10
    loop: bool = True

@dataclass
class Animation:
    clips: Dict[str, AnimationClip] = field(default_factory=dict)
    current: str = "idle"
    frame: int = 0
    time: float = 0.0
    playing: bool = True

@dataclass
class Renderer:
    visible: bool = True
    layer: int = 0

@dataclass
class Lifetime:
    duration: float
    elapsed: float = 0.0
```

### Step 2: Systems

```python
# src/idle_game/ecs/systems.py
from typing import List
from abc import ABC, abstractmethod

class System(ABC):
    @abstractmethod
    def update(self, entities: List, dt: float) -> None:
        pass

class AnimationSystem(System):
    def update(self, entities: List, dt: float) -> None:
        for e in entities:
            anim = e.get('animation')
            if not anim or not anim.playing:
                continue
            
            clip = anim.clips.get(anim.current)
            if not clip:
                continue
            
            anim.time += dt
            frame_dur = 1.0 / clip.fps
            
            while anim.time >= frame_dur:
                anim.time -= frame_dur
                anim.frame += 1
                
                if anim.frame >= len(clip.frames):
                    if clip.loop:
                        anim.frame = 0
                    else:
                        anim.frame = len(clip.frames) - 1
                        anim.playing = False

class RenderSystem(System):
    def __init__(self, w: int, h: int):
        self.w = w
        self.h = h
        self.buf = [[' '] * w for _ in range(h)]
    
    def update(self, entities: List, dt: float) -> None:
        # Clear
        for y in range(self.h):
            for x in range(self.w):
                self.buf[y][x] = ' '
        
        # Sort by layer
        renderable = [
            e for e in entities
            if e.active
            and e.has('transform')
            and e.has('animation')
            and e.has('renderer')
            and e.get('renderer').visible
        ]
        
        sorted_ent = sorted(
            renderable,
            key=lambda e: e.get('renderer').layer
        )
        
        # Render
        for e in sorted_ent:
            self._draw(e)
    
    def _draw(self, e) -> None:
        t = e.get('transform')
        a = e.get('animation')
        
        clip = a.clips.get(a.current)
        if not clip:
            return
        
        frame = clip.frames[a.frame]
        lines = frame.strip().split('\n')
        
        for dy, line in enumerate(lines):
            y = int(t.y) + dy
            if not (0 <= y < self.h):
                continue
            
            for dx, c in enumerate(line):
                x = int(t.x) + dx
                if 0 <= x < self.w and c != ' ':
                    self.buf[y][x] = c
```

### Step 3: World

```python
# src/idle_game/ecs/world.py
from typing import List
from .entity import Entity
from .systems import System

class World:
    def __init__(self):
        self.entities: List[Entity] = []
        self.systems: List[System] = []
    
    def create(self, tags=None) -> Entity:
        e = Entity(tags=tags or set())
        self.entities.append(e)
        return e
    
    def destroy(self, entity: Entity) -> None:
        if entity in self.entities:
            self.entities.remove(entity)
    
    def add_system(self, sys: System) -> None:
        self.systems.append(sys)
    
    def update(self, dt: float) -> None:
        for sys in self.systems:
            sys.update(self.entities, dt)
        
        self.entities = [e for e in self.entities if e.active]
```

## Phase 2: Canvas Integration (Day 3-4)

```python
# src/idle_game/widgets/ecs_canvas.py
from textual.widget import Widget
from textual.strip import Strip
from textual.segment import Segment
from ..ecs.world import World
from ..ecs.systems import AnimationSystem, RenderSystem
from ..ecs.components import *

class ECSCanvas(Widget):
    def __init__(self, game_state, **kwargs):
        super().__init__(**kwargs)
        self.game_state = game_state
        self.world = World()
        self.render_sys = None
    
    def on_mount(self) -> None:
        self.world.add_system(AnimationSystem())
        self.render_sys = RenderSystem(self.size.width, self.size.height)
        self.world.add_system(self.render_sys)
        
        self.create_player()
        self.set_interval(1/15, self.tick)
    
    def create_player(self):
        e = self.world.create({'player'})
        e.add('transform', Transform(x=40, y=20))
        
        clip = AnimationClip('idle', PLAYER_FRAMES, fps=4)
        anim = Animation()
        anim.clips['idle'] = clip
        e.add('animation', anim)
        e.add('renderer', Renderer(layer=10))
    
    def tick(self):
        self.world.update(1/15)
        self.refresh()
    
    def render_line(self, y: int) -> Strip:
        line = ''.join(self.render_sys.buf[y]) if y < self.render_sys.h else ''
        return Strip([Segment(line)])
```

## Phase 3: Advanced Features (Day 5-7)

### Physics System

```python
@dataclass
class Physics:
    vx: float = 0.0
    vy: float = 0.0
    gravity: bool = False

class PhysicsSystem(System):
    def __init__(self):
        self.gravity = 20.0
    
    def update(self, entities, dt):
        for e in entities:
            phys = e.get('physics')
            trans = e.get('transform')
            
            if not phys or not trans:
                continue
            
            if phys.gravity:
                phys.vy += self.gravity * dt
            
            trans.x += phys.vx * dt
            trans.y += phys.vy * dt
```

### State Machine Component

```python
@dataclass
class StateMachine:
    current: str = "idle"
    states: Dict[str, Any] = field(default_factory=dict)

class StateMachineSystem(System):
    def update(self, entities, dt):
        for e in entities:
            sm = e.get('state_machine')
            anim = e.get('animation')
            
            if not sm or not anim:
                continue
            
            # Sync animation with state
            if anim.current != sm.current:
                anim.current = sm.current
                anim.frame = 0
                anim.time = 0.0
```

## Testing

```python
# tests/test_ecs.py
def test_entity_components():
    e = Entity()
    e.add('transform', Transform(x=10, y=20))
    
    assert e.has('transform')
    assert e.get('transform').x == 10

def test_animation_system():
    e = Entity()
    clip = AnimationClip('test', ['A', 'B'], fps=10)
    anim = Animation()
    anim.clips['test'] = clip
    e.add('animation', anim)
    
    sys = AnimationSystem()
    sys.update([e], 0.1)
    
    assert anim.frame == 1
```

## Best Practices

1. Keep components as data only
2. Put logic in systems
3. Use tags for queries
4. Limit component types (< 15)
5. Cache entity queries
6. Profile system performance
7. Document component contracts

## When NOT to Use

- Simple incremental games
- Time constraints (< 1 week)
- Team unfamiliar with ECS
- Prototype/MVP phase
- Performance not critical

Consider Strategy 1 or 2 for simpler needs.
