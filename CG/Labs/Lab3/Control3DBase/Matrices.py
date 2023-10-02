import math
from abc import ABC

import numpy as np

from oven_engine.utils.geometry import Vector3D


def set_values_in_matrix(matrix, idx_val_zip):
    for idx, val in idx_val_zip:
        matrix[idx] = val

    return matrix

class Matrix(ABC):
    def __init__(self, rows = 4, cols = 4):
        self.matrix = np.eye(rows, cols).flatten()
        self.rows = rows
        self.cols = cols

    def load_identity(self):
        self.matrix = np.eye(self.rows, self.cols).flatten()

    def copy_matrix(self):
        return np.copy(self.matrix)

    def add_transformation(self, other):
        counter = 0
        new_matrix = np.zeros(16)
        for row in range(4):
            for col in range(4):
                for i in range(4):
                    new_matrix[counter] += self.matrix[row*4 + i]*other[col + 4*i]
                counter += 1
        self.matrix = new_matrix

        #self.matrix = self.matrix @ other

    def add_nothing(self):
        other_matrix = np.eye(4).flatten()
        self.add_transformation(other_matrix)

    def __str__(self):
        ret_str = ""
        counter = 0
        for _ in range(4):
            ret_str += "["
            for _ in range(4):
                ret_str += " " + str(self.matrix[counter]) + " "
                counter += 1
            ret_str += "]\n"
        return ret_str

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

    ## MAKE OPERATIONS TO ADD TRANLATIONS, SCALES AND ROTATIONS ##
    # ---
    def add_translation(self, x : [float|Vector3D], y = None, z = None):
        if type(x) is Vector3D:
            offset = x
        else:
            offset = Vector3D(x, y, z)

        translation_matrix = np.eye(4).flatten()
        set_values_in_matrix(translation_matrix, zip([3, 7, 11], [offset.x, offset.y, offset.z]))

        self.add_transformation(translation_matrix)

    def add_rotation(self, angle_x: [float|Vector3D], angle_y = None, angle_z = None):
        if type(angle_x) is Vector3D:
            angle_x, angle_y, angle_z = angle_x.x, angle_x.y, angle_x.z

        rotation_matrix = np.eye(4).flatten()
        cx, sx = np.cos(angle_x), np.sin(angle_x)
        cy, sy = np.cos(angle_y), np.sin(angle_y)
        cz, sz = np.cos(angle_z), np.sin(angle_z)

        set_values_in_matrix(rotation_matrix,
                             zip([0, 1, 2, 4, 5, 6, 8, 9, 10],
                                 [cy*cz,            -cy*sz,            sy,
                                  cx*sz + sx*sy*cz,  cx*cz - sx*sy*sz, -sx*cy,
                                  sx*sz - cx*sy*cz,  sx*cz + cx*sy*sz,  cx*cy]))

        self.add_transformation(rotation_matrix)

    def add_scale(self, x : [float|Vector3D], y = None, z = None):
        if type(x) is Vector3D:
            scale = x
        else:
            scale = Vector3D(x, y, z)

        scale_matrix = np.eye(4).flatten()
        set_values_in_matrix(scale_matrix, zip([0, 5, 10], [scale.x, scale.y, scale.z]))

        self.add_transformation(scale_matrix)

    # YOU CAN TRY TO MAKE PUSH AND POP (AND COPY) LESS DEPENDANT ON GARBAGE COLLECTION
    # THAT CAN FIX SMOOTHNESS ISSUES ON SOME COMPUTERS
    def push_matrix(self):
        self.stack.append(self.copy_matrix().tolist())

    def pop_matrix(self):
        self.matrix = self.stack.pop()



# The ViewMatrix class holds the camera's coordinate frame and
# set's up a transformation concerning the camera's position
# and orientation

class ViewMatrix:
    def __init__(self):
        self.eye = Vector3D(0,0,0)
        self.u = Vector3D(1, 0, 0)
        self.v = Vector3D(0, 1, 0)
        self.n = Vector3D(0, 0, 1)

    ## MAKE OPERATIONS TO ADD LOOK, SLIDE, PITCH, YAW and ROLL ##
    # ---
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

    @staticmethod
    def __rotate_axes(a, b, angle):
        c = np.cos(angle)
        s = np.sin(angle)
        old_a = a

        a = c * a + s * b
        b = -s * old_a + c * b

        return a, b

    def get_matrix(self):
        minusEye = -self.eye
        return [self.u.x, self.u.y, self.u.z, minusEye.dot(self.u),
                self.v.x, self.v.y, self.v.z, minusEye.dot(self.v),
                self.n.x, self.n.y, self.n.z, minusEye.dot(self.n),
                0,        0,        0,        1]


# The ProjectionMatrix class builds transformations concerning
# the camera's "lens"

class ProjectionMatrix:
    def __init__(self):
        self.left = 0.
        self.right = 0.
        self.bottom = 0.
        self.top = 0.
        self.near = 0.
        self.far = 0.

        self.is_orthographic = False

    ## MAKE OPERATION TO SET PERSPECTIVE PROJECTION (don't forget to set is_orthographic to False) ##
    # ---
    @staticmethod
    def perspective(fov: float, aspect_ratio: float, near: float, far: float):
        output = ProjectionMatrix()

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
        output.left = -hw
        output.right = hw
        output.bottom = -hh
        output.top = hh
        output.near = near
        output.far = far
        output.is_orthographic = True

        return output

    def get_matrix(self):
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

