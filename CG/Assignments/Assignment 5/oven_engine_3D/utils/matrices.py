import math
from abc import ABC

import numpy as np

from oven_engine_3D.utils.geometry import Vector3D


def set_values_in_matrix(matrix, idx_val_zip):
    for idx, val in idx_val_zip:
        matrix[idx] = val

    return matrix

class Matrix(ABC):
    def __init__(self, rows = 4, cols = 4):
        self._matrix = np.eye(rows, cols)
        self.rows = rows
        self.cols = cols

    def __eq__(self, other):
        if not isinstance(other, Matrix):
            return False

        return np.array_equal(self._matrix, other._matrix)

    @property
    def identity(self):
        return np.eye(self.rows, self.cols)

    def load_identity(self):
        self._matrix = self.identity

    def copy_matrix(self):
        return np.copy(self._matrix)

    def __str__(self):
        ret_str = ""
        counter = 0
        for _ in range(4):
            ret_str += "["
            for _ in range(4):
                ret_str += " " + str(self._matrix[counter]) + " "
                counter += 1
            ret_str += "]\n"
        return ret_str

    def add_transformation(self, other):
        other = np.array(other).reshape(4, 4)
        self._matrix = (self._matrix @ other)

    @property
    def values(self):
        return self._matrix

class ModelMatrix(Matrix):
    def __init__(self):
        super().__init__(4, 4)

        self.stack = []
        self.stack_count = 0
        self.stack_capacity = 0

    @staticmethod
    def from_transformations(offset: Vector3D, rotation: Vector3D = Vector3D.ZERO, scale:Vector3D = Vector3D.ONE):
        matrix = ModelMatrix()
        matrix.add_translation(offset)

        if rotation is not None:
            matrix.add_rotation(rotation)

        if scale is not None:
            matrix.add_scale(scale)

        return matrix

    def add_translation(self, x : [float|Vector3D], y = None, z = None):
        offset = x
        if not type(x) is Vector3D:
            offset = Vector3D(x, y, z)

        if offset == Vector3D.ZERO:
            return

        translation_matrix = set_values_in_matrix(np.eye(4).flatten(), zip([3, 7, 11], [offset.x, offset.y, offset.z]))

        self.add_transformation(translation_matrix)

    def add_rotation(self, angle_x: [float|Vector3D], angle_y = None, angle_z = None):
        if type(angle_x) is Vector3D:
            angle_x, angle_y, angle_z = angle_x.x, angle_x.y, angle_x.z

        if angle_x == angle_y == angle_z == 0.:
            return

        cx, sx = np.cos(angle_x), np.sin(angle_x)
        cy, sy = np.cos(angle_y), np.sin(angle_y)
        cz, sz = np.cos(angle_z), np.sin(angle_z)

        rot_mat_x = np.array([
            [1, 0, 0, 0],
            [0, cx, -sx, 0],
            [0, sx, cx, 0],
            [0, 0, 0, 1]
        ])

        rot_mat_y = np.array([
            [cy, 0, sy, 0],
            [0, 1, 0, 0],
            [-sy, 0, cy, 0],
            [0, 0, 0, 1]
        ])

        rot_mat_z = np.array([
            [cz, -sz, 0, 0],
            [sz, cz, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        self.add_transformation(rot_mat_x)
        self.add_transformation(rot_mat_y)
        self.add_transformation(rot_mat_z)

    def add_scale(self, x : [float|Vector3D], y = None, z = None):
        if type(x) is Vector3D:
            scale = x
        else:
            scale = Vector3D(x, y, z)

        if scale == Vector3D.ONE:
            return

        scale_matrix = set_values_in_matrix(np.eye(4).flatten(), zip([0, 5, 10], [scale.x, scale.y, scale.z]))

        self.add_transformation(scale_matrix)


# The ViewMatrix class holds the camera's coordinate frame and
# set's up a transformation concerning the camera's position
# and orientation

class ViewMatrix(Matrix):
    def __init__(self):
        super().__init__(4, 4)

        self.eye = Vector3D(0,0,0)
        self.u = Vector3D(1, 0, 0)
        self.v = Vector3D(0, 1, 0)
        self.n = Vector3D(0, 0, 1)

    def look_at(self, eye, target, up_vector = Vector3D.UP):
        self.eye = eye
        self.n = (eye - target).normalized
        self.u = up_vector.cross(self.n).normalized
        self.v = self.n.cross(self.u)

    def slide(self, del_u, del_v, del_n):
        self.eye += del_u * self.u + del_v * self.v + del_n * self.n

    def rotate_x(self, angle):
        """
        Rotates the camera around its x-axis (Pitch)
        :param angle: angle to rotate by
        """
        self.n, self.v = ViewMatrix.__rotate_axes(self.n, self.v, angle)

    def rotate_y(self, angle):
        """
        Rotates the camera around its y-axis (Yaw)
        :param angle: angle to rotate by
        """
        self.u, self.n = ViewMatrix.__rotate_axes(self.u, self.n, angle)

    def rotate_z(self, angle):
        """
        Rotates the camera around its z-axis (Roll)
        :param angle: angle to rotate by
        """
        self.u, self.v = ViewMatrix.__rotate_axes(self.u, self.v, angle)

    def rotate_global_x(self, angle):
        c = np.cos(angle)
        s = np.sin(angle)

        # Create the rotation matrix around the global x-axis
        R_x = np.array([
            [1, 0, 0, 0],
            [0, c, -s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        self.rotate_with_matrix(R_x)

    def rotate_global_y(self, angle):
        c = np.cos(angle)
        s = np.sin(angle)

        # Create the rotation matrix around the global y-axis
        R_y = np.array([
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        self.rotate_with_matrix(R_y)

    def rotate_global_z(self, angle):
        c = np.cos(angle)
        s = np.sin(angle)

        # Create the rotation matrix around the global z-axis
        R_z = np.array([
            [c, -s, 0, 0],
            [s, c, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        self.rotate_with_matrix(R_z)

    def rotate_with_matrix(self, rot_matrix):
        self.u = self.u.rotate_with_matrix(rot_matrix)
        self.v = self.v.rotate_with_matrix(rot_matrix)
        self.n = self.n.rotate_with_matrix(rot_matrix)

    @staticmethod
    def __rotate_axes(a, b, angle):
        c = np.cos(angle)
        s = np.sin(angle)
        old_a = a

        a = c * a + s * b
        b = -s * old_a + c * b

        return a, b

    @property
    def values(self):
        return np.array([[self.u.x, self.u.y, self.u.z, -self.eye.dot(self.u)],
                [self.v.x, self.v.y, self.v.z, -self.eye.dot(self.v)],
                [self.n.x, self.n.y, self.n.z, -self.eye.dot(self.n)],
                [0,        0,        0,        1]])

class ProjectionMatrix(Matrix):
    __create_key = object()

    def __init__(self, key):
        assert(key == ProjectionMatrix.__create_key), \
            "ProjectionMatrix must be created using the static perspective() or orthographic() methods!"

        super().__init__(4, 4)

        self.left = 0.
        self.right = 0.
        self.bottom = 0.
        self.top = 0.
        self.near = 0.
        self.far = 0.
        self.fov = 0.
        self.aspect_ratio = 0.

        self.is_orthographic = False

    @staticmethod
    def perspective(fov: float, aspect_ratio: float, near: float, far: float):
        near, far = min(near, far), max(near, far)
        fov = math.fmod(fov, math.tau)

        output = ProjectionMatrix(key=ProjectionMatrix.__create_key)

        output.fov = fov
        output.near = near
        output.far = far

        output.top = math.tan(fov / 2.) * near
        output.bottom = -output.top

        output.right = output.top * aspect_ratio
        output.left = -output.right

        output.is_orthographic = False

        return output

    @staticmethod
    def ortographic(near: float, far: float, width: float, height: float = None):
        if height is None:
            height = width

        hw = width / 2.
        hh = height / 2.

        output = ProjectionMatrix(key=ProjectionMatrix.__create_key)
        output.aspect_ratio = hw/hh
        output.left = -hw
        output.right = hw
        output.bottom = -hh
        output.top = hh
        output.near = near
        output.far = far
        output.is_orthographic = True

        return output

    @property
    def values(self):
        rl_inv_dist = 1. / (self.right - self.left)
        tb_inv_dist = 1. / (self.top - self.bottom)
        nf_inv_dist = 1. / (self.near - self.far)

        if self.is_orthographic:
            p11 = 2 * rl_inv_dist
            p22 = 2 * tb_inv_dist
            p33 = 2 * nf_inv_dist
            p34 = (self.near + self.far) * nf_inv_dist

            """A = 2 * rl_inv_dist
            # B = -(self.right + self.left) * rl_inv_dist
            C = 2 * tb_inv_dist
            # D = -(self.top + self.bottom) * tb_inv_dist
            E = 2 * nf_inv_dist
            F = (self.near + self.far) * nf_inv_dist

            return np.array([[A,0,0,B],
                            [0,C,0,D],
                            [0,0,E,F],
                            [0,0,0,1]])"""
        else:
            p11 = 2 * self.near * rl_inv_dist
            p22 = 2 * self.near * tb_inv_dist
            p33 = (self.near + self.far) * nf_inv_dist
            p34 = 2 * self.near * self.far * nf_inv_dist

        return np.array([[p11,  0,  0,  0],
                        [0,  p22,  0,  0],
                        [0,    0,  p33,p34],
                        [0,    0,   -1,  0]])

