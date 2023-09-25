import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "True"

from pygame.color import Color

from base_app import BaseApp
from utils import *

"""
Make a windowed desktop application that displays a box. Make the box move at an even
speed diagonally. If the box hits the edges of the window, make it change direction as if it's
bouncing. If it hits the top of the screen, only change the up-down direction and so on.
"""
class Part1(BaseApp):
    def __init__(self):
        super().__init__()

        self.box_pos = self.win_size * 0.5
        self.box_size = Vector2D(50,70)
        self.direction = Vector2D(1.)
        self.speed = 0.1

    def display(self):
        set_draw_color(Color("white"))
        draw_box(self.box_pos, self.box_size)

    def handle_event(self, ev):
        return super().handle_event(ev)
    
    def update(self, delta):
        next_pos = self.box_pos + self.direction * delta * self.speed

        if not (0. <= next_pos.x <= self.win_size.x - self.box_size.x):
            self.direction.x *= -1
        if not (0. <= next_pos.y <= self.win_size.y - self.box_size.y):
            self.direction.y *= -1

        self.box_pos = next_pos

if __name__ == "__main__":
    g = Part1()
    
    exit_code = g.run()

    quit(code = exit_code)