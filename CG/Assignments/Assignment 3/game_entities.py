import math
import pygame as pg
from pygame import Color

from oven_engine_3D.camera import FPCamera, Camera
from oven_engine_3D.entities import Entity
from oven_engine_3D.light import Light
from oven_engine_3D.utils.geometry import Vector3D

class PlayerLight(Light):
    def __init__(self, app, player, color):
        super().__init__(parent_app=app, position=player.position, color=color)

        self.player = player

    def update(self, delta):
        self.translate_to(self.player.camera.origin)

class Player(Entity):

    def __init__(self, parent_app, camera_params: dict, origin=Vector3D.ZERO, rot_y=math.tau / 4., height=1.,
                 coll_radius=1.):
        super().__init__(parent_app, origin)

        v_offset = Vector3D.UP * height
        look_at = (Vector3D.FORWARD + v_offset).rotate(Vector3D.UP, rot_y)

        self.forward_dir = look_at.x0z.normalized
        self.speed = 7.
        self.camera = FPCamera(parent_app, eye=origin + v_offset, look_at=look_at, sensitivity=80., **camera_params)
        self.light = PlayerLight(parent_app, self, Color("white"))

        self.maze = parent_app.maze
        self.collision_radius = coll_radius

        self.slide_keys = {
            pg.K_w: Vector3D.FORWARD,
            pg.K_s: Vector3D.BACKWARD,
            pg.K_a: Vector3D.RIGHT,
            pg.K_d: Vector3D.LEFT,
        }

        parent_app.add_keys(self.slide_keys.keys())

    @property
    def position(self):
        return self.camera.origin

    def _update(self, delta):
        """# Check if the player is in a wall
        pos = self.position
        i, j = int(pos.z), int(pos.x)
        if self.maze[i][j] == 1:
            # If so, move the player back
            self.camera.translate(-self.forward * delta * self.camera.speed)

        # Check if the player is colliding with a wall
        for i in range(self.maze.shape[0]):
            for j in range(self.maze.shape[1]):
                if self.maze[i][j] == 1:
                    # If so, move the player back
                    wall_pos = Vector3D(j, 0, i)
                    dist = (wall_pos - pos).length
                    if dist < self.collision_radius:
                        self.camera.translate(-self.forward * delta * self.camera.speed)"""

        self.move(delta)
        self.camera.update(delta)
        self.light.update(delta)

    def move(self, delta):
        slide_dir = Vector3D.ZERO
        for key, _dir in self.slide_keys.items():
            state = self.parent_app.is_key_pressed(key)
            fact = 1. if state else 0.
            slide_dir += _dir * fact

        slide_dir = slide_dir.normalized
        if slide_dir != Vector3D.ZERO:
            slide_dir = slide_dir.rotate(Vector3D.UP, self.camera.y_rot)
            slide_offset = slide_dir * delta * self.speed

            self.camera.translate(slide_offset)


    def handle_event(self, ev):
        self.camera.handle_event(ev)