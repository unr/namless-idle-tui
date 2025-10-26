from textual.widgets import Button
from textual.message import Message

class ClickButton(Button):
    """Button for manual clicking"""
    
    class Clicked(Message):
        """Message sent when button is clicked"""
        pass
    
    def __init__(self):
        super().__init__("🖱️ CLICK FOR +10", id="click-button")
    
    def on_button_pressed(self):
        self.post_message(self.Clicked())