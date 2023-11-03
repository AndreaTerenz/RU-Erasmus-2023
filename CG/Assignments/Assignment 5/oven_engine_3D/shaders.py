import os.path
from abc import abstractmethod, ABC
from typing import Collection

import OpenGL.GLUT
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.error import GLError
from pygame import Color

from oven_engine_3D.environment import Environment
from oven_engine_3D.utils.geometry import Vector3D
from oven_engine_3D.utils.misc import is_collection
from oven_engine_3D.utils.textures import TexturesManager

DEFAULT_SHADER_DIR = "shaders"

def add_missing(dict1, dict2):
    dict1.update({key:value for key,value in dict2.items() if not key in dict1})

class BaseShader(ABC):
    compiled_vert_shaders = {}
    compiled_frag_shaders = {}

    class ShaderAttribute:
        def __init__(self, attrib_name: str, attrib_loc: int, attrib_elem_count: int, attrib_type: int):
            self.name = attrib_name
            self.loc = attrib_loc
            self.elem_count = attrib_elem_count
            self.type = attrib_type

    def __init__(self, vert_shader_path, frag_shader_path, params=None):

        self.vert_shader_path = vert_shader_path
        self.frag_shader_path = frag_shader_path

        self.renderingProgramID = MeshShader.get_shader_program(self.vert_shader_path, self.frag_shader_path)

        self.uniform_locations = {}
        self.attributes = {}

        def_params = self.__class__.get_default_params()
        if params is None:
            params = def_params

        self.params = params
        add_missing(self.params, def_params)

    def add_attribute(self, attrib_name, attrib_elem_count, attrib_type):
        if attrib_name in self.attributes:
            return

        attrib_loc = self.enable_attrib_array(attrib_name)
        self.attributes[attrib_name] = BaseShader.ShaderAttribute(attrib_name, attrib_loc, attrib_elem_count, attrib_type)

        return attrib_loc

    @staticmethod
    @abstractmethod
    def get_default_params():
        return {}

    @staticmethod
    def get_shader_program(vert_path: str, frag_path: str):
        print("Creating shader program...")

        vert_shader = BaseShader.compile_shader_file(vert_path, GL_VERTEX_SHADER)
        frag_shader = BaseShader.compile_shader_file(frag_path, GL_FRAGMENT_SHADER)

        progID = glCreateProgram()

        assert progID != 0, print("Failed to create program")

        glAttachShader(progID, vert_shader)
        glAttachShader(progID, frag_shader)
        glLinkProgram(progID)

        assert glGetProgramiv(progID, GL_LINK_STATUS) == 1, print("Failed to link")

        return progID

    @staticmethod
    def compile_shader_file(shader_file: str, shader_type: int):
        assert shader_type in [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER], print("Invalid shader type")

        shader_path = shader_file
        """if shader_folder != "":
            shader_path = path.join(shader_folder, shader_file)"""

        print(f"\tCompiling shader file {shader_path}...", end="")

        lookup: dict = BaseShader.compiled_vert_shaders if shader_type == GL_VERTEX_SHADER else BaseShader.compiled_frag_shaders

        if shader_path in lookup:
            print("done (already compiled)")
            return lookup[shader_path]

        shader_id = glCreateShader(shader_type)

        assert shader_id != 0, print("Couldn't create shader")

        try:
            with open(shader_path) as shader_file:
                glShaderSource(shader_id, shader_file.read())
        except FileNotFoundError:
            assert False, print("Shader compilation failed")

        glCompileShader(shader_id)
        result = glGetShaderiv(shader_id, GL_COMPILE_STATUS)
        assert result == 1, print(
            f"Couldn't compile shader\nShader compilation Log:\n{str(glGetShaderInfoLog(shader_id))}")

        lookup[shader_path] = shader_id

        print("done")

        return shader_id

    @staticmethod
    def activate_texture(texture_id = -1, texture_slot = 0):
        if texture_id <= 0:
            return

        glActiveTexture(GL_TEXTURE0 + texture_slot)
        glBindTexture(GL_TEXTURE_2D, texture_id)

    def link_attrib_vbo(self, vbo):
        attrib_objects = [a for a in self.attributes.values()]

        locations = [a.loc for a in attrib_objects]
        values_per_attrib = [a.elem_count for a in attrib_objects]
        attrib_types = [a.type for a in attrib_objects]

        attrib_sizes = [sizeof(t) for t in attrib_types]
        total_size = sum([s * v for s, v in zip(attrib_sizes, values_per_attrib)])

        glBindBuffer(GL_ARRAY_BUFFER, vbo)

        offset_size = 0
        for idx in range(len(locations)):
            glVertexAttribPointer(locations[idx], values_per_attrib[idx], GL_FLOAT, False, total_size, ctypes.c_void_p(offset_size))
            offset_size += attrib_sizes[idx] * values_per_attrib[idx]

        glBindBuffer(GL_ARRAY_BUFFER, 0)

    @staticmethod
    def __get_color(color):
        if type(color) is str:
            color = Color(color)
        if type(color) is Color:
            color = color.normalize()
        elif type(color) in [int, float]:
            color = color, color, color, 1.

        if len(color) == 3:
            color = (*color, 1.)

        return color

    @property
    def info_log(self):
        return glGetProgramInfoLog(self.renderingProgramID)

    def enable_attrib_array(self, attrib_name):
        attrib_loc = self.get_attrib_loc(attrib_name)

        assert attrib_loc != -1, "Attribute not found!"

        glEnableVertexAttribArray(attrib_loc)

        return attrib_loc

    def get_attrib_loc(self, attrib_name):
        return glGetAttribLocation(self.renderingProgramID, attrib_name)

    def use(self):
        try:
            glUseProgram(self.renderingProgramID)
        except OpenGL.error.GLError:
            print(f"Failed to use shader - {self.info_log}")
            raise

    def get_uniform_loc(self, uniform_name):
        if uniform_name in self.uniform_locations:
            return self.uniform_locations[uniform_name]

        output = glGetUniformLocation(self.renderingProgramID, uniform_name)

        if output != -1:
            self.uniform_locations[uniform_name] = output

        return output

    def get_uniform_int(self, uniform_name, count = 1):
        return self.get_uniform_value(uniform_name, ctypes.c_int, count)

    def get_uniform_float(self, uniform_name, count = 1):
        return self.get_uniform_value(uniform_name, ctypes.c_float, count)

    def get_uniform_color(self, uniform_name):
        tmp = self.get_uniform_float(uniform_name, 4)
        return Color(*(int(v*255.) for v in tmp))

    def get_uniform_value(self, uniform_name, datatype, count = 1):
        loc = self.get_uniform_loc(uniform_name)
        output = (datatype * count)()

        if loc == -1:
            return None

        glGetUniformfv(self.renderingProgramID, loc, output)

        return list(output) if count > 1 else output[0]

    def set_uniform_matrix(self, matrix, uniform_name):
        loc = self.get_uniform_loc(uniform_name)
        glUniformMatrix4fv(loc, 1, True, matrix)

    def set_uniform_color(self, color, uniform_name):
        loc = self.get_uniform_loc(uniform_name)
        color = BaseShader.__get_color(color)

        glUniform4f(loc, *color)

    def set_uniform_vec3D(self, vector: Vector3D, uniform_name, homogenous=True, w=1.0):
        loc = self.get_uniform_loc(uniform_name)

        if homogenous:
            glUniform4f(loc, *vector, w)
        else:
            glUniform3f(loc, *vector)

    def set_uniform_float(self, value: [float|Collection], uniform_name):
        count = 1 if not is_collection(value) else len(value)

        loc = self.get_uniform_loc(uniform_name)
        glUniform1fv(loc, count, value)

    def set_uniform_int(self, value: [int|Collection], uniform_name):
        count = 1 if not is_collection(value) else len(value)

        loc = self.get_uniform_loc(uniform_name)
        glUniform1iv(loc, count, value)

    def set_uniform_bool(self, value: [bool|Collection], uniform_name):
        if not is_collection(value):
            value = [value]

        value = [int(v) for v in value]
        self.set_uniform_int(value, uniform_name)

    def set_uniform_sampler2D(self, uniform_name, texture_slot = 0):
        loc = self.get_uniform_loc(uniform_name)
        glUniform1i(loc, texture_slot)

