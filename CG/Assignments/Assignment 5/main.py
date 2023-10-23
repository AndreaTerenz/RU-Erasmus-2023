import math
import pygame as pg
import numpy as np

from pygame import Color

from game_entities import Player
from oven_engine_3D.base_app import BaseApp3D
from oven_engine_3D.entities import Plane, Cube
from oven_engine_3D.light import Light
from oven_engine_3D.shaders import MeshShader
from oven_engine_3D.utils.collisions import LineCollider
from oven_engine_3D.utils.geometry import Vector3D, Vector2D
from oven_engine_3D.utils.gl3d import PLANE_POSITION_ARRAY, PLANE_NORMAL_ARRAY, CUBE_NORMAL_ARRAY, CUBE_POSITION_ARRAY


class Assignment3(BaseApp3D):
    WALL_CELL = 0
    EMPTY_CELL = 1
    START_CELL = 2
    LIGHT_CELL = 3

    def __init__(self):
        super().__init__(fullscreen=True, ambient_color=Color("white"), clear_color=Color(30, 30, 30), update_camera=False)

        ratio = self.win_size.aspect_ratio
        self.player = Player(self, camera_params={"ratio": ratio, "fov": math.tau/6., "near": .1, "far": 80.})

        self.camera = self.player.camera
        self.lights.append(self.player.light)

        self.objects.append(self.player)

        pMat = MeshShader(positions=PLANE_POSITION_ARRAY, normals=PLANE_NORMAL_ARRAY, diffuse_color=Color("white"))
        self.objects.append(Plane(self, Vector3D.DOWN, shader=pMat, scale=150.))

        cMat = MeshShader(positions=CUBE_POSITION_ARRAY, normals=CUBE_NORMAL_ARRAY, diffuse_color=Color("red"))
        self.objects.append(Cube(self, shader=cMat, origin=Vector3D.UP + Vector3D.FORWARD*4.))

    def update(self, delta):
        pass

    def display(self):
        pass

    def handle_event(self, event):
        return False


if __name__ == '__main__':
    prog = Assignment3()
    prog.run()