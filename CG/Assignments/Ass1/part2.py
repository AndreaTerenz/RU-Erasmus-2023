import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "True"

import pygame as pg

from base_app import BaseApp
from utils import *

"""
Make a windowed desktop application that displays a box. Make the box move around the
screen when you hold down the arrow keys. Dont let it exit the screen. When it hits the edge
make it stop or slide along the edge.
"""
class Part2(BaseApp):
    def __init__(self):
        super().__init__()

        # L, R, U, D
        self.goings = [False, False, False, False]
        self.box_pos = self.win_size * 0.5
        self.box_size = Vector2D(50,70)
        self.direction = Vector2D(0.)
        self.speed = .1

    def display(self):
        draw_box(self.box_pos, self.box_size)

    def handle_event(self, ev):
        if ev.type == KEYDOWN:
            if ev.key == K_LEFT and not (self.goings[1]):
                self.goings[0] = True
            elif ev.key == K_RIGHT and not (self.goings[0]):
                self.goings[1] = True

            if ev.key == K_UP and not (self.goings[3]):
                self.goings[2] = True
            elif ev.key == K_DOWN and not (self.goings[2]):
                self.goings[3] = True
        elif ev.type == KEYUP:
            if ev.key == K_LEFT:
                self.goings[0] = False
            if ev.key == K_RIGHT:
                self.goings[1] = False
            if ev.key == K_UP:
                self.goings[2] = False
            if ev.key == K_DOWN:
                self.goings[3] = False
        elif ev.type == pg.MOUSEBUTTONDOWN:
            if ev.button == 1:
                m_pos = pg.mouse.get_pos()
                self.position = self.scrn_to_ogl(Vector2D(m_pos))
        
        self.direction *= 0.0
        if self.goings[0]:
            self.direction.x = -1.0
        elif self.goings[1]:
            self.direction.x = 1.0
        if self.goings[2]:
            self.direction.y = 1.0
        elif self.goings[3]:
            self.direction.y = -1.0

        self.direction = self.direction.normalized()
    
    def update(self, delta):
        if self.direction.length_sq() != 0.0:
            next_pos = self.box_pos + self.direction * self.speed * delta

            next_pos.x = min(self.win_size.x - self.box_size.x, max(0., next_pos.x))
            next_pos.y = min(self.win_size.y - self.box_size.y, max(0., next_pos.y))

            self.box_pos = next_pos

if __name__ == "__main__":
    g = Part2()
    
    exit_code = g.run()

    quit(code = exit_code)