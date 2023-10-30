import pygame as pg
from pygame import Color

from oven_engine_3D.camera import FPCamera
from oven_engine_3D.entities import Entity
from oven_engine_3D.light import Light
from oven_engine_3D.utils.geometry import Vector3D, Vector2D


class PlayerLight(Light):
    def __init__(self, app, player, color):
        super().__init__(parent_app=app, position=player.position, color=color, radius=32.)

        self.player = player

    def update(self, delta):
        self.translate_to(self.player.camera.origin)

class Player(Entity):

    def __init__(self, parent_app, camera_params: dict, origin = Vector3D.ZERO, rot_y=0., height=1., speed=5.):

        super().__init__(parent_app, origin)

        v_offset = Vector3D.UP * height
        look_at = (Vector3D.FORWARD + v_offset).rotate(Vector3D.UP, rot_y) + origin

        self.forward_dir = look_at.x0z.normalized
        self.speed = speed
        self.camera = FPCamera(parent_app, eye=origin + v_offset, look_at=look_at, sensitivity=80., **camera_params)
        self.light = PlayerLight(parent_app, self, Color("white"))

        self.slide_keys = {
            pg.K_w: Vector3D.FORWARD,
            pg.K_s: Vector3D.BACKWARD,
            pg.K_a: Vector3D.RIGHT,
            pg.K_d: Vector3D.LEFT,
            pg.K_LSHIFT: Vector3D.UP,
            pg.K_LCTRL: Vector3D.DOWN,
        }

        parent_app.add_keys(self.slide_keys.keys())

    @property
    def position(self):
        return self.camera.view_matrix.eye

    def _update(self, delta):
        self.move(delta)
        self.camera.update(delta)
        self.light.update(delta)

    def move(self, delta):
        slide_dir = Vector3D.ZERO
        maze_dir = Vector2D.ZERO
        for key, _dir in self.slide_keys.items():
            state = self.parent_app.is_key_pressed(key)
            fact = 1. if state else 0.
            slide_dir += _dir * fact
            maze_dir += _dir.xz * fact

            if fact != 0.:
                pass

        slide_dir = slide_dir.normalized

        if slide_dir != Vector3D.ZERO:
            slide_dir = slide_dir.rotate(Vector3D.UP, self.camera.y_rot).normalized
            sp = delta * self.speed

            slide_offset = slide_dir * sp

            # move player
            self.camera.translate(slide_offset)

    def handle_event(self, ev):
        self.camera.handle_event(ev)