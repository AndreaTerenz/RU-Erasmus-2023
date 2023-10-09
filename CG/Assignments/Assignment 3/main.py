import math
import pygame as pg
import numpy as np

from pygame import Color

from game_entities import Player
from oven_engine_3D.base_app import BaseApp3D
from oven_engine_3D.camera import FPCamera
from oven_engine_3D.entities import Cube, Plane
from oven_engine_3D.light import Light, MovableLight
from oven_engine_3D.shaders import MeshShader
from oven_engine_3D.utils.geometry import Vector3D, Vector2D
from oven_engine_3D.utils.gl3d import PLANE_POSITION_ARRAY, PLANE_NORMAL_ARRAY

from OpenGL.GL import *
from OpenGL.GLU import *

def read_maze(file_path = "test.maze"):
    with open(file_path, "r") as f:
        lines = f.readlines()

    lines = [line.strip() for line in lines]

    # convert maze to numpy array
    return np.array([list(line) for line in lines], dtype=np.int8)

class Assignment3(BaseApp3D):
    def __init__(self):
        super().__init__(fullscreen=True, ambient_color=Color("red"),update_camera=False)

        self.maze = read_maze()

        ratio = self.win_size.aspect_ratio
        self.player = Player(self, camera_params={"ratio": ratio, "fov": math.tau/6., "near": .5, "far": 100.})
        self.camera = self.player.camera

        self.light = MovableLight(self, Vector3D.UP * 2., Color("white"))

        self.light_cube = Cube(self, color=self.light.color)
        self.light_cube.scale_by(.1)
        self.light_cube.translate_to(self.light.origin)
        self.light_cube.shader.set_unshaded(True)

        self.objects = [self.light_cube]

        self.maze = read_maze()

        yellow_mat = MeshShader(positions=PLANE_POSITION_ARRAY, normals=PLANE_NORMAL_ARRAY,
                                diffuse_color=Color("yellow"))
        blue_mat   = MeshShader(diffuse_color=Color("blue"), vbo=yellow_mat.pos_vbo)
        center = Vector2D(*self.maze.shape).yx

        # Create a Plane for each wall in the maze
        for i in range(self.maze.shape[0]):
            for j in range(self.maze.shape[1]):
                shader = blue_mat if self.maze[i][j] == 1 else yellow_mat
                pos = Vector2D(j, i)*2 - center

                plane = Plane(self, origin=pos.x0y, shader=shader, scale=Vector3D.ONE)
                self.objects.append(plane)

    def update(self, delta):
        self.player.update(delta)
        self.light_cube.translate_to(self.light.origin)

    def display(self):
        pass

    def handle_event(self, event):
        if event.type == pg.MOUSEMOTION:
            self.mouse_delta = Vector2D(event.rel) / self.win_size
            self.mouse_delta = self.mouse_delta.snap(.005)

        self.camera.handle_event(event)

        return False


if __name__ == '__main__':
    prog = Assignment3()
    prog.run()