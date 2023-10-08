import math

import numpy as np
from OpenGL.GL import *
from pygame import Color

from Control3DBase.Matrices import ModelMatrix
from Control3DBase.Shaders import MeshShader
from Control3DBase.utils.geometry import Vector3D, Vector2D, euler_from_vectors

CUBE_POSITION_ARRAY = np.array(
        # back
        [-1, -1, -1,
         -1,  1, -1,
          1,  1, -1,
          1, -1, -1,
        # front
         -1, -1,  1,
         -1,  1,  1,
          1,  1,  1,
          1, -1,  1,
        # bottom
         -1, -1, -1,
          1, -1, -1,
          1, -1,  1,
         -1, -1,  1,
        # top
         -1,  1, -1,
          1,  1, -1,
          1,  1,  1,
         -1,  1,  1,
        # left
         -1, -1, -1,
         -1, -1,  1,
         -1,  1,  1,
         -1,  1, -1,
        # right
          1, -1, -1,
          1, -1,  1,
          1,  1,  1,
          1,  1, -1])*.5

CUBE_NORMAL_ARRAY = np.array([0.0, 0.0, 1.0]*4 + [0.0, 0.0, -1.0,]*4 + [0.0, -1.0, 0.0,]*4 + [0.0, 1.0, 0.0]*4+[-1.0, 0.0, 0.0]*4 + [1.0, 0.0, 0.0]*4)

PLANE_POSITION_ARRAY = np.array([-1, 0, -1, -1, 0, 1, 1, 0, 1, 1, 0, -1])
PLANE_NORMAL_ARRAY = np.array([0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0])

def draw_cube(camera, light, shader,
              ambient_color = (1., 1., 1., 1.),
              offset: Vector3D = Vector3D.ZERO, rotation: Vector3D = None, scale:Vector3D = None, model_matrix: ModelMatrix = None, set_poss_norms = True):
    poss, norms = None, None
    if set_poss_norms:
        poss, norms = CUBE_POSITION_ARRAY, CUBE_NORMAL_ARRAY

    draw_mesh(camera, light, shader, 4, 6, poss, norms, ambient_color, offset, scale, rotation, model_matrix)


def draw_plane(camera, light, shader,
               ambient_color = (1., 1., 1., 1.),
               normal = None, offset = Vector3D.ZERO, scale:[float|Vector2D] = 1., rotation: Vector3D = Vector3D.ZERO, model_matrix = None, set_poss_norms = True):
    if model_matrix is None:
        if normal is not None:
            rotation = Vector3D(*euler_from_vectors(normal))

        if type(scale) in [int, float]:
            scale = Vector3D(scale, 1., scale)
        else:
            scale = Vector3D(scale.x, 1., scale.y)

    poss, norms = None, None
    if set_poss_norms:
        poss, norms = PLANE_POSITION_ARRAY, PLANE_NORMAL_ARRAY

    draw_mesh(camera, light, shader, 4, 1, positions=poss, normals=norms, ambient_color=ambient_color, offset=offset, scale=scale, rotation=rotation, model_matrix=model_matrix)

def draw_mesh(camera, light, shader, verts_per_face, face_count, positions=None, normals=None,
              ambient_color = (1., 1., 1., 1.),
              offset: Vector3D = Vector3D.ZERO, scale:Vector3D = Vector3D.ONE, rotation: Vector3D = Vector3D.ZERO, model_matrix = None):
    if model_matrix is None:
        model_matrix = ModelMatrix.from_transformations(offset, rotation, scale)

    shader.use()

    if positions is not None:
        shader.set_position_attribute(positions)
    if normals is not None:
        shader.set_normal_attribute(normals)

    shader.set_model_matrix(model_matrix.values)

    shader.set_camera_uniforms(camera)
    shader.set_light_uniforms(light)

    shader.set_ambient(ambient_color)

    for k in range(face_count):
        glDrawArrays(GL_TRIANGLE_FAN, k*verts_per_face, 4)