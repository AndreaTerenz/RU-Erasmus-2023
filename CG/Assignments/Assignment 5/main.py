import math

import pygame as pg
from OpenGL.GL import GL_CLAMP_TO_EDGE
from pygame import Color

from oven_engine_3D.base_app import BaseApp3D
from oven_engine_3D.camera import Camera, FPCamera
from oven_engine_3D.entities import Plane, DrawnEntity, Cube, Sphere
from oven_engine_3D.environment import Environment
from oven_engine_3D.light import Light
from oven_engine_3D.shaders.mesh_shader import MeshShader
from oven_engine_3D.utils.bezier import BezierCurve
from oven_engine_3D.utils.geometry import Vector3D, Vector2D
from oven_engine_3D.utils.textures import TexturesManager


class Assignment5(BaseApp3D):
    def __init__(self):
        super().__init__(fullscreen=True,
                         glob_ambient_mode=BaseApp3D.GlobalAmbientMode.SKYBOX,
                         win_size = Vector2D(1280, 720),
                         clear_color=Color(30, 30, 30), update_camera=False,
                         sky_textures={
                             "folder": "res\\textures\\skyes\\desert_day",
                             "ext": "png"
                         },
                         environment=Environment(
                             global_ambient_strength=.8,
                             fog_mode=Environment.FogMode.EXP, fog_density=.009,
                             tonemap=Environment.Tonemapping.ACES,
                         ))

        ratio = self.win_size.aspect_ratio

        #self.lights.append(Light(self, intensity=.2, radius=0.))
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)

        plane_mat = MeshShader(diffuse_texture="res/textures/uvgrid.jpg", uv_scale = Vector2D.ONE * 4.)
        self.add_entity(Plane(self, origin=Vector3D.DOWN * 5., scale=30., shader=plane_mat))

        ########### TRANSPARENCY
        tmp = Vector3D.FORWARD * 8. + Vector3D.LEFT * 4.

        grass_tex = TexturesManager.load_texture("res/textures/grass_transp.png", clamping=GL_CLAMP_TO_EDGE)
        mat_grass = MeshShader(diffuse_texture=grass_tex,
                               transparency_mode= MeshShader.TransparencyMode.ALPHA_DISCARD)
        self.add_entity(Plane(self, origin=tmp, normal=Vector3D.FORWARD, shader=mat_grass,
                              up_rotation=-math.tau / 4.))
        self.add_entity(Plane(self, origin=tmp + Vector3D.FORWARD + Vector3D.LEFT, normal=Vector3D.FORWARD, shader=mat_grass,
                              up_rotation=-math.tau / 4.))
        self.add_entity(Plane(self, origin=tmp + Vector3D.FORWARD + Vector3D.RIGHT, normal=Vector3D.FORWARD, shader=mat_grass,
                              up_rotation=-math.tau / 4.))

        window_tex = TexturesManager.load_texture("res/textures/window_semitransp.png", clamping=GL_CLAMP_TO_EDGE)
        mat_window = MeshShader(diffuse_texture=window_tex,
                                transparency_mode=MeshShader.TransparencyMode.ALPHA_BLEND)
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
                                shininess = 128.)
        self.add_entity(Cube(parent_app=self, shader=mat_crate1, origin=tmp))
        mat_crate2 = mat_crate1.variation(specular_texture="intentionallywrongpath.png")
        self.add_entity(Cube(parent_app=self, shader=mat_crate2, origin=tmp + Vector3D.RIGHT * 2.2))

        self.lights.append(Light(self, position=tmp + Vector3D.RIGHT * 1.5 + Vector3D.BACKWARD * 2., radius=3., intensity=15., color="green"))
        light_cube_mat = MeshShader(unshaded=True, diffuse_color = "green")
        self.add_entity(Cube(self, origin=self.lights[-1].origin, scale=.1, shader=light_cube_mat))
        ##############################

        ####### CUSTOM SHADERS
        tmp = Vector3D.RIGHT * 8.

        mat_funky = MeshShader(injected_vert="shaders/injected/vert_warp.vert",
                                    injected_frag="shaders/injected/funky.frag",
                                diffuse_texture="res/textures/window_semitransp.png")
        self.add_entity(Cube(self, origin=tmp + Vector3D.FORWARD * 5., shader=mat_funky))

        map_mat = MeshShader(injected_frag="shaders/injected/rotation.frag",
                                   diffuse_texture="res/textures/map.jpg")
        self.add_entity(Sphere(parent_app=self, origin=tmp, shader=map_mat, scale=2.))
        ##############################

        ###### OBJ LOADING
        tmp = Vector3D.LEFT * 8. + Vector3D.FORWARD * 3.

        mat_bunny = MeshShader(diffuse_color = "yellow")
        self.add_entity(DrawnEntity(mesh="res/models/bunny.obj", parent_app=self,
                                    origin=tmp, rotation=Vector3D.UP * -math.tau/4.,shader=mat_bunny))
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
        ##############################

        self.animate = False
        if not self.animate:
            camera_params = {"ratio": ratio, "fov": math.tau / 6., "near": .1, "far": 80.}
            self.camera = self.add_entity(FPCamera(self, look_at=Vector3D.FORWARD, sensitivity=80., **camera_params))
        else:
            self.camera = Camera(self, eye=Vector3D.UP * 6. + Vector3D.BACKWARD * 14.,
                                 look_at=Vector3D.FORWARD * .001, fov=math.tau / 6.)

    def update(self, delta):
        if self.animate and not self.bezier1.done:
            pos1, _dir = self.bezier1.interpolate_next(delta * .1)
            self.camera.look_at(pos1, new_origin=pos1 * .8)

    def display(self):
        pass

    def handle_event(self, event):
        return False


if __name__ == '__main__':
    prog = Assignment5()
    prog.run()