import numpy as np
from OpenGL.GL import *

from Control3DBase.Matrices import ModelMatrix
from Control3DBase.Shaders import MeshShader
from Control3DBase.utils.geometry import Vector3D

CUBE_POSITION_ARRAY = np.array(
        [-1, -1, -1,
         -1,  1, -1,
          1,  1, -1,
          1, -1, -1,
         -1, -1,  1,
         -1,  1,  1,
          1,  1,  1,
          1, -1,  1,
         -1, -1, -1,
          1, -1, -1,
          1, -1,  1,
         -1, -1,  1,
         -1,  1, -1,
          1,  1, -1,
          1,  1,  1,
         -1,  1,  1,
         -1, -1, -1,
         -1, -1,  1,
         -1,  1,  1,
         -1,  1, -1,
          1, -1, -1,
          1, -1,  1,
          1,  1,  1,
          1,  1, -1])*.5

CUBE_NORMAL_ARRAY = np.array( [ 0.0,  0.0, -1.0] * 6 +
                             [ 0.0,  0.0,  1.0] * 6 +
                             [ 0.0, -1.0,  0.0] * 6 +
                             [ 0.0,  1.0,  0.0] * 6 +
                             [-1.0,  0.0,  0.0] * 6 +
                             [ 1.0,  0.0,  0.0] * 6)

PLANE_POSITION_ARRAY = np.array([-1, 0, -1, -1, 0, 1, 1, 0, 1, 1, 0, -1])
PLANE_NORMAL_ARRAY = np.array([0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1])

def draw_cube(camera, offset: Vector3D = Vector3D.ZERO, color = None, rotation: Vector3D = None, scale:Vector3D = None, shader = None, model_matrix: ModelMatrix = None):
    draw_mesh(camera, CUBE_POSITION_ARRAY, CUBE_NORMAL_ARRAY, 4, 6, color, shader, offset, scale, rotation, model_matrix)

def draw_plane(camera, color = None, shader=None, offset: Vector3D = Vector3D.ZERO, scale:Vector3D = Vector3D.ONE, rotation: Vector3D = Vector3D.ZERO, model_matrix = None):
    draw_mesh(camera, PLANE_POSITION_ARRAY, PLANE_NORMAL_ARRAY, 4, 1, color, shader, offset, scale, rotation, model_matrix)

def draw_mesh(camera, positions, normals, verts_per_face, face_count, color = None, shader=None, offset: Vector3D = Vector3D.ZERO, scale:Vector3D = Vector3D.ONE, rotation: Vector3D = Vector3D.ZERO, model_matrix = None):
    if model_matrix is None:
        model_matrix = ModelMatrix.from_transformations(offset, rotation, scale)

    if shader is None:
        shader = MeshShader()

    shader.use()

    shader.set_position_attribute(positions)
    shader.set_normal_attribute(normals)
    shader.set_model_matrix(model_matrix.values)
    shader.set_projection_matrix(camera.projection_matrix.values)
    shader.set_view_matrix(camera.view_matrix.values)

    if color is not None:
        shader.set_solid_color(color[0], color[1], color[2])

    for k in range(face_count):
        glDrawArrays(GL_TRIANGLE_FAN, k*verts_per_face, 4)