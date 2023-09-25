import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "True"

import pygame as pg
from pygame.locals import *

from base_app import BaseApp
from utils import *

"""
Make a windowed desktop application that displays a blank screen. When you click with the
mouse on the screen display a box centered at the point you clicked on. Each time you click
the screen add a new box. Every frame you have to display all the boxes, so you have to keep
track of them the whole time. Only one box should be created for each click.
"""
class Part3(BaseApp):
    def __init__(self):
        super().__init__()

        self.box_size = Vector2D(30.)
        self.boxes = []

    def display(self):
        for b in self.boxes:
            draw_box_centered(b, self.box_size)
    
    def handle_event(self, ev):
        if ev.type == pg.MOUSEBUTTONDOWN:
            if ev.button == 1:
                m_pos = self.get_mouse_pos()

                self.boxes.append(m_pos)
    
    def update(self, delta):
        return super().update(delta)

if __name__ == "__main__":
    g = Part3()
    
    exit_code = g.run()

    quit(code = exit_code)