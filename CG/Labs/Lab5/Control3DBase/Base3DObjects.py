import math
from abc import abstractmethod, ABC

from OpenGL.GL import *

# from Control3DBase.Geometry import Vector3D
from Control3DBase.Matrices import ModelMatrix
from Control3DBase.Shaders import MeshShader
from Control3DBase.utils.geometry import Vector3D
from Control3DBase.utils.gl3d import CUBE_POSITION_ARRAY, CUBE_NORMAL_ARRAY, draw_cube


class Entity3D(ABC):
    def __init__(self, parent_app, origin = Vector3D.ZERO, size=1., color=(1.0, 0.0, 1.0), vertex_shader=None, frag_shader=None):
        self.parent_app = parent_app
        self.origin = origin
        self.rotation = Vector3D.ZERO
        self.scale = Vector3D.ONE
        self.model_matrix = ModelMatrix()
        self.shader = None

    def update_model_matrix(self):
        self.model_matrix.load_identity()
        self.model_matrix.add_translation(self.origin)
        self.model_matrix.add_rotation(self.rotation)
        self.model_matrix.add_scale(self.scale)

        if self.shader is not None:
            self.shader.set_model_matrix(self.model_matrix.values)

    @abstractmethod
    def draw(self):
        self.shader.use()

        for k in range(6):
            glDrawArrays(GL_TRIANGLE_FAN, k*4, 4)

    def update(self, delta):
        self._update(delta)
        self.update_model_matrix()

    @abstractmethod
    def _update(self, delta):
        pass

    @abstractmethod
    def handle_event(self, ev):
        pass

    @property
    def forward(self):
        return self.to_global(Vector3D.FORWARD)

    def translate(self, offset: Vector3D):
        self.origin += offset

    def scale(self, factor):
        self.scale *= factor

    def rotate(self, angle, axis):
        self.rotation += angle * axis

    def to_global(self, local_pos: Vector3D):
        return self.model_matrix * local_pos

    #TODO: Requires computing inverse of model matrix...
    """def to_local(self, global_pos: Vector3D):
        return self.model_matrix.inverse() * global_pos"""


class Cube(Entity3D, ABC):
    def __init__(self, parent_app, origin = Vector3D.ZERO, size=1., color=(1.0, 0.0, 1.0), vertex_shader=None, frag_shader=None):
        super().__init__(parent_app, origin, size, color, vertex_shader, frag_shader)

        self.shader = MeshShader()
        self.shader.use()
        self.shader.set_solid_color(color[0], color[1], color[2])
        self.shader.set_position_attribute(CUBE_POSITION_ARRAY)
        self.shader.set_normal_attribute(CUBE_NORMAL_ARRAY)

    def draw(self):
        draw_cube(self.parent_app.camera, model_matrix=self.model_matrix, shader=self.shader)

    def handle_event(self, ev):
        pass

class Cube1(Cube):
    def __init__(self, parent_app, origin = Vector3D.ZERO, speed =.5, size=1.):
        super().__init__(parent_app, origin, size, color=(1.0, 0.0, 0.0))
        self.speed = speed

    def _update(self, delta):
        fact = math.sin(self.parent_app.ticks / 100.) * 1.
        self.translate(Vector3D.FORWARD * delta * fact * self.speed)

class Cube2(Cube):
    def __init__(self, parent_app, origin = Vector3D.ZERO, size=1.):
        super().__init__(parent_app, origin, size, color=(0.0, 1.0, 0.0))

    def _update(self, delta):
        fact = math.sin(self.parent_app.ticks / 100.)
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