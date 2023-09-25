from abc import abstractmethod, ABC

import numpy as np
import math

from OpenGL.GL import *

from Control3DBase.Geometry import Vector
from Control3DBase.Matrices import ModelMatrix
from Control3DBase.Shaders import Shader3D


class Cube(ABC):
    def __init__(self, parent_app, origin = Vector(0, 0, 0), size=1., color=(1.0, 0.0, 1.0)):
        self.parent_app = parent_app
        self.origin = origin
        self.rotation = Vector(0, 0, 0)
        self.scale = Vector(1, 1, 1)
        self.model_matrix = ModelMatrix()

        self.shader = Shader3D(shader_folder="Control3DBase/Shader Files")
        self.shader.use()
        self.shader.set_solid_color(color[0], color[1], color[2])
        self.shader.set_projection_view_matrix(self.parent_app.projection_view_matrix.get_matrix())

        self.model_matrix.add_translation(self.origin)
        self.model_matrix.add_scale(self.scale)

        self.position_array = np.array(
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
                              1,  1, -1]) * size
        self.normal_array = np.array([0.0,  0.0, -1.0] * 6 +
                                     [0.0,  0.0,  1.0] * 6 +
                                     [0.0, -1.0,  0.0] * 6 +
                                     [0.0,  1.0,  0.0] * 6 +
                                     [-1.0, 0.0,  0.0] * 6 +
                                     [1.0,  0.0,  0.0] * 6)

    def __update_model_matrix(self):
        self.model_matrix.load_identity()
        self.model_matrix.add_translation(self.origin)
        self.model_matrix.add_rotation(self.rotation)
        self.model_matrix.add_scale(self.scale)

    def draw(self):
        self.shader.use()
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.shader.set_position_attribute(self.position_array)
        self.shader.set_normal_attribute(self.normal_array)

        for k in range(6):
            glDrawArrays(GL_TRIANGLE_FAN, k*4, 4)

    def update(self, delta):
        self._update(delta)
        self.__update_model_matrix()

    @abstractmethod
    def _update(self, delta):
        pass

    def translate(self, offset):
        self.origin += offset

    def scale(self, factor):
        self.scale *= factor

    def rotate(self, angle, axis):
        self.rotation += angle * axis

class Cube1(Cube):
    def __init__(self, parent_app, origin = Vector(0, 0, 0), speed =1., size=1.):
        super().__init__(parent_app, origin, size)
        self.speed = speed

    def _update(self, delta):
        fact = math.sin(self.parent_app.ticks / 500.)
        self.origin.z += delta * fact * self.speed

class Cube2(Cube):
    def __init__(self, parent_app, origin = Vector(0, 0, 0), size=1.):
        super().__init__(parent_app, origin, size)

    def _update(self, delta):
        fact = math.sin(self.parent_app.ticks / 500.)
        fact = (fact + 1.) / 2. # Remap [-1, 1] to [0, 1]

        self.scale = Vector(fact * 2., 1, 1)

class Cube3(Cube):
    def __init__(self, parent_app, origin = Vector(0, 0, 0), size=1.):
        super().__init__(parent_app, origin, size)

    def _update(self, delta):
        self.rotate(delta, Vector(0, 1, 0))

        fact = math.sin(self.parent_app.ticks / 500.)
        fact = (fact + 1.) / 2. # Remap [-1, 1] to [0, 1]

        self.scale = Vector(fact * 2., 1, 1)