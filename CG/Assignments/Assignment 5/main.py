import math

from OpenGL.GL import GL_CLAMP_TO_EDGE
from pygame import Color

from game_entities import Player
from oven_engine_3D.base_app import BaseApp3D
from oven_engine_3D.entities import Plane, DrawnEntity, Cube, Sphere
from oven_engine_3D.environment import Environment
from oven_engine_3D.shaders import MeshShader
from oven_engine_3D.utils.geometry import Vector3D
from oven_engine_3D.utils.textures import TexturesManager


class Assignment5(BaseApp3D):
    def __init__(self):
        super().__init__(fullscreen=True, ambient_color="white",
                         clear_color=Color(30, 30, 30), update_camera=False,
                         sky_textures={
                             "px" : "px.jpg",
                             "nx" : "nx.jpg",
                             "py" : "py.jpg",
                             "ny" : "ny.jpg",
                             "pz" : "pz.jpg",
                             "nz" : "nz.jpg",
                             "folder" : "res/textures/skyes/lake"
                         },
                         environment=Environment(
                             #global_ambient=Color(114, 230, 232),
                             fog_mode=Environment.FogMode.DISABLED, fog_density=.05,
                             tonemap=Environment.Tonemapping.ACES
                         ))

        ratio = self.win_size.aspect_ratio
        self.player = Player(self, rot_y=math.tau/2., height=0., camera_params={"ratio": ratio, "fov": math.tau/6., "near": .1, "far": 80.})

        self.camera = self.player.camera
        self.lights.append(self.player.light)
        self.add_entity(self.player)

        self.add_entity(Plane(self, origin=Vector3D.DOWN * 5., scale=30., color="white"))

        mat1 = MeshShader(specular_texture="res/textures/img1.png",
                          params={"diffuse_color": "gray", "shininess": 90.})
        mat2 = mat1.variation(diffuse_texture="", specular_texture="", params={"diffuse_color": "red", "unshaded": False})
        mat3 = mat2.variation(params={"diffuse_color": "yellow"})

        self.add_entity(Cube(parent_app=self, shader=mat1, origin=Vector3D.FORWARD * 3.))
        self.add_entity(DrawnEntity(mesh="res/models/teapot.obj", parent_app=self, shader=mat2))
        self.add_entity(DrawnEntity(mesh="res/models/bunny.obj", parent_app=self, shader=mat3))

        map_mat = MeshShader(diffuse_texture="res/textures/map.jpg")
        moon_mat = map_mat.variation(diffuse_texture="res/textures/map_moon.jpg")
        self.add_entity(Sphere(parent_app=self, origin=Vector3D.BACKWARD * 10., shader=map_mat, scale=2.))
        self.add_entity(
            Sphere(parent_app=self, origin=Vector3D.BACKWARD * 10. + Vector3D.RIGHT * 5., shader=moon_mat, scale=.5))
        """
        # mat5 = mat1.variation(diffuse_texture="", frag_shader_path="shaders/funky.frag", params = {"unshaded": False})
        # self.add_entity(MeshEntity(mesh="res/models/monke.obj", parent_app=self, shader=mat5))
        """

        grass_tex = TexturesManager.load_texture("res/textures/grass_transp.png", clamping=GL_CLAMP_TO_EDGE)
        mat_grass = MeshShader(diffuse_texture=grass_tex, transparent=True, params={"alpha_discard": True})
        self.add_entity(Plane(self, origin=Vector3D.BACKWARD * 2., normal=Vector3D.BACKWARD, shader=mat_grass, up_rotation=-math.tau/4.))

        window_tex = TexturesManager.load_texture("res/textures/window_semitransp.png", clamping=GL_CLAMP_TO_EDGE)
        mat_window = MeshShader(diffuse_texture=window_tex, transparent=True)
        self.add_entity(Plane(self, origin=Vector3D.BACKWARD * 3., normal=Vector3D.BACKWARD, shader=mat_window))
        self.add_entity(Plane(self, origin=Vector3D.BACKWARD, normal=Vector3D.BACKWARD, shader=mat_window))

    def update(self, delta):
        pass

    def display(self):
        pass

    def handle_event(self, event):
        return False


if __name__ == '__main__':
    prog = Assignment5()
    prog.run()