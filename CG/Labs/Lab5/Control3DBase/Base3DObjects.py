import math
from abc import abstractmethod, ABC

from OpenGL.GL import *

# from Control3DBase.Geometry import Vector3D
from Control3DBase.Matrices import ModelMatrix
from Control3DBase.Shaders import MeshShader
from Control3DBase.utils.geometry import Vector3D
from Control3DBase.utils.gl3d import CUBE_POSITION_ARRAY, CUBE_NORMAL_ARRAY, draw_cube


class Entity3D(ABC):
    def __init__(self, parent_app, origin = Vector3D.ZERO):
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

    def translate_to(self, position: Vector3D):
        self.origin = position

    def scale_by(self, factor):
        self.scale *= factor

    def rotate(self, angle, axis):
        self.rotation += angle * axis

    def to_global(self, local_pos: Vector3D):
        return self.model_matrix * local_pos

    #TODO: Requires computing inverse of model matrix...
    """def to_local(self, global_pos: Vector3D):
        return self.model_matrix.inverse() * global_pos"""


class Cube(Entity3D):

    def __init__(self, parent_app, origin = Vector3D.ZERO, color=(1.0, 0.0, 1.0)):
        super().__init__(parent_app, origin)

        self.shader = MeshShader(positions=CUBE_POSITION_ARRAY, normals=CUBE_NORMAL_ARRAY, diffuse_color=color)

    def draw(self):
        light = self.parent_app.light
        camera = self.parent_app.camera

        draw_cube(camera=camera, light=light, ambient_color=self.parent_app.ambient_color, model_matrix=self.model_matrix, shader=self.shader)

    def handle_event(self, ev):
        pass

    def _update(self, delta):
        pass