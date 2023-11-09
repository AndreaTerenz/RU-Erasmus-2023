import math
import os.path

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

from oven_engine_3D.meshes import SkyboxMesh
from oven_engine_3D.shaders import DEFAULT_SHADER_DIR, BaseShader


class SkyboxShader(BaseShader):
    SKY_VERTEX = os.path.join(DEFAULT_SHADER_DIR, "sky.vert")
    SKY_FRAG = os.path.join(DEFAULT_SHADER_DIR, "sky.frag")

    def __init__(self, cubemap_id: int):

        super().__init__(vert_shader_path=SkyboxShader.SKY_VERTEX,
                         frag_shader_path=SkyboxShader.SKY_FRAG)

        self.sky_mesh = SkyboxMesh()
        self.cubemap_id = cubemap_id

        # No need for on_compile since we're never deferring compilation for a skybox shader

        self.add_attribute("a_position", 3, GLfloat, BaseShader.POS_ATTRIB_ID)

        self.use()
        self.set_rotation(self.material_params["rotation"])
        self.set_cubemap()

    def _ondraw(self, *args, **kwargs):
        app = kwargs["app"]

        self.link_attrib_vbo(self.sky_mesh.vbo, self.sky_mesh.attrib_order)
        self.set_camera_uniforms(app.camera)
        self.set_uniform_int(app.environment.tonemap.value, "u_tonemap_mode")

        time = np.float32(app.ticks / 1000.)
        self.set_time(time)

        self.sky_mesh.draw()

    def set_rotation(self, angle):
        self.set_uniform_float(angle, "u_rotation")

    def set_cubemap(self):
        self.set_texture(0, self.cubemap_id,
                         "u_material.u_cubemap", texture_type=GL_TEXTURE_CUBE_MAP)

    def set_camera_uniforms(self, camera: 'Camera'):
        self.set_uniform_matrix(camera.projection_matrix.values, "u_projection_matrix")

        v = camera.view_matrix.values
        v = np.array(v, dtype="float32").reshape(4, 4)
        v[:3, 3] = 0
        v = v.flatten()

        self.set_uniform_matrix(v, "u_view_matrix")

    """def set_environment_uniforms(self, env: Environment):
        self.set_uniform_int(env.tonemap.value, "u_tonemap_mode")

    def set_model_matrix(self, matrix):
        self.set_uniform_matrix(matrix.values, "u_model_matrix")"""

    def set_time(self, value: float):
        self.set_uniform_float(value, "u_time")

    @staticmethod
    def get_default_params():
        return {
            "rotation": math.tau / 4.
        }