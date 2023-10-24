from abc import abstractmethod, ABC
from pygame import Color
from oven_engine_3D.meshes import CubeMesh, PlaneMesh, Mesh
# from oven_engine_3D.Geometry import Vector3D
from oven_engine_3D.utils.matrices import ModelMatrix
from oven_engine_3D.shaders import MeshShader
from oven_engine_3D.utils.geometry import Vector3D, euler_from_vectors


class Entity(ABC):
    def __init__(self, parent_app, origin=Vector3D.ZERO, rotation=Vector3D.ZERO, scale=Vector3D.ONE):
        self.parent_app = parent_app
        self.origin = origin
        self.rotation = rotation
        self.scale = scale
        self.model_matrix = ModelMatrix.from_transformations(origin, rotation, scale)

    def update_model_matrix(self):
        self.model_matrix.load_identity()
        self.model_matrix.add_translation(self.origin)
        self.model_matrix.add_rotation(self.rotation)
        self.model_matrix.add_scale(self.scale)
        self.modelmat_update()

    def modelmat_update(self):
        pass

    def update(self, delta):
        self._update(delta)
        self.update_model_matrix()

    @property
    def forward(self):
        return self.to_global(Vector3D.FORWARD)

    def translate(self, offset: Vector3D):
        self.origin += offset
        return self

    def translate_to(self, position: Vector3D):
        self.origin = position
        return self

    def scale_by(self, factor):
        self.scale *= factor
        return self

    def rotate(self, angle, axis=Vector3D.UP):
        self.rotation += angle * axis
        return self

    def to_global(self, local_pos: Vector3D):
        return self.model_matrix * local_pos

    # TODO: Requires computing inverse of model matrix...
    """def to_local(self, global_pos: Vector3D):
        return self.model_matrix.inverse() * global_pos"""

    @abstractmethod
    def _update(self, delta):
        pass

    @abstractmethod
    def handle_event(self, ev):
        pass


class MeshEntity(Entity):

    def __init__(self, parent_app, mesh: Mesh, origin=Vector3D.ZERO, rotation=Vector3D.ZERO, scale=Vector3D.ONE, color=Color("magenta"), shader=None):
        super().__init__(parent_app, origin, rotation, scale)

        if shader is None:
            shader = MeshShader(diffuse_color=color)

        self.shader = shader
        self.mesh = mesh

    def modelmat_update(self):
        if self.shader is not None:
            self.shader.set_model_matrix(self.model_matrix)

    def draw(self):
        self.mesh.draw(self.parent_app, shader=self.shader, model_matrix=self.model_matrix)

    def _update(self, delta):
        pass

    def handle_event(self, ev):
        pass


class Cube(MeshEntity):

    def __init__(self, parent_app, origin=Vector3D.ZERO, rotation=Vector3D.ZERO, scale=Vector3D.ONE, color=Color("magenta"), shader=None):
        super().__init__(parent_app, mesh=CubeMesh(), origin=origin, rotation=rotation, scale=scale, color=color, shader=shader)


    def handle_event(self, ev):
        pass

    def _update(self, delta):
        pass


class Plane(MeshEntity):
    def __init__(self, parent_app, origin=Vector3D.ZERO, color=(1.0, 0.0, 1.0), normal=Vector3D.UP, scale=Vector3D.ONE,
                 shader=None):
        rotation = Vector3D(*euler_from_vectors(normal))

        super().__init__(parent_app, mesh=PlaneMesh(), origin=origin, rotation=rotation, scale=scale, color=color, shader=shader)

    def point_to(self, _dir: Vector3D):
        rotation = Vector3D(*euler_from_vectors(_dir))
        self.rotate(rotation.x, Vector3D.RIGHT)
        self.rotate(rotation.y, Vector3D.UP)
        self.rotate(rotation.z, Vector3D.FORWARD)

    def _update(self, delta):
        pass

    def handle_event(self, ev):
        pass
