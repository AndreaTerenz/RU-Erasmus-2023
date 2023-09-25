import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "True"

from base_app import BaseApp
from utils import *
from random import uniform

class Lab2B(BaseApp):
    def __init__(self):
        super().__init__(win_title="Lab2B - Brownian Motion")

        self.points = []
        self.agent_pos = Vector2D(200.)
        self.agent_dir = Vector2D(1., 0.)
        self.agent_speed = 20.

    def display(self):
        set_draw_color("darkgoldenrod1")
        draw_circle(self.agent_pos, 5., filled=True)

        set_draw_color("white")
        draw_lines(self.points, strip=True)

    def handle_event(self, ev):
        return super().handle_event(ev)
    
    def update(self, delta):
        angle = uniform(-1.,1.) * math.tau/3. 
        self.agent_dir = self.agent_dir.rotated(angle)
        self.agent_pos += self.agent_dir * self.agent_speed * delta * 0.01

        if len(self.points) > 200:
            self.points.pop(0)

        self.points += [self.agent_pos]

if __name__ == "__main__":
    g = Lab2B()
    
    exit_code = g.run()

    quit(code = exit_code)