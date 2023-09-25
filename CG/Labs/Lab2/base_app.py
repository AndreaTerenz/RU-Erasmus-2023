# 28.08
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "True"

import pygame as pg
from pygame.locals import *
from pygame.color import Color

from OpenGL.GL import *
from OpenGL.GLU import *

from abc import ABC, abstractmethod

from utils import *

class BaseApp(ABC):
    def __init__(self, 
                 win_title   = "BaseApp",
                 win_size    = Vector2D(800,600), 
                 clear_color = Color("black"),
                 scaling     = 1.,
                 target_fps  = 60.,
                 enable_fps_print = False) -> None:
        if target_fps <= 0.:
            target_fps = 60.

        if not type(win_size) is Vector2D:
            win_size = Vector2D(win_size, win_size)

        if not type(scaling) is Vector2D:
            scaling = Vector2D(scaling, scaling)

        self.win_size = win_size
        self.scaling = scaling
        self.ortho_size = win_size * (scaling ** -1)
        self.clear_color = clear_color
        self.win_title = win_title
        self.target_fps = target_fps
        self.enable_fps_print = enable_fps_print
        
        pg.display.init()
        pg.display.set_mode((self.win_size.x, self.win_size.y), DOUBLEBUF|OPENGL)
        pg.display.set_caption(win_title)

        set_clear_color(self.clear_color)

        self.avg_fps = 0.
        self.ticks = 0
        self.exit_code = 0
        self.running = True
        self.clock = pg.time.Clock()
        
    def __update(self, delta):
        self.update(delta)

    def __display(self):
        glClear(GL_COLOR_BUFFER_BIT)

        # Ignore for now...
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Sets up (in OGL) the orthographic viewing window size
        # BASICALLY 2D coordinates can be on a different scale w.r.t.
        # actual pixel coordinates
        gluOrtho2D(0, self.ortho_size.x, 0, self.ortho_size.y)
        # Sets up (in OGL) the actual size of the screen
        glViewport(0, 0, self.win_size.x, self.win_size.y)

        self.display()

        # Actually show screen buffer
        pg.display.flip()    

    def quit_game(self, exit_code = 0):
        print("Quitting")
        pg.quit()
        self.exit_code = exit_code
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
                delta = self.clock.tick(self.target_fps)
                fps = 1000. / delta
                self.avg_fps += fps
                self.ticks += 1
                
                if self.ticks % 10 == 0:
                    self.avg_fps /= 10
                    fps_target_ratio = self.avg_fps / self.target_fps

                    fps_str = f"FPS: {fps:.2f} ({fps_target_ratio*100:.2f}% of target)"
                    pg.display.set_caption(f"{self.win_title} | {fps_str}")
                    
                    self.avg_fps = 0.
                
                if self.enable_fps_print: 
                    print(fps_str)

                self.__update(delta)
                self.__display()

        return self.exit_code

    def scrn_to_ogl(self, pos: Vector2D):
        return Vector2D(pos.x, self.win_size.y - pos.y)

    def get_mouse_pos(self) -> Vector2D:
        m_pos = pg.mouse.get_pos()
        m_pos = Vector2D(m_pos)
        m_pos = self.scrn_to_ogl(m_pos)

        return m_pos

    @abstractmethod
    def display(self):
        pass

    @abstractmethod
    def handle_event(self, ev):
        pass

    @abstractmethod
    def update(self, delta):
        pass