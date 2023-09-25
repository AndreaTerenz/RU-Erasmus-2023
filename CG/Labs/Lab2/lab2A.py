import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "True"

from pygame.color import Color
from pygame.colordict import THECOLORS
from base_app import BaseApp
from utils import *
from dataclasses import dataclass

@dataclass
class Planet():
    color: str
    offset: float
    speed: float
    current_angle: float

class Lab2A(BaseApp):
    def __init__(self):
        super().__init__()

        self.planets = [
            Planet("brown", 40., 30., 0.),
            Planet("blue", 80., 14., 0.),
            Planet("darkgreen", 200., 6., 0.)
        ]

    def display(self):
        push_matrix()

        translate_2D(Vector2D(300))
        
        set_draw_color("darkgoldenrod1")
        draw_circle(Vector2D(0.), 20., filled=True)

        for p in self.planets:
            push_matrix()
            rotate_2D(p.current_angle)
            translate_2D(Vector2D(p.offset, 0.))

            set_draw_color(p.color)
            draw_circle(Vector2D(0.), 5., filled=True)
            pop_matrix()

        pop_matrix()

    def handle_event(self, ev):
        return super().handle_event(ev)
    
    def update(self, delta):
        for p_idx in range(len(self.planets)):
            self.planets[p_idx].current_angle += delta * 0.01 * self.planets[p_idx].speed

if __name__ == "__main__":
    g = Lab2A()
    
    exit_code = g.run()

    quit(code = exit_code)