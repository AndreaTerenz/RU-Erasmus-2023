import math

from pygame import Color

from game_entities import Player
from oven_engine_3D.base_app import BaseApp3D
from oven_engine_3D.entities import Plane, DrawnEntity, Cube, Sphere, Skybox
from oven_engine_3D.environment import Environment
from oven_engine_3D.shaders import MeshShader
from oven_engine_3D.utils.geometry import Vector3D
from oven_engine_3D.utils.textures import TexturesManager


class Assignment5(BaseApp3D):
    def __init__(self):
        super().__init__(fullscreen=True, ambient_color="white",
                         clear_color=Color(30, 30, 30), update_camera=False,
                         environment=Environment(
                             #global_ambient=Color(114, 230, 232),
                             fog_mode=Environment.FogMode.DISABLED, fog_density=.05,
                             tonemap=Environment.Tonemapping.ACES
                         ))

        ratio = self.win_size.aspect_ratio
        self.player = Player(self, rot_y=math.tau/2., height=0., camera_params={"ratio": ratio, "fov": math.tau/6., "near": .1, "far": 80.})

        self.camera = self.player.camera
        self.lights.append(self.player.light)
        self.objects.append(self.player)

        self.objects.append(Plane(self, origin=Vector3D.DOWN * 5., scale=30., color="white"))

        mat1 = MeshShader(diffuse_texture="res/textures/img1.png", params={"diffuse_color": "cyan", "unshaded": True})
        mat2 = mat1.variation(diffuse_texture="", params={"diffuse_color": "red", "unshaded": False})
        mat3 = mat2.variation(params={"diffuse_color": "yellow"})

        self.objects.append(Cube(parent_app=self, shader=mat1, origin=Vector3D.FORWARD * 3.))
        self.objects.append(DrawnEntity(mesh="res/models/teapot.obj", parent_app=self, shader=mat2))
        self.objects.append(DrawnEntity(mesh="res/models/bunny.obj", parent_app=self, shader=mat3))

        map_mat = MeshShader(diffuse_texture="res/textures/map.jpg")
        moon_mat = map_mat.variation(diffuse_texture="res/textures/map_moon.jpg")
        self.objects.append(Sphere(parent_app=self, origin=Vector3D.BACKWARD * 10., shader=map_mat, scale=2.))
        self.objects.append(
            Sphere(parent_app=self, origin=Vector3D.BACKWARD * 10. + Vector3D.RIGHT * 5., shader=moon_mat, scale=.5))
        """
        # mat5 = mat1.variation(diffuse_texture="", frag_shader_path="shaders/funky.frag", params = {"unshaded": False})
        # self.objects.append(MeshEntity(mesh="res/models/monke.obj", parent_app=self, shader=mat5))
        """

        sky_cubemap = TexturesManager.load_cubemap(px="px.jpg", nx="s.jpg", py="py.jpg", ny="ny.jpg", pz="pz.jpg", nz="nz.jpg",
                                                   folder="res\\textures\\skyes\\lake")

        self.skybox = Skybox(parent_app=self, cubemap_text=sky_cubemap)
        self.objects.append(self.skybox)

    def update(self, delta):
        pass

    def display(self):
        pass

    def handle_event(self, event):
        return False


if __name__ == '__main__':
    prog = Assignment5()
    prog.run()