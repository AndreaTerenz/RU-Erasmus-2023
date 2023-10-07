import math
from abc import abstractmethod, ABC

from OpenGL.GL import *

# from Control3DBase.Geometry import Vector3D
from Control3DBase.Matrices import ModelMatrix
from Control3DBase.Shaders import MeshShader
from Control3DBase.utils.geometry import Vector3D
from Control3DBase.utils.gl3d import CUBE_POSITION_ARRAY, CUBE_NORMAL_ARRAY, draw_cube, PLANE_POSITION_ARRAY, \
    PLANE_NORMAL_ARRAY, euler_from_vectors, draw_plane


class Entity(ABC):
    def __init__(self, parent_app, origin = Vector3D.ZERO):
        self.parent_app = parent_app
        self.origin = origin

    def update(self, delta):
        self._update(delta)

    @abstractmethod
    def _update(self, delta):
        pass

    @abstractmethod
    def handle_event(self, ev):
        pass

class MeshEntity(Entity):
    def __init__(self, parent_app, origin = Vector3D.ZERO, rotation = Vector3D.ZERO, scale = Vector3D.ONE):
        super().__init__(parent_app, origin)

        self.rotation = rotation
        self.scale = scale
        self.model_matrix = ModelMatrix.from_transformations(origin, rotation, scale)
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
        pass

    def update(self, delta):
        self._update(delta)
        self.update_model_matrix()

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


class Cube(MeshEntity):

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

class Plane(MeshEntity):
    def __init__(self, parent_app, origin = Vector3D.ZERO, color=(1.0, 0.0, 1.0), normal=Vector3D.UP, scale = Vector3D.ONE):
        rotation = Vector3D(*euler_from_vectors(normal))

        super().__init__(parent_app, origin, rotation=rotation, scale=scale)

        self.shader = MeshShader(positions=PLANE_POSITION_ARRAY, normals=PLANE_NORMAL_ARRAY, diffuse_color=color)

    def point_to(self, dir: Vector3D):
        rotation = Vector3D(*euler_from_vectors(dir))
        self.rotate(rotation.x, Vector3D.RIGHT)
        self.rotate(rotation.y, Vector3D.UP)
        self.rotate(rotation.z, Vector3D.FORWARD)

    def draw(self):
        camera = self.parent_app.camera
        light = self.parent_app.light

        draw_plane(camera, light, ambient_color=self.parent_app.ambient_color,
                   model_matrix=self.model_matrix, shader=self.shader)

    def _update(self, delta):
        pass

    def handle_event(self, ev):
        pass

