import math
import pygame as pg
import numpy as np

from pygame import Color

from game_entities import Player
from oven_engine_3D.base_app import BaseApp3D
from oven_engine_3D.camera import FPCamera
from oven_engine_3D.entities import Cube, Plane
from oven_engine_3D.shaders import MeshShader
from oven_engine_3D.utils.geometry import Vector3D, Vector2D
from oven_engine_3D.utils.gl3d import PLANE_POSITION_ARRAY, PLANE_NORMAL_ARRAY, CUBE_POSITION_ARRAY, CUBE_NORMAL_ARRAY

from OpenGL.GL import *
from OpenGL.GLU import *

def read_maze(file_path = "test.maze"):
    with open(file_path, "r") as f:
        lines = f.readlines()

    lines = [line.strip() for line in lines]

    # convert maze to numpy array
    return np.array([list(line) for line in lines], dtype=np.int8)

class Assignment3(BaseApp3D):
    EMPTY_CELL = 1
    START_CELL = 2

    def __init__(self):
        super().__init__(fullscreen=True, ambient_color=Color("white"), clear_color=Color(30, 30, 30), update_camera=False)

        self.maze = read_maze(file_path="test.maze")

        ratio = self.win_size.aspect_ratio
        self.player = Player(self, camera_params={"ratio": ratio, "fov": math.tau/6., "near": .5, "far": 100.})

        self.camera = self.player.camera
        self.light = self.player.light

        self.objects.append(self.player)

        self.maze = read_maze().transpose()

        floor_mat = MeshShader(positions=PLANE_POSITION_ARRAY, normals=PLANE_NORMAL_ARRAY,
                                diffuse_color=Color("yellow"))
        wall_mat = MeshShader(diffuse_color=Color("blue"), vbo=floor_mat.pos_vbo)
        center = Vector2D(*self.maze.shape).yx

        # Create a Plane for each wall in the maze
        for i in range(self.maze.shape[0]):
            for j in range(self.maze.shape[1]):
                maze_pos = Vector2D(i,j)
                pos = (maze_pos*2 - center).x0y

                if self.cell_state_at(maze_pos) == Assignment3.EMPTY_CELL:
                    plane = Plane(self, origin=pos, shader=floor_mat, scale=Vector3D.ONE)
                    self.objects.append(plane)
                else:
                    # Check which surrounding cells are walls and
                    # create a Plane for each of them
                    for _dir in Vector2D.CARDINALS:
                        new_pos = maze_pos + _dir

                        # check that new_pos is valid
                        if not self.is_valid_pos(new_pos):
                            continue

                        if self.cell_state_at(new_pos) == Assignment3.EMPTY_CELL:
                            _dir = _dir.x0y
                            wall_pos = pos + Vector3D.UP + _dir
                            wall_norm = (-_dir)

                            # Create the plane
                            plane = Plane(self, origin=wall_pos, shader=wall_mat, normal=wall_norm, scale=Vector3D.ONE)
                            self.objects.append(plane)

    def cell_state_at(self, pos: Vector2D):
        return self.maze[int(pos.x)][int(pos.y)]

    def is_valid_pos(self, pos:Vector2D):
        return 0 <= pos.x < self.maze.shape[0] and 0 <= pos.y < self.maze.shape[1]

    def update(self, delta):
        pass

    def display(self):
        pass

    def handle_event(self, event):
        if event.type == pg.MOUSEMOTION:
            self.mouse_delta = Vector2D(event.rel) / self.win_size
            self.mouse_delta = self.mouse_delta.snap(.005)

        return False


if __name__ == '__main__':
    prog = Assignment3()
    prog.run()