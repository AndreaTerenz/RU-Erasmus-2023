import math

import numpy as np
from OpenGL.GL import *
from pygame import Color

from oven_engine_3D.matrices import ModelMatrix
from oven_engine_3D.shaders import MeshShader
from oven_engine_3D.utils.geometry import Vector3D, Vector2D, euler_from_vectors

CUBE_POSITION_ARRAY = np.array(
        # back
        [[-1, -1, -1],
         [-1,  1, -1],
         [ 1,  1, -1],
         [ 1, -1, -1],
        # front
        [-1, -1,  1],
        [-1,  1,  1],
        [ 1,  1,  1],
        [ 1, -1,  1],
        # bottom
        [-1, -1, -1],
        [ 1, -1, -1],
        [ 1, -1,  1],
        [-1, -1,  1],
        # top
        [-1,  1, -1],
        [ 1,  1, -1],
        [ 1,  1,  1],
        [-1,  1,  1],
        # left
        [-1, -1, -1],
        [-1, -1,  1],
        [-1,  1,  1],
        [-1,  1, -1],
        # right
        [ 1, -1, -1],
        [ 1, -1,  1],
        [ 1,  1,  1],
        [ 1,  1, -1]])*.5

CUBE_NORMAL_ARRAY = np.array([list(Vector3D.FORWARD)]*4+
                              [list(Vector3D.BACKWARD)]*4+
                              [list(Vector3D.DOWN)]*4+
                              [list(Vector3D.UP)]*4+
                              [list(Vector3D.LEFT)]*4+
                              [list(Vector3D.RIGHT)]*4)

PLANE_POSITION_ARRAY = np.array([[-1, 0, -1],
                                 [-1, 0,  1],
                                 [ 1, 0,  1],
                                 [ 1, 0, -1]])*.5
PLANE_NORMAL_ARRAY = np.array([list(Vector3D.UP)]*4)

def draw_cube(camera, light, shader,
              ambient_color = (1., 1., 1., 1.),
              offset: Vector3D = Vector3D.ZERO, rotation: Vector3D = None, scale:Vector3D = None, model_matrix: ModelMatrix = None):

    draw_mesh(camera, light, shader, 4, 6, ambient_color, offset, scale, rotation, model_matrix)


def draw_plane(camera, light, shader,
               ambient_color = (1., 1., 1., 1.),
               normal = None, offset = Vector3D.ZERO, scale:[float|Vector2D] = 1., rotation: Vector3D = Vector3D.ZERO, model_matrix = None):
    if model_matrix is None:
        if normal is not None:
            rotation = Vector3D(*euler_from_vectors(normal))

        if type(scale) in [int, float]:
            scale = Vector3D(scale, 1., scale)
        else:
            scale = Vector3D(scale.x, 1., scale.y)

    draw_mesh(camera, light, shader, 4, 1, ambient_color, offset, scale, rotation, model_matrix)

def draw_mesh(camera, light, shader, verts_per_face, face_count,
              ambient_color = (1., 1., 1., 1.),
              offset: Vector3D = Vector3D.ZERO, scale:Vector3D = Vector3D.ONE, rotation: Vector3D = Vector3D.ZERO, model_matrix = None):
    if model_matrix is None:
        model_matrix = ModelMatrix.from_transformations(offset, rotation, scale)

    shader.use()

    shader.set_attribute_buffers()

    shader.set_model_matrix(model_matrix)
    shader.set_camera_uniforms(camera)
    shader.set_light_uniforms(light)
    shader.set_ambient(ambient_color)

    for k in range(face_count):
        glDrawArrays(GL_TRIANGLE_FAN, k*verts_per_face, 4)

    glBindBuffer(GL_ARRAY_BUFFER, 0)