import math
import pygame as pg
from pygame import Color

from oven_engine_3D.camera import FPCamera, Camera
from oven_engine_3D.entities import Entity
from oven_engine_3D.light import Light
from oven_engine_3D.utils.geometry import Vector3D, Vector2D


class PlayerLight(Light):
    def __init__(self, app, player, color):
        super().__init__(parent_app=app, position=player.position, color=color, radius=12.)

        self.player = player

    def update(self, delta):
        self.translate_to(self.player.camera.origin)

class Player(Entity):

    def __init__(self, parent_app, camera_params: dict, maze_pos=Vector3D.ZERO, rot_y=0., height=1.,
                 coll_radius=5.):

        origin = parent_app.maze_to_world(maze_pos) #* 2.

        super().__init__(parent_app, origin)

        v_offset = Vector3D.UP * height
        look_at = (Vector3D.FORWARD + v_offset).rotate(Vector3D.UP, rot_y) + origin

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

        self.maze_pos = maze_pos

        print("PLAYER STARTS AT: ", self.maze_pos)

        parent_app.add_keys(self.slide_keys.keys())

    @property
    def position(self):
        return self.camera.view_matrix.eye

    def _update(self, delta):


        self.move(delta)
        self.camera.update(delta)
        self.light.update(delta)

    def check_collisions_at(self, p):
        maze_pos = self.parent_app.world_to_maze(p) / 2.
        print("DIOCANE ", maze_pos)
        # Get list of surrounding cells that are walls
        wall_norms = []
        for dir in Vector2D.CARDINALS:
            cell = maze_pos + dir
            if self.parent_app.cell_state_at(cell) == 0:
                print(cell, end=" ")
                wall_norms.append(-dir)
        if len(wall_norms) > 0:
            print(" | ", end="")


        output = Vector3D.ZERO
        # Check if player is colliding with any of the surrounding walls
        for n in wall_norms:
            other = maze_pos - n

            # Distance from center of current cell
            dist = (p.xz - maze_pos).length

            if dist >= self.collision_radius * 2:
                print(other, end=" ")
                output += n.x0y

        if len(wall_norms) > 0:
            print()

        return output.normalized

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

            there = self.parent_app.world_to_maze(self.position + slide_dir * self.collision_radius * delta)# * self.collision_radius)

            if self.parent_app.cell_state_at(there) != 0:

                self.camera.translate(slide_offset)


    def handle_event(self, ev):
        self.camera.handle_event(ev)