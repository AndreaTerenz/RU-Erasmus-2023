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

def draw_cube(camera, offset: Vector3D = Vector3D.ZERO, color = None, rotation: Vector3D = None, scale:Vector3D = None, shader = None, model_matrix: ModelMatrix = None):
    if model_matrix is None:
        model_matrix = ModelMatrix.from_transformations(offset, rotation, scale)

    if shader is None:
        shader = MeshShader()
        shader.set_position_attribute(CUBE_POSITION_ARRAY)
        shader.set_normal_attribute(CUBE_NORMAL_ARRAY)

    shader.use()
    shader.set_model_matrix(model_matrix.values)
    shader.get_projview(camera)

    if color is not None:
        shader.set_solid_color(color[0], color[1], color[2])

    for k in range(6):
        glDrawArrays(GL_TRIANGLE_FAN, k*4, 4)

def draw_plane(camera, offset: Vector3D = Vector3D.ZERO, color = None, rotation: Vector3D = Vector3D.ZERO, scale:Vector3D = Vector3D.ONE, shader = None, model_matrix = None):
    if model_matrix is None:
        model_matrix = ModelMatrix.from_transformations(offset, rotation, scale)

    if shader is None:
        shader = MeshShader()

    shader.set_position_attribute(np.array([-1, 0, -1, -1, 0, 1, 1, 0, 1, 1, 0, -1]))
    shader.set_normal_attribute(np.array([0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1]))
    shader.set_model_matrix(model_matrix.matrix)
    shader.get_projview(camera)

    if color is not None:
        shader.set_solid_color(color[0], color[1], color[2])

    shader.use()
    glDrawArrays(GL_TRIANGLE_FAN, 0, 4)