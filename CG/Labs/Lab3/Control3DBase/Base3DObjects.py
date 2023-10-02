import math
from abc import abstractmethod, ABC

from OpenGL.GL import *
from pygame.locals import *

# from Control3DBase.Geometry import Vector3D
from Control3DBase.Matrices import ModelMatrix, ViewMatrix, ProjectionMatrix
from Control3DBase.Shaders import MeshShader
from oven_engine.utils.geometry import Vector3D
from oven_engine.utils.gl.gl3d import CUBE_POSITION_ARRAY, CUBE_NORMAL_ARRAY, draw_cube


class Entity3D(ABC):
    def __init__(self, parent_app, origin = Vector3D.ZERO, size=1., color=(1.0, 0.0, 1.0), vertex_shader=None, frag_shader=None):
        self.parent_app = parent_app
        self.origin = origin
        self.rotation = Vector3D.ZERO
        self.scale = Vector3D.ONE
        self.model_matrix = ModelMatrix()
        self.shader = None

    def __update_model_matrix(self):
        self.model_matrix.load_identity()
        self.model_matrix.add_translation(self.origin)
        self.model_matrix.add_rotation(self.rotation)
        self.model_matrix.add_scale(self.scale)

        if self.shader is not None:
            self.shader.set_model_matrix(self.model_matrix.matrix)

    @abstractmethod
    def draw(self):
        self.shader.use()

        for k in range(6):
            glDrawArrays(GL_TRIANGLE_FAN, k*4, 4)

    def update(self, delta):
        self._update(delta)
        self.__update_model_matrix()

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

class Camera(Entity3D):
    def __init__(self, parent_app, eye = Vector3D.ZERO, look_at = Vector3D.FORWARD, ratio = 16./9., near=.5, far=100, up_vec=Vector3D.UP):
        super().__init__(parent_app, origin=eye, size=0., color=None, vertex_shader=None, frag_shader=None)

        self.projection_matrix = ProjectionMatrix.perspective(math.tau / 8., ratio, near=near, far=far)
        self.view_matrix = ViewMatrix()
        self.target = Vector3D.ZERO

        self.look_at(look_at, up_vec)

        self.slide_keys = {
            K_w: Vector3D.UP,
            K_s: Vector3D.DOWN,
            K_a: Vector3D.LEFT,
            K_d: Vector3D.RIGHT,
            K_q: Vector3D.FORWARD,
            K_e: Vector3D.BACKWARD,
        }

        self.rotation_keys = {
            K_UP: Vector3D.UP,
            K_DOWN: Vector3D.DOWN,
        }

        self.keys = {key: False for key in list(self.slide_keys.keys()) + list(self.rotation_keys.keys())}

    def draw(self):
        pass

    def _update(self, delta):
        slide_dir = Vector3D.ZERO
        for key, _dir in self.slide_keys.items():
            state = self.keys[key]
            fact = 1. if state else 0.
            slide_dir += _dir * fact

        slide_dir = slide_dir.normalized
        if slide_dir != Vector3D.ZERO:
            self.slide(slide_dir * delta * 5.)

        target_slide_dir = Vector3D.ZERO
        for key, _dir in self.rotation_keys.items():
            state = self.keys[key]
            fact = 1. if state else 0.
            target_slide_dir += _dir * fact

        target_slide_dir = target_slide_dir.normalized
        if target_slide_dir != Vector3D.ZERO:
            self.slide_target(target_slide_dir * delta * 5.)

    def look_at(self, target, up=Vector3D.ZERO):
        self.target = target
        self.view_matrix.look_at(self.origin, target, up)

    def slide(self, offset):
        self.origin += offset
        self.target += offset
        self.view_matrix.slide(*offset)

    def slide_target(self, offset, up_vec = Vector3D.UP):
        self.look_at(self.target + offset, up_vec)

    def handle_event(self, event):
        if not (hasattr(event, 'key')):
            return

        if event.key in self.keys.keys():
            self.keys[event.key] = (event.type == KEYDOWN)

        """if event.key == K_UP:
            self.view_matrix.rotate_x(-math.tau/10.)
        elif event.key == K_DOWN:
            self.view_matrix.rotate_x(math.tau/10.)

        if event.key == K_LEFT:
            self.view_matrix.rotate_y(-math.tau/10.)
        elif event.key == K_RIGHT:
            self.view_matrix.rotate_y(math.tau/10.)"""


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