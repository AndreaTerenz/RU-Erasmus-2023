from abc import abstractmethod, ABC

import shortuuid
from OpenGL.GL import *

from oven_engine_3D.meshes import CubeMesh, PlaneMesh, Mesh, OBJMesh, SphereMesh
from oven_engine_3D.shaders import MeshShader, SkyboxShader
from oven_engine_3D.utils.geometry import Vector3D, euler_from_vectors
from oven_engine_3D.utils.matrices import ModelMatrix


class Entity(ABC):
    def __init__(self, parent_app, origin=Vector3D.ZERO, rotation=Vector3D.ZERO, scale=Vector3D.ONE, name=""):
        self.origin = origin
        self.rotation = rotation
        self.scale = scale
        self.model_matrix = ModelMatrix.from_transformations(origin, rotation, scale)
        self.name = shortuuid.uuid() if name == "" else name
        self.parent_app = parent_app

    def update(self, delta):
        self.model_matrix.load_identity()
        self.model_matrix.add_translation(self.origin)
        self.model_matrix.add_rotation(self.rotation)
        self.model_matrix.add_scale(self.scale)

        self._update(delta)

    @property
    def forward(self):
        return self.to_global(Vector3D.FORWARD)

    def translate_to(self, position: Vector3D):
        self.origin = position
        return self

        # return self.translate(position - self.origin)

    def translate(self, offset: Vector3D):
        self.origin += offset
#         self.model_matrix.add_translation(offset)
        return self

    def scale_by(self, factor):
        self.scale *= factor
        # self.model_matrix.add_scale(factor)
        return self

    def rotate(self, angle, axis=Vector3D.UP):
        self.rotation += angle * axis
        # self.model_matrix.add_rotation(angle * axis)
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


class DrawnEntity(Entity):

    def __init__(self, parent_app, mesh: [str|Mesh], origin=Vector3D.ZERO, rotation=Vector3D.ZERO, scale=Vector3D.ONE, name="", color="white", shader=None):
        super().__init__(parent_app, origin, rotation, scale, name=name)

        if shader is None:
            shader = MeshShader(params={"diffuse_color" : color})

        self.shader = shader

        if type(mesh) is str:
            mesh = OBJMesh.load(mesh)

        self.mesh = mesh

    def draw(self):
        self.shader.draw(app=self.parent_app, mesh=self.mesh, model_matrix=self.model_matrix)

    def _update(self, delta):
        pass

    def handle_event(self, ev):
        pass


class Cube(DrawnEntity):

    def __init__(self, parent_app, origin=Vector3D.ZERO, rotation=Vector3D.ZERO, scale=Vector3D.ONE, uv_mode = CubeMesh.UVMode.SAME, name="", color="white", shader=None):
        super().__init__(parent_app, mesh=CubeMesh(uv_mode=uv_mode), origin=origin, rotation=rotation, scale=scale, name=name, color=color, shader=shader)


    def handle_event(self, ev):
        pass

    def _update(self, delta):
        pass

class Skybox(DrawnEntity):
    def __init__(self, parent_app, cubemap_text):
        shader = SkyboxShader(cubemap_id=cubemap_text)
        # super().__init__(parent_app, mesh=SkyboxMesh(), name="skybox", shader=shader)
        super().__init__(parent_app, mesh=shader.sky_mesh, name="skybox", shader=shader)

    def draw(self):
        glDisable(GL_CULL_FACE)
        glDepthFunc(GL_LEQUAL)
        self.shader.draw(app=self.parent_app)#, mesh=self.mesh)
        glDepthFunc(GL_LESS)
        glEnable(GL_CULL_FACE)

    def handle_event(self, ev):
        pass

    def _update(self, delta):
        pass

class Sphere(DrawnEntity):
    def __init__(self, parent_app, origin=Vector3D.ZERO, rotation=Vector3D.ZERO, scale=Vector3D.ONE,
                 slices=32, stacks=0, name="", color="white", shader=None):
        mesh = SphereMesh(n_slices=slices, n_stacks=stacks)
        super().__init__(parent_app, mesh=mesh, origin=origin, rotation=rotation, scale=scale,
                         name=name, color=color, shader=shader)


    def handle_event(self, ev):
        pass

    def _update(self, delta):
        pass


class Plane(DrawnEntity):
    def __init__(self, parent_app, origin=Vector3D.ZERO, normal=Vector3D.UP, scale=Vector3D.ONE, color="white",
                 name="", shader=None):
        rotation = Vector3D(*euler_from_vectors(normal))

        super().__init__(parent_app, mesh=PlaneMesh(), origin=origin, rotation=rotation, scale=scale,
                         name=name,color=color, shader=shader)

    def _update(self, delta):
        pass

    def handle_event(self, ev):
        pass
