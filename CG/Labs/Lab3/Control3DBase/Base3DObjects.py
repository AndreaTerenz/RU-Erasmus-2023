from abc import abstractmethod, ABC

import numpy as np
import math

from OpenGL.GL import *

from oven_engine.utils.geometry import Vector3D
#from Control3DBase.Geometry import Vector3D
from Control3DBase.Matrices import ModelMatrix
from Control3DBase.Shaders import Shader3D, CubeShader


class Cube(ABC):
    def __init__(self, parent_app, origin = Vector3D.ZERO, size=1., color=(1.0, 0.0, 1.0), vertex_shader=None, frag_shader=None):
        self.parent_app = parent_app
        self.origin = origin
        self.rotation = Vector3D.ZERO
        self.scale = Vector3D.ONE
        self.model_matrix = ModelMatrix()

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

        self.shader = CubeShader()
        self.shader.use()
        self.shader.set_solid_color(color[0], color[1], color[2])
        #self.shader.set_projection_view_matrix(self.parent_app.projection_view_matrix.get_matrix())
        self.shader.set_projection_matrix(self.parent_app.projection_matrix.get_matrix())
        self.shader.set_view_matrix(self.parent_app.view_matrix.get_matrix())
        self.shader.set_position_attribute(self.position_array)
        self.shader.set_normal_attribute(self.normal_array)

    def __update_model_matrix(self):
        self.model_matrix.load_identity()
        self.model_matrix.add_translation(self.origin)
        self.model_matrix.add_rotation(self.rotation)
        self.model_matrix.add_scale(self.scale)

        self.shader.set_model_matrix(self.model_matrix.matrix)

    def draw(self):
        self.shader.use()
        self.shader.set_model_matrix(self.model_matrix.matrix)

        for k in range(6):
            glDrawArrays(GL_TRIANGLE_FAN, k*4, 4)

    def update(self, delta):
        self._update(delta)
        self.__update_model_matrix()

    @abstractmethod
    def _update(self, delta):
        pass

    def translate(self, offset: Vector3D):
        self.origin += offset

    def scale(self, factor):
        self.scale *= factor

    def rotate(self, angle, axis):
        self.rotation += angle * axis

class Cube1(Cube):
    def __init__(self, parent_app, origin = Vector3D.ZERO, speed =1., size=1.):
        super().__init__(parent_app, origin, size, color=(1.0, 0.0, 0.0))
        self.speed = speed

    def _update(self, delta):
        fact = math.sin(self.parent_app.ticks / 500.)
        self.translate(Vector3D.FORWARD * delta * fact * self.speed)

class Cube2(Cube):
    def __init__(self, parent_app, origin = Vector3D.ZERO, size=1.):
        super().__init__(parent_app, origin, size, color=(0.0, 1.0, 0.0))

    def _update(self, delta):
        fact = math.sin(self.parent_app.ticks / 500.)
        fact = (fact + 1.) / 2. # Remap [-1, 1] to [0, 1]

        self.scale = Vector3D(fact * 2., 1, 1)

class Cube3(Cube):
    def __init__(self, parent_app, origin = Vector3D.ZERO, size=1.):
        super().__init__(parent_app, origin, size, color=(0.0, 0.0, 1.0))

    def _update(self, delta):
        self.rotate(delta, Vector3D(0, 1, 0))

        fact = math.sin(self.parent_app.ticks / 500.)
        fact = (fact + 1.) / 2. # Remap [-1, 1] to [0, 1]

        self.scale = Vector3D(fact * 2., 1, 1)