class MeshShader(BaseShader):
    DEFAULT_VERTEX = os.path.join(DEFAULT_SHADER_DIR, "mesh.vert")
    DEFAULT_FRAG =  os.path.join(DEFAULT_SHADER_DIR, "mesh.frag")

    def __init__(self, diffuse_texture : [int|str] = "", params=None, ignore_camera_pos=False):

        super().__init__(params=params,
                         vert_shader_path=MeshShader.DEFAULT_VERTEX,
                         frag_shader_path=MeshShader.DEFAULT_FRAG)

        self.add_attribute("a_position", 3, GLfloat)
        self.add_attribute("a_normal", 3, GLfloat)
        self.add_attribute("a_uv", 2, GLfloat)

        self.ignore_camera_pos = ignore_camera_pos

        self.diff_tex_id = -1
        if type(diffuse_texture) is int and diffuse_texture >= 0:
            self.diff_tex_id = diffuse_texture
        elif type(diffuse_texture) is str and diffuse_texture != "":
            self.diff_tex_id = TexturesManager.load_texture(diffuse_texture, filtering=GL_LINEAR)

        self.use()
        self.set_diffuse_texture(self.diff_tex_id)
        self.set_material_uniforms()

        print()


    def duplicate(self):
        return self.variation()

    def variation(self, **kwargs):
        print("Shader variation:\n\t", end="")
        print(*kwargs.items(), sep="\n\t")

        p = kwargs.get("params", {})
        add_missing(p, self.params)

        return MeshShader(
            params=p,
            diffuse_texture=kwargs.get("diffuse_texture", self.diff_tex_id),
        )

    @staticmethod
    def get_default_params():
        return {
                "diffuse_color" : "white",
                "specular_color" : (.2, .2, .2),
                "ambient_color" : (.1, .1, .1),
                "shininess" : 5.,
                "unshaded" : False,
                "receive_ambient" : True
            }

    def activate_diffuse_text(self):
        BaseShader.activate_texture(self.diff_tex_id, texture_slot = 0)

    def set_material_uniforms(self, params = None):
        if params is None:
            params = self.params

        self.set_uniform_color(params["diffuse_color"], "u_material.diffuse_color")
        self.set_uniform_color(params["specular_color"], "u_material.specular_color")
        self.set_uniform_color(params["ambient_color"], "u_material.ambient_color")
        self.set_uniform_bool (params["unshaded"], "u_material.unshaded")
        self.set_uniform_bool (params["receive_ambient"], "u_material.receive_ambient")
        self.set_uniform_float(params["shininess"], "u_material.shininess")

    def set_camera_uniforms(self, camera: 'Camera'):
        self.set_uniform_matrix(camera.projection_matrix.values, "u_projection_matrix")

        v = camera.view_matrix.values

        if self.ignore_camera_pos:

            v = np.array(v, dtype="float32").reshape(4,4)
            v[:3, 3] = 0
            v = v.flatten()

        # self.set_uniform_matrix(camera.view_matrix.values, "u_view_matrix")
        self.set_uniform_matrix(v, "u_view_matrix")
        self.set_uniform_vec3D(camera.view_matrix.eye, "u_camera_position")

    def set_environment_uniforms(self, env: Environment):
        self.set_uniform_color(env.global_ambient, "u_env.global_ambient")
        self.set_uniform_color(env.fog_color, "u_env.fog_color")
        self.set_uniform_float(env.start_fog, "u_env.start_fog")
        self.set_uniform_float(env.end_fog, "u_env.end_fog")
        self.set_uniform_float(env.fog_density, "u_env.fog_density")
        self.set_uniform_int(env.fog_mode.value, "u_env.fog_mode")
        self.set_uniform_int(env.tonemap.value, "u_env.tonemap_mode")

    def set_light_uniforms(self, lights: ["Light"|Collection]):
        if not isinstance(lights, Collection):
            lights = [lights]

        self.set_uniform_int(len(lights), "u_light_count")

        for idx, l in enumerate(lights):
            self.set_uniform_vec3D(l.origin, f"u_lights[{idx}].position")
            self.set_uniform_float(l.radius, f"u_lights[{idx}].radius")
            self.set_uniform_float(l.intensity, f"u_lights[{idx}].intensity")
            self.set_uniform_float(l.attenuation, f"u_lights[{idx}].attenuation")
            self.set_uniform_color(l.color, f"u_lights[{idx}].diffuse")
            self.set_uniform_color(l.color, f"u_lights[{idx}].specular")
            self.set_uniform_color(l.ambient, f"u_lights[{idx}].ambient")

    def set_model_matrix(self, matrix):
        self.set_uniform_matrix(matrix.values, "u_model_matrix")

    def set_diffuse_texture(self, diff_tex_id):
        self.set_uniform_bool((diff_tex_id > 0), "u_material.has_texture")
        self.set_uniform_sampler2D("u_material.diffuse_tex", 0)

    def set_time(self, value: float):
        self.set_uniform_float(value, "u_time")

