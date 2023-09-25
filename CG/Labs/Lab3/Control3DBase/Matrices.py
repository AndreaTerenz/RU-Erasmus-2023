from abc import ABC
import numpy as np

from Control3DBase.Geometry import Point, Vector

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

    ## MAKE OPERATIONS TO ADD TRANLATIONS, SCALES AND ROTATIONS ##
    # ---
    def add_translation(self, x : [float|Vector], y = None, z = None):
        if type(x) is Vector:
            offset = x
        else:
            offset = Vector(x, y, z)

        translation_matrix = np.eye(4).flatten()
        set_values_in_matrix(translation_matrix, zip([3, 7, 11], [offset.x, offset.y, offset.z]))

        self.add_transformation(translation_matrix)

    def add_rotation_x(self, angle):
        rotation_matrix = np.eye(4).flatten()
        c = np.cos(angle)
        s = np.sin(angle)

        set_values_in_matrix(rotation_matrix, zip([5, 6, 9, 10], [c, -s, s, c]))

        self.add_transformation(rotation_matrix)

    def add_rotation_y(self, angle):
        rotation_matrix = np.eye(4).flatten()
        c = np.cos(angle)
        s = np.sin(angle)

        set_values_in_matrix(rotation_matrix, zip([0, 2, 8, 10], [c, s, -s, c]))

        self.add_transformation(rotation_matrix)

    def add_rotation_z(self, angle):
        rotation_matrix = np.eye(4).flatten()
        c = np.cos(angle)
        s = np.sin(angle)

        set_values_in_matrix(rotation_matrix, zip([0, 1, 4, 5], [c, -s, s, c]))

        self.add_transformation(rotation_matrix)

    def add_rotation(self, angle_x: [float|Vector], angle_y = None, angle_z = None):
        if type(angle_x) is Vector:
            angle_x, angle_y, angle_z = angle_x.x, angle_x.y, angle_x.z

        rotation_matrix = np.eye(4).flatten()
        cx = np.cos(angle_x)
        sx = np.sin(angle_x)
        cy = np.cos(angle_y)
        sy = np.sin(angle_y)
        cz = np.cos(angle_z)
        sz = np.sin(angle_z)

        set_values_in_matrix(rotation_matrix,
                             zip([0, 1, 2, 4, 5, 6, 8, 9, 10],
                                 [cy*cz, -cy*sz, sy, cx*sz + sx*sy*cz, cx*cz - sx*sy*sz, -sx*cy, sx*sz - cx*sy*cz, sx*cz + cx*sy*sz, cx*cy]))

        self.add_transformation(rotation_matrix)

    def add_scale(self, x : [float|Vector], y = None, z = None):
        if type(x) is Vector:
            scale = x
        else:
            scale = Vector(x, y, z)

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
        self.eye = Point(0, 0, 0)
        self.u = Vector(1, 0, 0)
        self.v = Vector(0, 1, 0)
        self.n = Vector(0, 0, 1)

    ## MAKE OPERATIONS TO ADD LOOK, SLIDE, PITCH, YAW and ROLL ##
    # ---

    def get_matrix(self):
        minusEye = Vector(-self.eye.x, -self.eye.y, -self.eye.z)
        return [self.u.x, self.u.y, self.u.z, minusEye.dot(self.u),
                self.v.x, self.v.y, self.v.z, minusEye.dot(self.v),
                self.n.x, self.n.y, self.n.z, minusEye.dot(self.n),
                0,        0,        0,        1]


# The ProjectionMatrix class builds transformations concerning
# the camera's "lens"

class ProjectionMatrix:
    def __init__(self):
        self.left = -1
        self.right = 1
        self.bottom = -1
        self.top = 1
        self.near = -1
        self.far = 1

        self.is_orthographic = True

    ## MAKE OPERATION TO SET PERSPECTIVE PROJECTION (don't forget to set is_orthographic to False) ##
    # ---

    def set_orthographic(self, left, right, bottom, top, near, far):
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self.near = near
        self.far = far
        self.is_orthographic = True

    def get_matrix(self):
        if self.is_orthographic:
            A = 2 / (self.right - self.left)
            B = -(self.right + self.left) / (self.right - self.left)
            C = 2 / (self.top - self.bottom)
            D = -(self.top + self.bottom) / (self.top - self.bottom)
            E = 2 / (self.near - self.far)
            F = (self.near + self.far) / (self.near - self.far)

            return [A,0,0,B,
                    0,C,0,D,
                    0,0,E,F,
                    0,0,0,1]

        else:
            pass
            # Set up a matrix for a Perspective projection
            ###  Remember that it's a non-linear transformation   ###
            ###  so the bottom row is different                   ###



# The ProjectionViewMatrix returns a hardcoded matrix
# that is just used to get something to send to the
# shader before you properly implement the ViewMatrix
# and ProjectionMatrix classes.
# Feel free to throw it away afterwards!

class ProjectionViewMatrix:
    def __init__(self):
        pass

    def get_matrix(self):
        return [ 0.45052942369783683,  0.0,  -0.15017647456594563,  0.0,
                -0.10435451285616304,  0.5217725642808152,  -0.3130635385684891,  0.0,
                -0.2953940042189954,  -0.5907880084379908,  -0.8861820126569863,  3.082884480118567,
                -0.2672612419124244,  -0.5345224838248488,  -0.8017837257372732,  3.7416573867739413 ]


# IDEAS FOR OPERATIONS AND TESTING:
# if __name__ == "__main__":
#     matrix = ModelMatrix()
#     matrix.push_matrix()
#     print(matrix)
#     matrix.add_translation(3, 1, 2)
#     matrix.push_matrix()
#     print(matrix)
#     matrix.add_scale(2, 3, 4)
#     print(matrix)
#     matrix.pop_matrix()
#     print(matrix)
    
#     matrix.add_translation(5, 5, 5)
#     matrix.push_matrix()
#     print(matrix)
#     matrix.add_scale(3, 2, 3)
#     print(matrix)
#     matrix.pop_matrix()
#     print(matrix)
    
#     matrix.pop_matrix()
#     print(matrix)
        
#     matrix.push_matrix()
#     matrix.add_scale(2, 2, 2)
#     print(matrix)
#     matrix.push_matrix()
#     matrix.add_translation(3, 3, 3)
#     print(matrix)
#     matrix.push_matrix()
#     matrix.add_rotation_y(pi / 3)
#     print(matrix)
#     matrix.push_matrix()
#     matrix.add_translation(1, 1, 1)
#     print(matrix)
#     matrix.pop_matrix()
#     print(matrix)
#     matrix.pop_matrix()
#     print(matrix)
#     matrix.pop_matrix()
#     print(matrix)
#     matrix.pop_matrix()
#     print(matrix)
    
