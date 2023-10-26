import math

from pygame import Color

from game_entities import Player
from oven_engine_3D.base_app import BaseApp3D
from oven_engine_3D.entities import Plane, Cube, MeshEntity
from oven_engine_3D.meshes import OBJMesh
from oven_engine_3D.shaders import MeshShader, DEFAULT_FRAG
from oven_engine_3D.utils.geometry import Vector3D


class Assignment5(BaseApp3D):
    WALL_CELL = 0
    EMPTY_CELL = 1
    START_CELL = 2
    LIGHT_CELL = 3

    def __init__(self):
        super().__init__(fullscreen=True, ambient_color=Color("white"), clear_color=Color(30, 30, 30), update_camera=False)

        ratio = self.win_size.aspect_ratio
        self.player = Player(self, rot_y=math.tau/2., camera_params={"ratio": ratio, "fov": math.tau/6., "near": .1, "far": 80.})

        self.camera = self.player.camera
        self.lights.append(self.player.light)
        self.objects.append(self.player)

        self.objects.append(Plane(self, origin=Vector3D.DOWN * 5., scale=30., color=Color("white")))

        mat1 = MeshShader(diffuse_color=Color("cyan"), diffuse_texture="res/textures/img1.png", unshaded=True)
        mat2 = mat1.variation(diffuse_color=Color("red"), unshaded=False, diffuse_texture="")
        mat3 = mat1.variation(diffuse_texture="res/textures/cubemap2.png", diffuse_color=Color("yellow"))
        mat4 = mat2.variation(diffuse_texture="")
        mat5 = mat2.variation(diffuse_texture="", fragID="funky.frag")

        self.objects.append(MeshEntity(mesh="res/models/cube.obj", parent_app=self, shader=mat1))
        self.objects.append(MeshEntity(mesh="res/models/teapot.obj", parent_app=self, origin=Vector3D.RIGHT*3. + Vector3D.UP * 2., shader=mat2))
        self.objects.append(MeshEntity(mesh="res/models/cube.obj", parent_app=self, origin=Vector3D.LEFT*3. - Vector3D.UP * 2., shader=mat3))
        self.objects.append(MeshEntity(mesh="res/models/bunny.obj", parent_app=self, shader=mat4))
        self.objects.append(MeshEntity(mesh="res/models/monke.obj", parent_app=self, shader=mat5))

    def update(self, delta):
        pass

    def display(self):
        pass

    def handle_event(self, event):
        return False


if __name__ == '__main__':
    prog = Assignment5()
    prog.run()