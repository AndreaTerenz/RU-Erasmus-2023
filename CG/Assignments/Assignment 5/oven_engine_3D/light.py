import pygame as pg

from oven_engine_3D.entities import Entity
from oven_engine_3D.utils.geometry import Vector3D

BASE_INTENSITY = 2.

class Light(Entity):
    def __init__(self, parent_app, position, color, radius=0.,
                 ambient_color="black", intensity=1., attenuation=(1., .2, 0.)):
        super().__init__(parent_app, origin=position)

        self.color = color
        self.radius = radius
        self.ambient = ambient_color
        self.intensity = intensity * BASE_INTENSITY
        self.attenuation = attenuation

    def _update(self, delta):
        pass

    def handle_event(self, ev):
        pass

class MovableLight(Light):
    def __init__(self, parent_app, position, color, radius=0.):
        super().__init__(parent_app, position, color, radius=radius)

        self.keys_to_dir = {
            pg.K_k: Vector3D.FORWARD,
            pg.K_i: Vector3D.BACKWARD,
            pg.K_j: Vector3D.LEFT,
            pg.K_l: Vector3D.RIGHT,
            pg.K_u: Vector3D.UP,
            pg.K_o: Vector3D.DOWN,
        }

    def _update(self, delta):
        light_dir = Vector3D.ZERO
        for key, _dir in self.keys_to_dir.items():
            state = self.parent_app.keys_states[key]
            fact = 1. if state else 0.
            light_dir += _dir * fact

        if light_dir != Vector3D.ZERO:
            self.origin += light_dir.normalized * delta * 4.

    def handle_event(self, ev):
        pass
