# Urwid - Console UI Library

## Overview
Urwid is a console user interface library for Python that supports multiple text layouts, unicode, and various terminal capabilities. It's one of the older and more established TUI frameworks.

## Relevance to Our Goals
- **Widget-based**: Similar architecture to Textual
- **Animation support**: Can update widgets dynamically
- **Layout management**: Flexible box model
- **Event handling**: Keyboard and mouse support

## Key Features
- Multiple display modules (raw, curses, web)
- Custom widget creation
- Alarm-based updates for animation
- ListBox with smooth scrolling
- Progress bars and graphs

## Code Example
```python
import urwid
import random

class AnimatedWidget(urwid.WidgetWrap):
    def __init__(self):
        self.frame = 0
        self.text = urwid.Text("Frame: 0")
        super().__init__(self.text)
    
    def update(self, loop, user_data):
        self.frame += 1
        self.text.set_text(f"Frame: {self.frame}")
        # Schedule next update for ~60fps
        loop.set_alarm_in(0.016, self.update)

def main():
    animated = AnimatedWidget()
    fill = urwid.Filler(animated, 'top')
    
    loop = urwid.MainLoop(fill)
    loop.set_alarm_in(0, animated.update)
    loop.run()

if __name__ == '__main__':
    main()
```

## Pros
- Mature and stable
- Good documentation
- Flexible architecture
- Can achieve smooth animations

## Cons
- Older API design
- Not as modern as Textual
- Would require complete rewrite
- Less active development

## Integration Difficulty
**Very High** - Urwid and Textual are competing frameworks that cannot be used together.

## Alternative Use
Could study Urwid's alarm system for timing animations.

## Verdict
Not compatible with our Textual-based application. Textual is more modern and better suited for our needs.
