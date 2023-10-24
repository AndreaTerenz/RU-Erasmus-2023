import math

from pygame import Color

from game_entities import Player
from oven_engine_3D.base_app import BaseApp3D
from oven_engine_3D.entities import Plane, Cube
from oven_engine_3D.shaders import MeshShader
from oven_engine_3D.utils.geometry import Vector3D


class Assignment5(BaseApp3D):
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

        planeMat = MeshShader(diffuse_color=Color("cyan"), diffuse_texture="res/img1.png")
        cubeMat = MeshShader(diffuse_color=Color("red"), diffuse_texture="res/img1.png")

        self.objects.append(Plane(self, Vector3D.DOWN, shader=cubeMat, scale=50.))
        self.objects.append(Cube(self, shader=planeMat, origin=Vector3D.UP*2. + Vector3D.FORWARD*4.))

    def update(self, delta):
        pass

    def display(self):
        pass

    def handle_event(self, event):
        return False


if __name__ == '__main__':
    prog = Assignment5()
    prog.run()