class SkyboxShader(BaseShader):
    SKY_VERTEX = os.path.join(DEFAULT_SHADER_DIR, "sky.vert")
    SKY_FRAG = os.path.join(DEFAULT_SHADER_DIR, "sky.frag")

    def __init__(self, diffuse_texture : [int|str] = "", params=None):

        super().__init__(params=params,
                         vert_shader_path=SkyboxShader.SKY_VERTEX,
                         frag_shader_path=SkyboxShader.SKY_FRAG)

        self.add_attribute("a_position", 3, GLfloat)
        self.add_attribute("a_normal", 3, GLfloat)
        self.add_attribute("a_uv", 2, GLfloat)

        self.diff_tex_id = -1
        if type(diffuse_texture) is int and diffuse_texture >= 0:
            self.diff_tex_id = diffuse_texture
        elif type(diffuse_texture) is str and diffuse_texture != "":
            self.diff_tex_id = TexturesManager.load_texture(diffuse_texture, filtering=GL_LINEAR)

        print()

    def set_material_uniforms(self, params = None):
        if params is None:
            params = self.params

        self.set_uniform_color(params["diffuse_color"], "u_material.diffuse_color")

    def set_camera_uniforms(self, camera: 'Camera'):
        self.set_uniform_matrix(camera.projection_matrix.values, "u_projection_matrix")
        self.set_uniform_matrix(camera.view_matrix.values, "u_view_matrix")

    def set_environment_uniforms(self, env: Environment):
        self.set_uniform_int(env.tonemap.value, "u_env.tonemap_mode")

    @staticmethod
    def get_default_params():
        return {}



