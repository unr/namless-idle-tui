# Pillow (PIL) for Sprite Processing

## Overview
Pillow (Python Imaging Library) can be used to load, process, and convert sprite images into ASCII/Unicode art for terminal display. This enables using real image assets in TUI applications.

## Relevance to Our Goals
- **Sprite loading**: Load PNG/GIF sprite sheets
- **ASCII conversion**: Convert images to terminal characters
- **Animation frames**: Extract frames from animated GIFs
- **Image processing**: Resize, crop, and manipulate sprites

## Key Features
- Load various image formats
- Image to ASCII/Unicode conversion
- Sprite sheet splitting
- Color quantization for terminal colors
- GIF frame extraction

## Code Example
```python
from PIL import Image
import numpy as np
from textual.widgets import Static
from textual.app import App, ComposeResult

class SpriteConverter:
    def __init__(self):
        # Unicode block characters for different brightness levels
        self.blocks = ' ░▒▓█'
        # Extended ASCII art characters
        self.ascii_chars = ' .:-=+*#%@'
        
    def load_sprite_sheet(self, path, frame_width, frame_height):
        """Load and split a sprite sheet into frames"""
        sheet = Image.open(path)
        frames = []
        
        for y in range(0, sheet.height, frame_height):
            for x in range(0, sheet.width, frame_width):
                frame = sheet.crop((x, y, x + frame_width, y + frame_height))
                frames.append(frame)
        
        return frames
    
    def image_to_unicode(self, image, width=20, height=10):
        """Convert PIL image to Unicode block art"""
        # Resize image to target dimensions
        image = image.resize((width, height), Image.Resampling.LANCZOS)
        
        # Convert to grayscale
        image = image.convert('L')
        pixels = np.array(image)
        
        # Map brightness to Unicode blocks
        result = []
        for row in pixels:
            line = ''
            for pixel in row:
                # Map 0-255 to block index
                index = int(pixel * (len(self.blocks) - 1) / 255)
                line += self.blocks[index]
            result.append(line)
        
        return '\n'.join(result)
    
    def image_to_colored_unicode(self, image, width=20, height=10):
        """Convert to colored Unicode with ANSI escape codes"""
        # Resize image
        image = image.resize((width, height), Image.Resampling.LANCZOS)
        
        # Keep RGB for color
        pixels = np.array(image)
        
        result = []
        for row in pixels:
            line = ''
            for pixel in row:
                r, g, b = pixel[:3] if len(pixel) >= 3 else (pixel, pixel, pixel)
                # Create ANSI color escape
                color = f'\033[38;2;{r};{g};{b}m'
                # Choose character based on brightness
                brightness = (r + g + b) // 3
                char = '█' if brightness > 128 else '▓'
                line += f'{color}{char}\033[0m'
            result.append(line)
        
        return '\n'.join(result)

class AnimatedSprite:
    def __init__(self, frames, fps=10):
        self.frames = frames
        self.fps = fps
        self.current_frame = 0
        self.time_accumulator = 0
        self.frame_duration = 1.0 / fps
        
    def update(self, dt):
        self.time_accumulator += dt
        
        while self.time_accumulator >= self.frame_duration:
            self.time_accumulator -= self.frame_duration
            self.current_frame = (self.current_frame + 1) % len(self.frames)
    
    def get_current_frame(self):
        return self.frames[self.current_frame]

class SpriteCanvas(Static):
    def __init__(self):
        super().__init__()
        self.converter = SpriteConverter()
        self.sprites = []
        
    def on_mount(self):
        # Load sprite sheet
        try:
            frames = self.converter.load_sprite_sheet(
                'sprites/coin.png', 16, 16
            )
            # Convert frames to Unicode
            unicode_frames = [
                self.converter.image_to_unicode(frame, 8, 8) 
                for frame in frames
            ]
            
            self.sprite = AnimatedSprite(unicode_frames, fps=10)
            self.sprites.append(self.sprite)
            
        except FileNotFoundError:
            # Create placeholder animation
            frames = ['O', '0', 'o', '.']
            self.sprite = AnimatedSprite(frames, fps=4)
            self.sprites.append(self.sprite)
        
        self.set_interval(1/60, self.update_animation)
    
    def update_animation(self):
        dt = 1/60
        for sprite in self.sprites:
            sprite.update(dt)
        self.refresh()
    
    def render(self):
        if self.sprites:
            return self.sprites[0].get_current_frame()
        return "No sprites loaded"

class SpriteDemo(App):
    def compose(self) -> ComposeResult:
        yield SpriteCanvas()

# Utility function to create sprite sheets
def create_sprite_sheet_from_gif(gif_path, output_path):
    """Extract frames from GIF and create a sprite sheet"""
    gif = Image.open(gif_path)
    frames = []
    
    try:
        while True:
            frames.append(gif.copy())
            gif.seek(len(frames))
    except EOFError:
        pass
    
    if frames:
        # Calculate sprite sheet dimensions
        frame_width = frames[0].width
        frame_height = frames[0].height
        sheet_width = frame_width * len(frames)
        sheet_height = frame_height
        
        # Create sprite sheet
        sheet = Image.new('RGBA', (sheet_width, sheet_height))
        
        for i, frame in enumerate(frames):
            sheet.paste(frame, (i * frame_width, 0))
        
        sheet.save(output_path)
        return sheet

if __name__ == "__main__":
    app = SpriteDemo()
    app.run()
```

## Pros
- Use real image assets
- Automatic ASCII/Unicode conversion
- Support for animated GIFs
- Rich image processing capabilities
- Can create sophisticated visual effects

## Cons
- Requires Pillow dependency
- Image to text conversion loses detail
- Color support depends on terminal capabilities
- Processing overhead for conversion

## Integration Difficulty
**Low** - Pillow works well as a preprocessing tool for sprites without interfering with Textual.

## Verdict
**Recommended** for projects that want to use image-based sprites. The ability to convert real images to terminal art opens up many possibilities for rich visuals.
