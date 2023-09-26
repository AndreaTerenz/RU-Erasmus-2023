
# from OpenGL.GL import *
# from OpenGL.GLU import *

import pygame
from pygame.locals import *

from Control3DBase.Base3DObjects import Cube1, Cube2, Cube3
from Control3DBase.Matrices import *
from Control3DBase.Shaders import *

from oven_engine.utils.geometry import Vector3D


class GraphicsProgram3D:
    def __init__(self, bg_color = (0.0, 0.0, 0.0, 1.0)):

        pygame.init() 
        pygame.display.set_mode((800,600), pygame.OPENGL|pygame.DOUBLEBUF)

        self.projection_matrix = ProjectionMatrix(.5, 100, 4)
        self.view_matrix = ViewMatrix()
        self.view_matrix.look_at(Vector3D(-5., 5., 5.), Vector3D.ZERO)

        self.cubes = [
            Cube1(self, size=0.4),
            Cube2(self, origin=Vector3D(-3., 0., 0.), size=0.4),
            Cube3(self, origin=Vector3D(0., 2., 0.), size=0.4),
        ]

        self.clock = pygame.time.Clock()
        self.clock.tick()

        self.angle = 0

        self.UP_key_down = False  ## --- ADD CONTROLS FOR OTHER KEYS TO CONTROL THE CAMERA --- ##

        self.bg_color = bg_color
        self.white_background = False
        self.ticks = 0

    def update(self):
        delta_time = self.clock.tick() / 1000.0
        self.ticks += 1

        self.angle += np.pi * delta_time
        # if angle > 2 * pi:
        #     angle -= (2 * pi)

        if self.UP_key_down:
            self.white_background = True
        else:
            self.white_background = False

        for cube in self.cubes:
            cube.update(delta_time)

    def display(self):
        glEnable(GL_DEPTH_TEST)  ### --- NEED THIS FOR NORMAL 3D BUT MANY EFFECTS BETTER WITH glDisable(GL_DEPTH_TEST) ... try it! --- ###

        # glClearColor(self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3])
        if self.white_background:
            glClearColor(1.0, 1.0, 1.0, 1.0)
        else:
            glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)  ### --- YOU CAN ALSO CLEAR ONLY THE COLOR OR ONLY THE DEPTH --- ###

        glViewport(0, 0, 800, 600)

        for cube in self.cubes:
            cube.draw()

        pygame.display.flip()

    def program_loop(self):
        exiting = False
        while not exiting:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quitting!")
                    exiting = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        print("Escaping!")
                        exiting = True

                elif event.type == pygame.KEYUP:
                    if event.key == K_UP:
                        self.UP_key_down = not self.UP_key_down
            
            self.update()
            self.display()

        #OUT OF GAME LOOP
        pygame.quit()

    def start(self):
        self.program_loop()

if __name__ == "__main__":
    GraphicsProgram3D().start()