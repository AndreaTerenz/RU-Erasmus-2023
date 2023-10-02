import pygame as pg
from pygame.locals import *

from Control3DBase.Base3DObjects import Cube1, Cube2, Cube3, Camera
from Control3DBase.Shaders import *
from oven_engine.utils.geometry import Vector3D, Vector2D


# from OpenGL.GL import *
# from OpenGL.GLU import *


class GraphicsProgram3D:
    def __init__(self,
                 win_title   = "BaseApp",
                 win_size    = Vector2D(720,720),
                 clear_color = Color("black"),
                 fullscreen = True):

        pg.init()

        if fullscreen:
            screen = pg.display.set_mode((0,0), pg.OPENGL|pg.DOUBLEBUF|pg.FULLSCREEN)
            self.win_size = Vector2D(screen.get_size())
        else:
            pg.display.set_mode(tuple(win_size), pg.OPENGL|pg.DOUBLEBUF)
            self.win_size = win_size

        pg.display.set_caption(win_title)

        ratio = self.win_size.aspect_ratio

        self.camera = Camera(self, eye=Vector3D(-8., 8., 8.) * 3., look_at=Vector3D.ZERO, ratio=ratio, near=.5, far=100)

        self.cubes = [
            Cube1(self, size=0.4),
            Cube2(self, origin=Vector3D(-3., 0., 0.), size=0.4),
            Cube3(self, origin=Vector3D(0., 2., 0.), size=0.4),
        ]

        self.clock = pg.time.Clock()

        self.clear_color = clear_color
        self.white_background = False
        self.ticks = 0

    def update(self):
        delta_time = self.clock.tick(60.) / 1000.0
        self.ticks += 1

        self.camera.update(delta_time)

        for cube in self.cubes:
            cube.update(delta_time)

    def display(self):
        glEnable(GL_DEPTH_TEST)  ### --- NEED THIS FOR NORMAL 3D BUT MANY EFFECTS BETTER WITH glDisable(GL_DEPTH_TEST) ... try it! --- ###

        if self.white_background:
            glClearColor(1.0, 1.0, 1.0, 1.0)
        else:
            glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)  ### --- YOU CAN ALSO CLEAR ONLY THE COLOR OR ONLY THE DEPTH --- ###

        glViewport(0, 0, self.win_size.x, self.win_size.y)

        #draw_plane(self.camera, offset=Vector3D.UP * 4., color=(0.5, 0.5, 0.5), scale=Vector3D(10, 0, 10))
        for cube in self.cubes:
            cube.shader.get_projview(self.camera)
            cube.draw()

        pg.display.flip()

    def program_loop(self):
        exiting = False
        while not exiting:
            exiting = self.handle_events()

            if not exiting:
                self.update()
                self.display()

        #OUT OF GAME LOOP
        pg.quit()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                print("Quitting!")
                return True
            elif event.type == pg.KEYDOWN:
                if event.key == K_ESCAPE:
                    print("Escaping!")
                    return True

            self.camera.handle_event(event)

        return False
    
    def start(self):
        self.program_loop()

if __name__ == "__main__":
    GraphicsProgram3D().start()