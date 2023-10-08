import math
import pygame as pg
from pygame import Color

from oven_engine_3D.base_app import BaseApp3D
from oven_engine_3D.camera import FPCamera
from oven_engine_3D.entities import Cube, Plane
from oven_engine_3D.light import Light
from oven_engine_3D.utils.geometry import Vector3D, Vector2D


class Assignment3(BaseApp3D):
    def __init__(self):
        super().__init__(fullscreen=True, ambient_color=Color("red"))

        ratio = self.win_size.aspect_ratio
        self.camera = FPCamera(self, eye=Vector3D(-2., 1., 2.) * 5., look_at=Vector3D.ZERO, ratio=ratio, fov=math.tau/6., near=.5, far=100)

        self.light = Light(Vector3D(0., 0., 0.), (1., 1., 1.))

        self.light_cube = Cube(self)
        self.light_cube.scale_by(.1)
        self.light_cube.shader.set_material_diffuse(self.light.color)
        self.light_cube.shader.set_unshaded(True)
        self.light_cube.translate_to(self.light.position)

        dist = 3.
        self.objects = [
            Plane(self, origin=Vector3D(0., -5., 0.), color=(.5, .5, .5), scale=Vector3D.ONE*10.),
            Plane(self, origin=Vector3D(0., 5., -10.), color=(.5, .5, .5), normal=Vector3D.FORWARD, scale=Vector3D.ONE*10.),
            Plane(self, origin=Vector3D(10., 5., 0.), color=(.5, .5, .5), normal=Vector3D.LEFT, scale=Vector3D.ONE*10.),

            Cube(self, color=Color("blue"), origin=dist * Vector3D.FORWARD),
            Cube(self, color=Color("blue"), origin=dist * Vector3D.BACKWARD),
            Cube(self, color=Color("red"), origin=dist * Vector3D.RIGHT),
            Cube(self, color=Color("red"), origin=dist * Vector3D.LEFT),
            Cube(self, color=Color("green"), origin=dist * Vector3D.UP),
            Cube(self, color=Color("green"), origin=dist * Vector3D.DOWN),

            self.light_cube,
        ]

        self.objects[4].rotate(math.tau/8.)
        self.objects[6].rotate(math.tau/8.)
        self.objects[8].rotate(math.tau/8.)

    def update(self, delta):
        self.camera.update(delta)

        # Update light position based on input
        light_dir = Vector3D.ZERO
        for key, _dir in self.light_movement_keys.items():
            state = self.keys_states[key]
            fact = 1. if state else 0.
            light_dir += _dir * fact

        if light_dir != Vector3D.ZERO:
            self.light.position += light_dir.normalized * delta * 4.
            self.light_cube.translate_to(self.light.position)

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