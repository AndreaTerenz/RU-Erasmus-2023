import math
import pygame as pg

from oven_engine_3D.camera import FPCamera, Camera
from oven_engine_3D.entities import Entity
from oven_engine_3D.utils.geometry import Vector3D


class Player:

    def __init__(self, parent_app, camera_params: dict, origin=Vector3D.ZERO, rot_y = math.tau/4., height=1., coll_radius=1.):
        v_offset = Vector3D.UP * height
        look_at = (Vector3D.FORWARD + v_offset).rotate(Vector3D.UP, rot_y)

        self.forward = look_at.x0z.normalized
        self.camera = FPCamera(parent_app, eye=origin + v_offset, look_at=look_at, sensitivity=100., speed=10., **camera_params)

        self.maze = parent_app.maze
        self.collision_radius = coll_radius

    @property
    def position(self):
        return self.camera.origin

    def update(self, delta):
        # Check if the player is in a wall
        pos = self.position
        i, j = int(pos.z), int(pos.x)
        if self.maze[i][j] == 1:
            # If so, move the player back
            self.camera.translate(-self.forward * delta * self.camera.speed)

        # Check if the player is colliding with a wall
        """for i in range(self.maze.shape[0]):
            for j in range(self.maze.shape[1]):
                if self.maze[i][j] == 1:
                    # If so, move the player back
                    wall_pos = Vector3D(j, 0, i)
                    dist = (wall_pos - pos).length
                    if dist < self.collision_radius:
                        self.camera.translate(-self.forward * delta * self.camera.speed)"""

        # Update the camera
        self.camera.update(delta)


    def handle_event(self, ev):
        pass