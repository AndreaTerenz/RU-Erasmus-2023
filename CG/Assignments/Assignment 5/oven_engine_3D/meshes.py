from abc import abstractmethod, ABC
from itertools import chain
from OpenGL.GL import *
import numpy as np
from oven_engine_3D.utils.geometry import Vector3D

from oven_engine_3D.utils.matrices import ModelMatrix


class Mesh(ABC):
    def __init__(self, verts_per_face, face_count):
        tmp = [(*p, *n, *u) for p, n, u in zip(self.vertex_positions, self.vertex_normals, self.vertex_uvs)]
        tmp = list(chain.from_iterable(tmp))

        self.__vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.__vbo)
        glBufferData(GL_ARRAY_BUFFER, np.array(tmp, dtype="float32"), GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        self.verts_per_face = verts_per_face
        self.face_count = face_count

    def draw(self, app_context: 'BaseApp3D', shader,
                  offset: Vector3D = Vector3D.ZERO, scale: Vector3D = Vector3D.ONE, rotation: Vector3D = Vector3D.ZERO,
                  model_matrix=None):
        if model_matrix is None:
            model_matrix = ModelMatrix.from_transformations(offset, rotation, scale)

        shader.use()

        shader.set_mesh_attributes(self.vbo)
        shader.set_model_matrix(model_matrix)

        camera = app_context.camera
        lights = app_context.lights

        shader.set_uniform_int(len(lights), "u_light_count")
        shader.set_light_uniforms(lights)

        shader.set_camera_uniforms(camera)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        for k in range(self.face_count):
            glDrawArrays(GL_TRIANGLE_FAN, k * self.verts_per_face, 4)

        glBindBuffer(GL_ARRAY_BUFFER, 0)

    @property
    def vbo(self):
        return self.__vbo

    @property
    @abstractmethod
    def vertex_positions(self):
        return []

    @property
    @abstractmethod
    def vertex_normals(self):
        return []

    @property
    @abstractmethod
    def vertex_uvs(self):
        return []

class CubeMesh(Mesh):
    CUBE_POSITION_ARRAY = np.array(
        # back
        [[1, -1, -1],
         [1, 1, -1],
         [-1, 1, -1],
         [-1, -1, -1],
         # front
         [-1, -1, 1],
         [-1, 1, 1],
         [1, 1, 1],
         [1, -1, 1],
         # bottom
         [-1, -1, -1],
         [-1, -1, 1],
         [1, -1, 1],
         [1, -1, -1],
         # top
         [-1, 1, 1],
         [-1, 1, -1],
         [1, 1, -1],
         [1, 1, 1],
         # left
         [-1, -1, -1],
         [-1, 1, -1],
         [-1, 1, 1],
         [-1, -1, 1],
         # right
         [1, -1, 1],
         [1, 1, 1],
         [1, 1, -1],
         [1, -1, -1], ])

    CUBE_NORMAL_ARRAY = np.array([list(Vector3D.BACKWARD)] * 4 +
                                 [list(Vector3D.FORWARD)] * 4 +
                                 [list(Vector3D.DOWN)] * 4 +
                                 [list(Vector3D.UP)] * 4 +
                                 [list(Vector3D.LEFT)] * 4 +
                                 [list(Vector3D.RIGHT)] * 4)

    CUBE_UV_ARRAY = np.array([[0., 0.],
                              [0., 1.],
                              [1., 1.],
                              [1., 0.], ] * 6)

    def __init__(self):
        super().__init__(4, 6)

    @property
    def vertex_positions(self):
        return CubeMesh.CUBE_POSITION_ARRAY

    @property
    def vertex_normals(self):
        return CubeMesh.CUBE_NORMAL_ARRAY

    @property
    def vertex_uvs(self):
        return CubeMesh.CUBE_UV_ARRAY


class PlaneMesh(Mesh):
    PLANE_POSITION_ARRAY = np.array([[-1, 0, -1],
                                     [1, 0, -1],
                                     [1, 0, 1],
                                     [-1, 0, 1],])
    PLANE_NORMAL_ARRAY = np.array([list(Vector3D.UP)] * 4)
    PLANE_UV_ARRAY = np.array([[0., 0.],
                               [0., 1.],
                               [1., 1.],
                               [1., 0.]])

    def __init__(self):
        super().__init__(4, 1)

    @property
    def vertex_positions(self):
        return PlaneMesh.PLANE_POSITION_ARRAY

    @property
    def vertex_normals(self):
        return PlaneMesh.PLANE_NORMAL_ARRAY

    @property
    def vertex_uvs(self):
        return PlaneMesh.PLANE_UV_ARRAY