import math

from OpenGL.GL import *
from pygame import Color

from game_entities import Player
from oven_engine_3D.base_app import BaseApp3D
from oven_engine_3D.entities import Plane, MeshEntity, Cube, Sphere
from oven_engine_3D.environment import Environment
from oven_engine_3D.meshes import CubeMesh
from oven_engine_3D.shaders import MeshShader
from oven_engine_3D.utils.geometry import Vector3D


class Assignment5(BaseApp3D):
    def __init__(self):
        super().__init__(fullscreen=True, ambient_color="white",
                         clear_color=Color(30, 30, 30), update_camera=False,
                         environment=Environment(
                             fog_mode=Environment.FogMode.DISABLED, fog_density=.05,
                             tonemap=Environment.Tonemapping.UNCHARTED
                         ))

        ratio = self.win_size.aspect_ratio
        self.player = Player(self, rot_y=math.tau/2., height=0., camera_params={"ratio": ratio, "fov": math.tau/6., "near": .1, "far": 80.})

        self.camera = self.player.camera
        self.lights.append(self.player.light)
        self.objects.append(self.player)

        self.objects.append(Plane(self, origin=Vector3D.DOWN * 5., scale=30., color="white"))

        sky_mat = MeshShader(diffuse_texture="res/textures/cubemap5.png", params={"unshaded": True}, ignore_camera_pos=True)
        #sky_mat = SkyboxShader(diffuse_texture="res/textures/cubemap4.png", params={"unshaded": True})
        self.skybox = Cube(uv_mode=CubeMesh.UVMode.CROSS, parent_app=self, shader=sky_mat)

        mat1 = MeshShader(diffuse_texture="res/textures/img1.png", params={"diffuse_color": "cyan", "unshaded": True})
        mat2 = mat1.variation(diffuse_texture="", params={"diffuse_color": "red", "unshaded": False})
        mat3 = mat2.variation(params={"diffuse_color": "yellow"})

        self.objects.append(Cube(parent_app=self, shader=mat1, origin=Vector3D.FORWARD * 3.))
        self.objects.append(MeshEntity(mesh="res/models/teapot.obj", parent_app=self, shader=mat2))
        self.objects.append(MeshEntity(mesh="res/models/bunny.obj", parent_app=self, shader=mat3))

        map_mat = MeshShader(diffuse_texture="res/textures/map.jpg")
        moon_mat = map_mat.variation(diffuse_texture="res/textures/map_moon.jpg")
        self.objects.append(Sphere(parent_app=self, origin=Vector3D.BACKWARD * 10., shader=map_mat, scale=2.))
        self.objects.append(
            Sphere(parent_app=self, origin=Vector3D.BACKWARD * 10. + Vector3D.RIGHT * 5., shader=moon_mat, scale=.5))
        """
        # mat5 = mat1.variation(diffuse_texture="", frag_shader_path="shaders/funky.frag", params = {"unshaded": False})
        # self.objects.append(MeshEntity(mesh="res/models/monke.obj", parent_app=self, shader=mat5))
        """

    def update(self, delta):
        pass

    def display(self):
        glDepthMask(GL_FALSE)
        glDisable(GL_CULL_FACE)
        self.skybox.draw()
        glEnable(GL_CULL_FACE)
        glDepthMask(GL_TRUE)

    def handle_event(self, event):
        return False


if __name__ == '__main__':
    prog = Assignment5()
    prog.run()