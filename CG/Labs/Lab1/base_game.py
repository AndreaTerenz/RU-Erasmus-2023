## 22/08

import math
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "True"

import pygame as pg
from pygame.locals import *
from pygame.color import Color

from OpenGL.GL import *
from OpenGL.GLU import *

import random
from random import *

from abc import ABC, abstractmethod

from utils import *

class BaseGame(ABC):
    def __init__(self, 
                 win_size    = Vertex2D(800,600), 
                 clear_color = Color("black"),
                 scaling     = 1.) -> None:
        if not type(win_size) is Vertex2D:
            win_size = Vertex2D(win_size, win_size)

        if not type(scaling) is Vertex2D:
            scaling = Vertex2D(scaling, scaling)

        self.win_size = win_size
        self.scaling = scaling
        self.ortho_size = win_size * (scaling ** -1)
        self.clear_color = clear_color
        
        self.init_game()

        self.running = True

    def init_game(self):
        pg.display.init()
        print(self.win_size)
        pg.display.set_mode((self.win_size.x, self.win_size.y), DOUBLEBUF|OPENGL)

        gl_set_clearcolor(self.clear_color)
        
    def __update(self):
        self.update()

    def __display(self):
        glClear(GL_COLOR_BUFFER_BIT)

        # Ignore for now...
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Sets up (in OGL) the actual size of the screen
        glViewport(0, 0, self.win_size.x, self.win_size.y)
        # Sets up (in OGL) the orthographic viewing window size
        # BASICALLY 2D coordinates can be on a different scale w.r.t.
        # actual pixel coordinates
        gluOrtho2D(0, self.ortho_size.x, 0, self.ortho_size.y)

        ####################################

        self.display()

        ####################################

        # Actually show screen buffer
        pg.display.flip()    

    def quit_game(self):
        print("Quitting")
        pg.quit()
        self.running = False

    def __handle_event(self, ev):
        if ev.type == pg.QUIT:
            # Handle X button
            self.quit_game()
        elif ev.type == pg.KEYDOWN:
            if ev.key == K_ESCAPE:
                # Handle Esc key
                self.quit_game()

        self.handle_event(ev)

    def run(self):
        while self.running:
            for ev in pg.event.get():
                self.__handle_event(ev)

            if self.running:
                self.__update()
                self.__display()

    def scrn_to_ogl(self, pos: Vertex2D):
        return Vertex2D(pos.x, self.win_size.y - pos.y)


    @abstractmethod
    def display(self):
        pass

    @abstractmethod
    def handle_event(self, ev):
        pass

    @abstractmethod
    def update(self):
        pass