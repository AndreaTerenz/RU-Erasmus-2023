import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "True"

import pygame as pg
from pygame.locals import *
from pygame.color import Color

from base_game import BaseGame
from utils import *

from OpenGL.GL import *
from OpenGL.GLU import *

from math import cos, sin

import random
from random import *

class Lab1_Game(BaseGame):
    def __init__(self, win_size: Vertex2D | int = Vertex2D(800,600), clear_color=Color("black"), scaling: Vertex2D | float = 1) -> None:
        super().__init__(win_size, clear_color, scaling)
        
        # L, R, U, D
        self.goings = [False, False, False, False]
        self.direction = Vertex2D(0., 0.)
        self.position = Vertex2D(0.0, 0.0)
        self.speed = 0.1

    def display(self):
        gl_circle(Vertex2D(40, 40), radius=10.0)
        gl_arc(Vertex2D(140, 40), math.tau/4., radius=10.0)
        gl_circle(Vertex2D(40, 140), radius=10.0, steps=4)
        gl_circle(Vertex2D(40, 240), radius=10.0, steps=4, phase=math.tau/8.)

        gl_box(Vertex2D(500, 500), Vertex2D(30,30))

        gl_set_drawcolor(Color("#FF00FF"))
        gl_triangle(
            self.position,
            self.position + (0,100),
            self.position + (100,0)
        )

    def handle_event(self, ev):
        if ev.type == KEYDOWN:
            if ev.key == K_q:
                glClearColor(
                    random(),
                    random(),
                    random(),
                    1.
                )
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
                self.position = self.scrn_to_ogl(Vertex2D(m_pos))
        
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

    def update(self):
        if self.direction.length() != 0.0:
            self.position += self.direction * self.speed
    
if __name__ == "__main__":
    print("Initializing...", end="")
    game = Lab1_Game(
        win_size=Vertex2D(600,600),
        clear_color=Color("blue"),
    )
    print("done")

    game.run()