import numpy as np
from OpenGL.GL import *
from pygame import Color

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

CUBE_NORMAL_ARRAY = np.array([0.0, 0.0, -1.0,
                            0.0, 0.0, -1.0,
                            0.0, 0.0, -1.0,
                            0.0, 0.0, -1.0,
                            0.0, 0.0, 1.0,
                            0.0, 0.0, 1.0,
                            0.0, 0.0, 1.0,
                            0.0, 0.0, 1.0,
                            0.0, -1.0, 0.0,
                            0.0, -1.0, 0.0,
                            0.0, -1.0, 0.0,
                            0.0, -1.0, 0.0,
                            0.0, 1.0, 0.0,
                            0.0, 1.0, 0.0,
                            0.0, 1.0, 0.0,
                            0.0, 1.0, 0.0,
                            -1.0, 0.0, 0.0,
                            -1.0, 0.0, 0.0,
                            -1.0, 0.0, 0.0,
                            -1.0, 0.0, 0.0,
                            1.0, 0.0, 0.0,
                            1.0, 0.0, 0.0,
                            1.0, 0.0, 0.0,
                            1.0, 0.0, 0.0])

PLANE_POSITION_ARRAY = np.array([-1, 0, -1, -1, 0, 1, 1, 0, 1, 1, 0, -1])
PLANE_NORMAL_ARRAY = np.array([0, -1, 0, 0, -1, 0, 0, -1, 0, 0, -1, 0])

def draw_cube(camera, light, shader, ambient_color = (1., 1., 1., 1.), offset: Vector3D = Vector3D.ZERO, rotation: Vector3D = None, scale:Vector3D = None, model_matrix: ModelMatrix = None):
    draw_mesh(camera, light, shader, CUBE_POSITION_ARRAY, CUBE_NORMAL_ARRAY, 4, 6, ambient_color, offset, scale, rotation, model_matrix)

def draw_plane(camera, light, shader, ambient_color = (1., 1., 1., 1.), offset: Vector3D = Vector3D.ZERO, scale:Vector3D = Vector3D.ONE, rotation: Vector3D = Vector3D.ZERO, model_matrix = None):
    draw_mesh(camera, light, shader, PLANE_POSITION_ARRAY, PLANE_NORMAL_ARRAY, 4, 1, ambient_color, offset, scale, rotation, model_matrix)

def draw_mesh(camera, light, shader, positions, normals, verts_per_face, face_count, ambient_color = (1., 1., 1., 1.), offset: Vector3D = Vector3D.ZERO, scale:Vector3D = Vector3D.ONE, rotation: Vector3D = Vector3D.ZERO, model_matrix = None):
    if model_matrix is None:
        model_matrix = ModelMatrix.from_transformations(offset, rotation, scale)

    shader.use()

    shader.set_position_attribute(positions)
    shader.set_normal_attribute(normals)
    shader.set_model_matrix(model_matrix.values)
    shader.set_projection_matrix(camera.projection_matrix.values)
    shader.set_view_matrix(camera.view_matrix.values)

    shader.set_light_position(light.position)
    shader.set_camera_position(camera.view_matrix.eye)

    shader.set_ambient(*ambient_color)
    shader.set_light_diffuse(*light.color)
    shader.set_light_specular(*light.color)

    for k in range(face_count):
        glDrawArrays(GL_TRIANGLE_FAN, k*verts_per_face, 4)