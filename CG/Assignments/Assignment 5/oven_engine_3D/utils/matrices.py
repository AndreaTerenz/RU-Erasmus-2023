import math
from abc import ABC

import numpy as np

from oven_engine_3D.utils.geometry import Vector3D, classproperty


def set_values_in_matrix(matrix, idx_val_zip):
    for idx, val in idx_val_zip:
        matrix[idx] = val

    return matrix

class Matrix(ABC):
    def __init__(self, rows = 4, cols = 4):
        self._matrix = np.eye(rows, cols).flatten()
        self.rows = rows
        self.cols = cols

    def __eq__(self, other):
        if not isinstance(other, Matrix):
            return False

        return np.array_equal(self._matrix, other._matrix)

    @property
    def identity(self):
        return np.eye(self.rows, self.cols).flatten()

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
        self._matrix = (self._matrix.reshape(4,4) @ other).flatten()

    @property
    def values(self):
        return self._matrix

    """@staticmethod
    def translation_matrix(offset: [float|Vector3D]):
        if type(offset) is float:
            offset = Vector3D(offset)

        return np.array([
            [1, 0, 0, offset.x],
            [0, 1, 0, offset.y],
            [0, 0, 1, offset.z],
            [0, 0, 0, 1]
        ], dtype=np.float32)

    @staticmethod
    def translation_matrix_to(position: Vector3D, target: Vector3D):
        return Matrix.translation_matrix(target - position)

    @staticmethod
    def rotation_matrix(angle, axis):
        c = np.cos(angle)
        s = np.sin(angle)
        t = 1 - c

        x, y, z = axis.normalized

        return np.array([
            [t * x * x + c,     t * x * y - z * s, t * x * z + y * s, 0],
            [t * x * y + z * s, t * y * y + c,     t * y * z - x * s, 0],
            [t * x * z - y * s, t * y * z + x * s, t * z * z + c, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

    @staticmethod
    def rotation_matrix_euler(angles: [float|Vector3D]):
        if type(angles) is float:
            angles = Vector3D(angles)

        x, y, z = angles

        cx, sx = np.cos(x), np.sin(x)
        cy, sy = np.cos(y), np.sin(y)
        cz, sz = np.cos(z), np.sin(z)

        return np.array([
            [cy*cz,            -cy*sz,            sy, 0],
            [cx*sz + sx*sy*cz,  cx*cz - sx*sy*sz, -sx*cy, 0],
            [sx*sz - cx*sy*cz,  sx*cz + cx*sy*sz,  cx*cy, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

    @staticmethod
    def scale_matrix(scale: [float|Vector3D]):
        if type(scale) is float:
            scale = Vector3D(scale)

        return np.array([
            [scale.x, 0, 0, 0],
            [0, scale.y, 0, 0],
            [0, 0, scale.z, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)"""

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

        translation_matrix = set_values_in_matrix(np.eye(4).flatten(), zip([3, 7, 11], [offset.x, offset.y, offset.z]))

        self.add_transformation(translation_matrix)

    def add_rotation(self, angle_x: [float|Vector3D], angle_y = None, angle_z = None):
        if type(angle_x) is Vector3D:
            angle_x, angle_y, angle_z = angle_x.x, angle_x.y, angle_x.z

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

        scale_matrix = set_values_in_matrix(np.eye(4).flatten(), zip([0, 5, 10], [scale.x, scale.y, scale.z]))

        self.add_transformation(scale_matrix)

    # YOU CAN TRY TO MAKE PUSH AND POP (AND COPY) LESS DEPENDANT ON GARBAGE COLLECTION
    # THAT CAN FIX SMOOTHNESS ISSUES ON SOME COMPUTERS
    def push_matrix(self):
        self.stack.append(self.copy_matrix().tolist())

    def pop_matrix(self):
        self._matrix = self.stack.pop()


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

        # Create the rotation matrix around the global y-axis
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

        # Create the rotation matrix around the global y-axis
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

    def get_axis_from_matrix(self):
        """
        Extract the values for each axis vector from the matrix
        """

        return Vector3D(self._matrix[0], self._matrix[1], self._matrix[2]), \
                Vector3D(self._matrix[4], self._matrix[5], self._matrix[6]), \
                Vector3D(self._matrix[8], self._matrix[9], self._matrix[10])

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
        minusEye = -self.eye
        return [self.u.x, self.u.y, self.u.z, minusEye.dot(self.u),
                self.v.x, self.v.y, self.v.z, minusEye.dot(self.v),
                self.n.x, self.n.y, self.n.z, minusEye.dot(self.n),
                0,        0,        0,        1]

class ProjectionMatrix(Matrix):
    def __init__(self):
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

        output = ProjectionMatrix()

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

        output = ProjectionMatrix()
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
        rl_dist = self.right - self.left
        tb_dist = self.top - self.bottom
        fn_dist = self.far - self.near

        if self.is_orthographic:
            A = 2 / rl_dist
            B = -(self.right + self.left) / rl_dist
            C = 2 / tb_dist
            D = -(self.top + self.bottom) / tb_dist
            E = 2 / -fn_dist
            F = (self.near + self.far) / -fn_dist

            return [A,0,0,B,
                    0,C,0,D,
                    0,0,E,F,
                    0,0,0,1]
        else:
            p11 = 2*self.near / rl_dist
            p13 = (self.right + self.left) / rl_dist

            p22 = 2*self.near / tb_dist
            p23 = (self.top + self.bottom) / tb_dist

            p33 = (self.near + self.far) / (-fn_dist)
            p34 = 2 * self.near * self.far / (-fn_dist)

            return [p11,  0,  p13,  0,
                    0,  p22,  p23,  0,
                    0,    0,  p33,p34,
                    0,    0,   -1,  0]

