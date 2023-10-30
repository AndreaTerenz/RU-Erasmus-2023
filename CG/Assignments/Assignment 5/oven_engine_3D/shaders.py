import os.path
import os.path as path
from typing import Collection

import OpenGL.GLUT
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.error import GLError
from pygame import Color

from oven_engine_3D.utils.matrices import Matrix
from oven_engine_3D.utils.textures import TexturesManager
from oven_engine_3D.utils.geometry import Vector3D

DEFAULT_SHADER_DIR = "shaders"
DEFAULT_VERTEX = os.path.join(DEFAULT_SHADER_DIR, "simple3D.vert")
DEFAULT_FRAG =  os.path.join(DEFAULT_SHADER_DIR, "simple3D.frag")
DEFAULT_PARAMS = {
                "diffuse_color" : Color("white"),
                "specular_color" : (.2, .2, .2),
                "ambient_color" : (.1, .1, .1),
                "shininess" : 5.,
                "unshaded" : False,
                "receive_ambient" : True
            }

def add_missing(dict1, dict2):
    dict1.update({key:value for key,value in dict2.items() if not key in dict1})

class MeshShader:
    compiled_vert_shaders = {}
    compiled_frag_shaders = {}

    def __init__(self,
                 vert_shader_path = DEFAULT_VERTEX, frag_shader_path = DEFAULT_FRAG,
                 diffuse_texture : [int|str] = "", params=None):

        self.vert_shader_path = vert_shader_path
        self.frag_shader_path = frag_shader_path

        self.renderingProgramID = MeshShader.get_shader_program(self.vert_shader_path, self.frag_shader_path)

        self.uniform_locations = {}

        self.positionLoc = self.enable_attrib_array("a_position")
        self.normalLoc   = self.enable_attrib_array("a_normal")
        self.uvLoc       = self.enable_attrib_array("a_uv")

        self.diff_tex_id = -1
        if type(diffuse_texture) is int and diffuse_texture >= 0:
            self.diff_tex_id = diffuse_texture
        elif type(diffuse_texture) is str and diffuse_texture != "":
            self.diff_tex_id = TexturesManager.load_texture(diffuse_texture, filtering=GL_LINEAR)

        if params is None:
            params = DEFAULT_PARAMS

        self.params = params
        add_missing(self.params, DEFAULT_PARAMS)

        self.use()
        self.set_diffuse_texture(self.diff_tex_id)
        self.set_material_uniforms(self.params)

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
            vert_shader_path=kwargs.get("vert_shader_path", self.vert_shader_path),
            frag_shader_path=kwargs.get("frag_shader_path", self.frag_shader_path),
        )

    @staticmethod
    def get_shader_program(vert_path : str, frag_path : str):
        print("Creating shader program...")

        vert_shader = MeshShader.compile_shader(vert_path, GL_VERTEX_SHADER)
        frag_shader = MeshShader.compile_shader(frag_path, GL_FRAGMENT_SHADER)

        progID = glCreateProgram()

        assert progID != 0, print("Failed to create program")

        glAttachShader(progID, vert_shader)
        glAttachShader(progID, frag_shader)
        glLinkProgram(progID)

        assert glGetProgramiv(progID, GL_LINK_STATUS) == 1, print("Failed to link")

        return progID

    @staticmethod
    def compile_shader(shader_file: str, shader_type: int, use_fallback = True):
        assert shader_type in [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER], print("Invalid shader type")

        shader_path = shader_file
        """if shader_folder != "":
            shader_path = path.join(shader_folder, shader_file)"""

        print(f"\tCompiling shader file {shader_path}...", end="")

        lookup : dict = MeshShader.compiled_vert_shaders if shader_type == GL_VERTEX_SHADER else MeshShader.compiled_frag_shaders

        if shader_path in lookup:
            print("done (already compiled)")
            return lookup[shader_path]

        shader_id = glCreateShader(shader_type)

        assert shader_id != 0, print("Couldn't create shader")

        try:
            with open(shader_path) as shader_file:
                glShaderSource(shader_id, shader_file.read())
        except FileNotFoundError:
            assert use_fallback, print("Fallback shader disabled - compilation failed")

            print(f"Unable to find shader source - using fallback shader")

            fallback_path = ""
            if shader_type == GL_VERTEX_SHADER:
                fallback_path = path.join(DEFAULT_SHADER_DIR, DEFAULT_VERTEX)
            elif shader_type == GL_FRAGMENT_SHADER:
                fallback_path = path.join(DEFAULT_SHADER_DIR, DEFAULT_FRAG)

            return MeshShader.compile_shader(fallback_path, shader_type, False)

        glCompileShader(shader_id)
        result = glGetShaderiv(shader_id, GL_COMPILE_STATUS)
        assert result == 1, print(f"Couldn't compile shader\nShader compilation Log:\n{str(glGetShaderInfoLog(shader_id))}")

        lookup[shader_path] = shader_id

        print("done")

        return shader_id

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

    def set_uniform_matrix(self, matrix: Matrix, uniform_name):
        loc = self.get_uniform_loc(uniform_name)
        glUniformMatrix4fv(loc, 1, True, matrix.values)

    @staticmethod
    def __get_color(color):
        if type(color) is Color:
            color = color.normalize()
        elif type(color) in [int, float]:
            color = color, color, color, 1.

        if len(color) == 3:
            color = (*color, 1.)

        return color

    def set_uniform_color(self, color, uniform_name):
        loc = self.get_uniform_loc(uniform_name)
        color = MeshShader.__get_color(color)

        glUniform4f(loc, *color)

    def set_uniform_vec3D(self, vector: Vector3D, uniform_name, homogenous=True, w=1.0):
        loc = self.get_uniform_loc(uniform_name)

        if homogenous:
            glUniform4f(loc, *vector, w)
        else:
            glUniform3f(loc, *vector)

    def set_uniform_float(self, value: [float|Collection], uniform_name):
        count = 1 if not isinstance(value, Collection) else len(value)

        loc = self.get_uniform_loc(uniform_name)
        glUniform1fv(loc, count, value)

    def set_uniform_int(self, value: [int|Collection], uniform_name):
        count = 1 if not isinstance(value, Collection) else len(value)

        loc = self.get_uniform_loc(uniform_name)
        glUniform1iv(loc, count, value)

    def set_uniform_bool(self, value: [bool|Collection], uniform_name):
        if not isinstance(value, Collection):
            value = [value]

        value = [int(v) for v in value]
        self.set_uniform_int(value, uniform_name)

    def set_uniform_sampler2D(self, uniform_name, texture_slot = 0):
        loc = self.get_uniform_loc(uniform_name)
        glUniform1i(loc, texture_slot)

    def activate_texture(self, texture_id = -1, texture_slot = 0):
        if texture_id <= 0:
            texture_id = self.diff_tex_id

        glActiveTexture(GL_TEXTURE0 + texture_slot)
        glBindTexture(GL_TEXTURE_2D, texture_id)

    def set_material_uniforms(self, params):
        self.set_material_diffuse(params["diffuse_color"])
        self.set_material_specular(params["specular_color"])
        self.set_material_ambient(params["ambient_color"])
        self.set_unshaded(params["unshaded"])
        self.set_receive_ambient(params["receive_ambient"])
        self.set_shininess(params["shininess"])

    def set_camera_uniforms(self, camera: 'Camera'):
        self.set_uniform_matrix(camera.projection_matrix, "u_projection_matrix")
        self.set_uniform_matrix(camera.view_matrix, "u_view_matrix")
        self.set_uniform_vec3D(camera.view_matrix.eye, "u_camera_position")

    def set_model_matrix(self, matrix):
        self.set_uniform_matrix(matrix, "u_model_matrix")

    def set_mesh_attributes(self, mesh_vbo: int):
        values_per_attrib = [3, 3, 2]
        locations = [self.positionLoc, self.normalLoc, self.uvLoc]
        attrib_sizes = [sizeof(GLfloat)] * len(values_per_attrib)

        total_size = sum([s * v for s, v in zip(attrib_sizes, values_per_attrib)])

        glBindBuffer(GL_ARRAY_BUFFER, mesh_vbo)

        offset_size = 0
        for idx in range(len(locations)):
            glVertexAttribPointer(locations[idx], values_per_attrib[idx], GL_FLOAT, False, total_size, ctypes.c_void_p(offset_size))
            offset_size += attrib_sizes[idx] * values_per_attrib[idx]

        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def set_light_uniforms(self, lights: ["Light"|Collection]):
        if not isinstance(lights, Collection):
            lights = [lights]

        self.set_uniform_int(len(lights), "u_light_count")

        for idx, l in enumerate(lights):
            self.set_uniform_vec3D(l.origin, f"u_lights[{idx}].position")
            self.set_uniform_float(l.radius, f"u_lights[{idx}].radius")
            self.set_uniform_color(l.color, f"u_lights[{idx}].diffuse")
            self.set_uniform_color(l.color, f"u_lights[{idx}].specular")
            self.set_uniform_color(l.ambient, f"u_lights[{idx}].ambient")

    def set_material_diffuse(self, color):
        self.set_uniform_color(color, "u_material.diffuse_color")

    def set_diffuse_texture(self, diff_tex_id):
        self.set_uniform_bool((diff_tex_id > 0), "u_material.has_texture")
        self.set_uniform_sampler2D("u_material.diffuse_tex", 0)

    def set_material_specular(self, color):
        self.set_uniform_color(color, "u_material.specular_color")

    def set_material_ambient(self, color):
        self.set_uniform_color(color, "u_material.ambient_color")

    def set_unshaded(self, state: bool):
        # self.unshaded = state
        self.set_uniform_bool(state, "u_material.unshaded")

    def set_receive_ambient(self, state: bool):
        # self.receive_ambient = state
        self.set_uniform_bool(state, "u_material.receive_ambient")

    def set_shininess(self, value: float):
        self.set_uniform_float(value, "u_material.shininess")

    def set_time(self, value: float):
        self.set_uniform_float(value, "u_time")
