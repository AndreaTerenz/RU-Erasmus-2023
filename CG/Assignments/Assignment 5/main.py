import math

import pygame as pg
from OpenGL.GL import GL_CLAMP_TO_EDGE
from pygame import Color

from oven_engine_3D.base_app import BaseApp3D
from oven_engine_3D.camera import Camera
from oven_engine_3D.entities import Plane, DrawnEntity, Cube, Sphere
from oven_engine_3D.environment import Environment
from oven_engine_3D.light import Light
from oven_engine_3D.shaders import MeshShader, CustomMeshShader
from oven_engine_3D.utils.bezier import BezierCurve
from oven_engine_3D.utils.geometry import Vector3D, Vector2D
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
                             fog_mode=Environment.FogMode.EXP, fog_density=.01,
                             tonemap=Environment.Tonemapping.ACES
                         ))

        ratio = self.win_size.aspect_ratio
        """self.player = Player(self, height=0.,
                             camera_params={"ratio": ratio, "fov": math.tau/6., "near": .1, "far": 80.})"""

        # self.camera = self.player.camera
        self.lights.append(Light(self, intensity=.2, radius=0.))
        # self.add_entity(self.player)
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)

        plane_mat = MeshShader(diffuse_texture="res/textures/uvgrid.jpg",
                                     material_params={"uv_scale": Vector2D.ONE})
        self.add_entity(Plane(self, origin=Vector3D.DOWN * 5., scale=30., shader=plane_mat))

        ########### TRANSPARENCY
        tmp = Vector3D.FORWARD * 8. + Vector3D.LEFT * 4.

        grass_tex = TexturesManager.load_texture("res/textures/grass_transp.png", clamping=GL_CLAMP_TO_EDGE)
        mat_grass = MeshShader(diffuse_texture=grass_tex,
                               material_params={"transparency_mode": MeshShader.TransparencyMode.ALPHA_DISCARD})
        self.add_entity(Plane(self, origin=tmp, normal=Vector3D.FORWARD, shader=mat_grass,
                              up_rotation=-math.tau / 4.))
        self.add_entity(Plane(self, origin=tmp + Vector3D.FORWARD + Vector3D.LEFT, normal=Vector3D.FORWARD, shader=mat_grass,
                              up_rotation=-math.tau / 4.))
        self.add_entity(Plane(self, origin=tmp + Vector3D.FORWARD + Vector3D.RIGHT, normal=Vector3D.FORWARD, shader=mat_grass,
                              up_rotation=-math.tau / 4.))

        window_tex = TexturesManager.load_texture("res/textures/window_semitransp.png", clamping=GL_CLAMP_TO_EDGE)
        mat_window = MeshShader(diffuse_texture=window_tex,
                                material_params={"transparency_mode": MeshShader.TransparencyMode.ALPHA_BLEND})
        self.add_entity(
            Plane(self, origin=tmp + Vector3D.BACKWARD, normal=Vector3D.FORWARD, shader=mat_window))
        self.add_entity(
            Plane(self, origin=tmp + Vector3D.BACKWARD + Vector3D.LEFT * 2., normal=Vector3D.FORWARD, shader=mat_window))
        self.add_entity(
            Plane(self, origin=tmp + Vector3D.BACKWARD + Vector3D.RIGHT * 2., normal=Vector3D.FORWARD, shader=mat_window))
        mat_window2 = mat_window.variation(diffuse_color = "cyan")
        self.add_entity(
            Plane(self, origin=tmp + Vector3D.FORWARD * 2. + Vector3D.RIGHT * 2., normal=Vector3D.FORWARD, shader=mat_window2))
        self.add_entity(
            Plane(self, origin=tmp + Vector3D.FORWARD * 2. + Vector3D.LEFT * 2., normal=Vector3D.FORWARD, shader=mat_window2))
        ##############################

        ########### SPECULAR MAP
        tmp = Vector3D.FORWARD * 8. + Vector3D.RIGHT * 2.

        mat_crate1 = MeshShader(diffuse_texture="res/textures/img1.png",
                                material_params={"shininess": 256.,})
        self.add_entity(Cube(parent_app=self, shader=mat_crate1, origin=tmp))
        mat_crate2 = mat_crate1.variation(specular_texture="intentionallywrongpath.png")
        self.add_entity(Cube(parent_app=self, shader=mat_crate2, origin=tmp + Vector3D.RIGHT * 3.))

        self.lights.append(Light(self, position=tmp + Vector3D.RIGHT * 1.5 + Vector3D.BACKWARD * 2., radius=3., intensity=15., color="green"))
        light_cube_mat = MeshShader(material_params={"unshaded" : True, "diffuse_color":"green"})
        self.add_entity(Cube(self, origin=self.lights[-1].origin, scale=.1, shader=light_cube_mat))
        ##############################

        ####### CUSTOM SHADERS
        tmp = Vector3D.RIGHT * 8.

        mat_funky = CustomMeshShader(injected_vert="shaders/injected/vert_warp.vert",
                                    injected_frag="shaders/injected/funky.frag",
                                diffuse_texture="res/textures/window_semitransp.png")
        self.add_entity(Cube(self, origin=tmp + Vector3D.FORWARD * 5., shader=mat_funky))

        map_mat = CustomMeshShader(injected_frag="shaders/injected/rotation.frag",
                                   diffuse_texture="res/textures/map.jpg")
        self.add_entity(Sphere(parent_app=self, origin=tmp, shader=map_mat, scale=2.))
        ##############################

        ###### OBJ LOADING
        tmp = Vector3D.LEFT * 8. + Vector3D.FORWARD * 3.

        mat_bunny = MeshShader(material_params={"diffuse_color": "yellow"})
        self.add_entity(DrawnEntity(mesh="res/models/bunny.obj", parent_app=self, origin=tmp, rotation=Vector3D.UP * -math.tau/4.,shader=mat_bunny))
        ##############################

        ###### MULTIPLE LIGHTS
        tmp = Vector3D.LEFT * 8. + Vector3D.BACKWARD * 2.

        self.add_entity(DrawnEntity(self, mesh="res/models/monke.obj", origin=tmp, rotation=Vector3D.UP*math.tau/4.))
        self.add_entity(Cube(self, origin = tmp + Vector3D.DOWN * 2., scale=Vector3D(3., .2, 3.), color="gray"))
        self.lights.append(Light(self, position=tmp + Vector3D.BACKWARD * 1.5, color="red", radius=3., intensity=20.))
        self.add_entity(Cube(self, origin=self.lights[-1].origin, scale=.1, shader=light_cube_mat.variation(diffuse_color="red")))
        self.lights.append(Light(self, position=tmp - Vector3D.BACKWARD * 1.5, color="cyan", radius=3., intensity=20.))
        self.add_entity(Cube(self, origin=self.lights[-1].origin, scale=.1, shader=light_cube_mat.variation(diffuse_color="cyan")))
        ##############################

        ###### BEZIER
        tmp = Vector3D.RIGHT * 8. + Vector3D.BACKWARD * 4.
        self.bezier_camera_start = tmp

        self.bezier1 = BezierCurve.from_file("test.bezier", loop_mode=BezierCurve.LoopMode.LOOP)

        #self.bezier_cube = self.add_entity(Cube(self, scale=.1))
        self.camera = Camera(self, eye=Vector3D.UP * 9., look_at=Vector3D.FORWARD * .001, fov=math.tau/6.)
        ##############################

    def update(self, delta):
        if not self.bezier1.done:
            pos1, _dir = self.bezier1.interpolate_next(delta * .1)
            #self.bezier_cube.translate_to(pos1)
            self.camera.look_at(pos1, new_origin=pos1 * .8)# + Vector3D.LEFT * .5)

    def display(self):
        pass

    def handle_event(self, event):
        return False


if __name__ == '__main__':
    prog = Assignment5()
    prog.run()