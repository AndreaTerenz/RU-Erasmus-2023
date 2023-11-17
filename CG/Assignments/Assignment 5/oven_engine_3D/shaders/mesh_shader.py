import os.path
from enum import Enum
from typing import Collection

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

from oven_engine_3D.shaders import BaseShader, DEFAULT_SHADER_DIR
from oven_engine_3D.utils.geometry import Vector2D
from oven_engine_3D.utils.misc import add_missing
from oven_engine_3D.utils.textures import TexturesManager


class MeshShader(BaseShader):
    INJECTION_BEGIN_ID = "//--INJECTION-BEGIN"
    INJECTION_END_ID = "//--INJECTION-END"
    INJECTED_CACHE_DIR = "shaders/cache"
    INJECTED_PREFIX = "tmp_"
    DEFAULT_VERTEX = os.path.join(DEFAULT_SHADER_DIR, "mesh.vert")
    DEFAULT_FRAG = os.path.join(DEFAULT_SHADER_DIR, "mesh.frag")

    class TransparencyMode(Enum):
        NONE = 0
        ALPHA_DISCARD = 1
        ALPHA_BLEND = 2

    def __init__(self, diffuse_texture: [int | str] = "", specular_texture: [int | str] = "",
                 injected_frag="", injected_vert="", **kwargs):

        v_path = MeshShader.DEFAULT_VERTEX
        f_path = MeshShader.DEFAULT_FRAG

        if injected_vert != "":
            v_path = MeshShader.inject_code(injected_vert, MeshShader.DEFAULT_VERTEX)
        if injected_frag != "":
            f_path = MeshShader.inject_code(injected_frag, MeshShader.DEFAULT_FRAG)

        super().__init__(transparent=False,
                         vert_shader_path=v_path,
                         frag_shader_path=f_path,
                         **kwargs)

        self.diff_tex_id = TexturesManager.load_texture(diffuse_texture, filtering=GL_LINEAR)
        self.spec_tex_id = TexturesManager.load_texture(specular_texture, filtering=GL_LINEAR)
        self.transparent = self.material_params["transparency_mode"] == MeshShader.TransparencyMode.ALPHA_BLEND

        self.add_attribute("a_position", 3, GLfloat, BaseShader.POS_ATTRIB_ID)
        self.add_attribute("a_normal", 3, GLfloat, BaseShader.NORM_ATTRIB_ID)
        self.add_attribute("a_uv", 2, GLfloat, BaseShader.UV_ATTRIB_ID)

        with self:
            self.set_diffuse_texture()
            self.set_specular_texture()
            self.set_material_uniforms()

    @staticmethod
    def inject_code(inject_source, inject_target,
                    injection_start=INJECTION_BEGIN_ID, injection_end=INJECTION_END_ID,
                    tmp_shader_dir=INJECTED_CACHE_DIR, tmp_shader_prefix=INJECTED_PREFIX, overwrite=False):
        with open(inject_source) as file:
            injected_lines = file.readlines()

        with open(inject_target) as file:
            source_lines = file.readlines()

        inj_start = source_lines.index(f"{injection_start}\n")
        inj_end = source_lines.index(f"{injection_end}\n")

        assert inj_start != -1 and inj_end != -1, "Unable to find injection points"

        src_head = source_lines[:inj_start + 1]
        src_tail = source_lines[inj_end:]
        source_lines = src_head + injected_lines + src_tail

        # Write to temp file
        if not os.path.exists(tmp_shader_dir):
            os.makedirs(tmp_shader_dir)

        pure_injected_name = os.path.basename(inject_source)
        pure_injected_name = os.path.splitext(pure_injected_name)[0]

        tmp_file = inject_target
        if not overwrite:
            tmp_file = os.path.join(tmp_shader_dir, f"{tmp_shader_prefix}{pure_injected_name}")

        open_mode = "w" if os.path.exists(tmp_file) else "x"

        with open(tmp_file, open_mode) as file:
            file.writelines(source_lines)

        return tmp_file

    def duplicate(self):
        return self.variation()

    def variation(self, **kwargs):
        p = {k: p for k, p in kwargs.items() if k in self.get_default_params()}
        add_missing(p, self.material_params)

        return MeshShader(
            diffuse_texture=kwargs.get("diffuse_texture", self.diff_tex_id),
            specular_texture=kwargs.get("specular_texture", self.spec_tex_id),
            **p
        )

    @staticmethod
    def get_default_params():
        return {
            "diffuse_color": "white",
            "specular_color": (.2, .2, .2),
            "ambient_color": (.1, .1, .1),
            "shininess": 5.,
            "unshaded": False,
            "receive_ambient": True,
            "transparency_mode": MeshShader.TransparencyMode.NONE,
            "alpha_cutoff": .2,
            "uv_scale": Vector2D.ONE,
            "use_distance_fade": False,
            "distance_fade": (60, 100),
            "uv_offset": Vector2D.ZERO,
        }

    def _ondraw(self, *args, **kwargs):
        mesh = kwargs["mesh"]
        app = kwargs["app"]
        model_matrix = kwargs["model_matrix"]

        self.link_attrib_vbo(mesh.vbo, mesh.attrib_order)
        self.set_model_matrix(model_matrix)

        self.set_light_uniforms(app.lights)
        self.set_camera_uniforms(app.camera)
        self.set_environment_uniforms(app.environment)
        self.set_skybox_texture(app.skybox.cubemap_id)

        time = np.float32(app.ticks / 1000.)
        self.set_time(time)

        mesh.draw()

    def set_material_uniforms(self, params=None):
        if params is None:
            params = self.material_params

        self.set_uniform_color(params["diffuse_color"], "u_material.diffuse_color")
        self.set_uniform_color(params["specular_color"], "u_material.specular_color")
        self.set_uniform_color(params["ambient_color"], "u_material.ambient_color")
        self.set_uniform_bool(params["unshaded"], "u_material.unshaded")
        self.set_uniform_bool(params["receive_ambient"], "u_material.receive_ambient")
        self.set_uniform_float(params["shininess"], "u_material.shininess")
        self.set_uniform_float(params["alpha_cutoff"], "u_material.alpha_cutoff")
        self.set_uniform_int(params["transparency_mode"].value, "u_material.transparency_mode")
        self.set_uniform_vec2D(params["uv_scale"], "u_uv_scale")
        self.set_uniform_vec2D(params["uv_offset"], "u_uv_offset")
        self.set_uniform_bool(params["use_distance_fade"], "u_material.use_distance_fade")
        self.set_uniform_float(params["distance_fade"], "u_material.distance_fade")

    def set_camera_uniforms(self, camera: 'Camera'):
        self.set_uniform_matrix(camera.projection_matrix.values, "u_projection_matrix")
        self.set_uniform_matrix(camera.view_matrix.values, "u_view_matrix")
        self.set_uniform_vec3D(camera.view_matrix.eye, "u_camera_position")

    def set_environment_uniforms(self, env: "Environment"):
        self.set_uniform_color(env.global_ambient, "u_env.global_ambient")
        self.set_uniform_float(env.global_ambient_strength, "u_env.ambient_strength")
        self.set_uniform_color(env.fog_color, "u_env.fog_color")
        self.set_uniform_float(env.start_fog, "u_env.start_fog")
        self.set_uniform_float(env.end_fog, "u_env.end_fog")
        self.set_uniform_float(env.fog_density, "u_env.fog_density")
        self.set_uniform_int  (env.fog_mode.value, "u_env.fog_mode")
        self.set_uniform_int  (env.tonemap.value, "u_env.tonemap_mode")

    def set_light_uniforms(self, lights: ["Light" | Collection]):
        if not isinstance(lights, Collection):
            lights = [lights]

        self.set_uniform_int(len(lights), "u_light_count")

        for idx, l in enumerate(lights):
            self.set_uniform_vec3D(l.origin, f"u_lights[{idx}].position")
            self.set_uniform_float(l.radius, f"u_lights[{idx}].radius")
            self.set_uniform_float(l.intensity, f"u_lights[{idx}].intensity")
            self.set_uniform_bool(l.sun, f"u_lights[{idx}].is_sun")
            self.set_uniform_float(l.attenuation, f"u_lights[{idx}].attenuation")
            self.set_uniform_color(l.diffuse, f"u_lights[{idx}].diffuse")
            self.set_uniform_color(l.specular, f"u_lights[{idx}].specular")
            self.set_uniform_color(l.ambient, f"u_lights[{idx}].ambient")

    def set_model_matrix(self, matrix):
        self.set_uniform_matrix(matrix.values, "u_model_matrix")

    def set_diffuse_texture(self):
        self.set_texture(0, self.diff_tex_id,
                         "u_material.diffuse_tex", tex_flag_uniform_name="u_material.use_diff_texture")

    def set_specular_texture(self):
        self.set_texture(1, self.spec_tex_id,
                         "u_material.specular_tex", tex_flag_uniform_name="u_material.use_spec_texture")

    def set_skybox_texture(self, skybox_tex_id):
        self.set_texture(1, skybox_tex_id,
                         "u_skybox", texture_type=GL_TEXTURE_CUBE_MAP)

    def set_time(self, value: float):
        self.set_uniform_float(value, "u_time")