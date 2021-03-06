import src.settings as s
from src.game_objects.gui import console_print_event
from src.game_objects.empty_sprite import EmptySprite


class State(EmptySprite):
    """Manage the game state"""
    def __init__(self):
        super().__init__()
        self.seconds_per_month = 60
        self.month = 0
        self.seconds_passed = 0.0
        self.frame = 0
        self.log_current_month()

    def update(self, *args):
        self.frame += 1
        if self.frame == s.FPS:
            self.frame = 0
            self.seconds_passed += 1.0
        if self.seconds_passed > self.seconds_per_month:
            self.month += 1
            self.seconds_passed = 0.0
            self.log_current_month()

    def log_current_month(self):
        console_print_event("It is month " + str(self.month))
