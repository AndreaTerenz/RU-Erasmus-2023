from abc import abstractmethod, ABC
import numpy as np
from oven_engine_3D.utils.geometry import Vector3D

class Mesh(ABC):
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

    CUBE_UV_ARRAY = np.array([0., 0.,
                              0., 1.,
                              1., 1.,
                              1., 0., ] * 6)

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
                                     [-1, 0, 1],
                                     [1, 0, 1],
                                     [1, 0, -1]])
    PLANE_NORMAL_ARRAY = np.array([list(Vector3D.UP)] * 4)
    PLANE_UV_ARRAY = np.array([0., 0., 0., 1., 1., 1., 1., 0.])

    @property
    def vertex_positions(self):
        return PlaneMesh.PLANE_POSITION_ARRAY

    @property
    def vertex_normals(self):
        return PlaneMesh.PLANE_NORMAL_ARRAY

    @property
    def vertex_uvs(self):
        return PlaneMesh.PLANE_UV_ARRAY