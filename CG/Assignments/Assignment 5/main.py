import math

from pygame import Color

from game_entities import Player
from oven_engine_3D.base_app import BaseApp3D
from oven_engine_3D.entities import Plane, Cube, MeshEntity
from oven_engine_3D.environment import Environment
from oven_engine_3D.light import Light
from oven_engine_3D.meshes import OBJMesh, SphereMesh
from oven_engine_3D.shaders import MeshShader, DEFAULT_FRAG
from oven_engine_3D.utils.geometry import Vector3D


class Assignment5(BaseApp3D):
    def __init__(self):
        super().__init__(fullscreen=True, ambient_color=Color("white"),
                         clear_color=Color(30, 30, 30), update_camera=False,
                         environment=Environment(
                             fog_mode=Environment.FogMode.DISABLED, fog_density=.05,
                             tonemap=Environment.Tonemapping.UNCHARTED
                         ))

        ratio = self.win_size.aspect_ratio
        self.player = Player(self, rot_y=math.tau/2., camera_params={"ratio": ratio, "fov": math.tau/6., "near": .1, "far": 80.})

        self.camera = self.player.camera
        self.lights.append(self.player.light)
        self.objects.append(self.player)

        self.objects.append(Plane(self, origin=Vector3D.DOWN * 5., scale=30., color=Color("white")))

        mat1 = MeshShader(diffuse_texture="res/textures/img1.png", params = {"diffuse_color" : Color("cyan"), "unshaded" : True})
        mat2 = mat1.variation(diffuse_texture="", params = {"diffuse_color" : Color("red"), "unshaded" : False})
        mat3 = mat1.variation(diffuse_texture="res/textures/cubemap2.png", params = {"diffuse_color": Color("yellow")})
        # mat5 = mat1.variation(diffuse_texture="", frag_shader_path="shaders/funky.frag", params = {"unshaded": False})

        self.objects.append(MeshEntity(mesh="res/models/cube.obj", parent_app=self, shader=mat1))
        self.objects.append(MeshEntity(mesh="res/models/teapot.obj", parent_app=self, shader=mat2))
        self.objects.append(MeshEntity(mesh="res/models/cube.obj", parent_app=self, origin=Vector3D.LEFT * 2., shader=mat3))
        self.objects.append(MeshEntity(mesh="res/models/bunny.obj", parent_app=self, shader=mat2))
        # self.objects.append(MeshEntity(mesh="res/models/monke.obj", parent_app=self, shader=mat5))

        sphere = SphereMesh(32)
        map_mat = MeshShader(diffuse_texture="res/textures/map.jpg")
        moon_mat = map_mat.variation(diffuse_texture="res/textures/map_moon.jpg")
        self.objects.append(MeshEntity(mesh=sphere, parent_app=self, origin=Vector3D.BACKWARD * 10., shader=map_mat, scale=2.))
        self.objects.append(MeshEntity(mesh=sphere, parent_app=self, origin=Vector3D.BACKWARD * 10. + Vector3D.RIGHT * 5., shader=moon_mat, scale = .5))

    def update(self, delta):
        pass

    def display(self):
        pass

    def handle_event(self, event):
        return False


if __name__ == '__main__':
    prog = Assignment5()
    prog.run()