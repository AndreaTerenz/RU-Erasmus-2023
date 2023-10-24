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

DEFAULT_SHADER_DIR = path.join("oven_engine_3D", "Shader Files")
DEFAULT_VERTEX = "simple3D.vert"
DEFAULT_FRAG = "simple3D.frag"


def uniform_updater(func):
    def foo(self, V, N, *args, **kwargs):
        if N in self.uniform_values and self.uniform_values[N] == V:
            return

        self.uniform_values[N] = V
        func(self, V, N, *args, **kwargs)

    return foo

class MeshShader:
    compiled_vert_shaders = {}
    compile_frag_shaders = {}

    def __init__(self,
                 vert_shader_path = DEFAULT_VERTEX, frag_shader_path = DEFAULT_FRAG, shader_folder : str = DEFAULT_SHADER_DIR,
                 diffuse_color=Color("white"), specular_color=(.2, .2, .2), ambient_color=(.1, .1, .1),
                 shininess=30., unshaded=False, receive_ambient=True, diffuse_texture : [int|str] = "", vertID=-1, fragID=-1):

        print("Compiling shaders...")

        v = vertID if vertID != -1 else vert_shader_path
        f = fragID if fragID != -1 else frag_shader_path

        self.renderingProgramID, self.vert_id, self.frag_id = MeshShader.get_shader_program(v, f, shader_folder)

        self.uniform_locations = {}
        self.uniform_values = {}

        self.positionLoc = self.enable_attrib_array("a_position")
        self.normalLoc = self.enable_attrib_array("a_normal")
        self.uvLoc = self.enable_attrib_array("a_uv")

        self.unshaded = unshaded
        self.receive_ambient = receive_ambient

        self.diff_tex_id = -1

        if type(diffuse_texture) is int and diffuse_texture >= 0:
            self.diff_tex_id = diffuse_texture
        elif diffuse_texture != "":
            self.diff_tex_id = TexturesManager.load_texture(diffuse_texture, filtering=GL_LINEAR)

        self.use()
        self.set_material_diffuse(diffuse_color)
        self.set_material_specular(specular_color)
        self.set_material_ambient(ambient_color)
        self.set_diffuse_texture(self.diff_tex_id)
        self.set_unshaded(unshaded)
        self.set_receive_ambient(receive_ambient)
        self.set_shininess(shininess)

    def duplicate(self):
        return self.variation()

    def variation(self, **kwargs):
        return MeshShader(
            diffuse_color=kwargs.get("diffuse_color", self.get_uniform_color("u_material.diffuse")),
            specular_color=kwargs.get("specular_color", self.get_uniform_color("u_material.specular")),
            ambient_color=kwargs.get("ambient_color", self.get_uniform_color("u_material.ambient")),
            shininess=kwargs.get("shininess", self.get_uniform_float("u_material.shininess")),
            unshaded=kwargs.get("unshaded", self.unshaded),
            receive_ambient=kwargs.get("receive_ambient", self.receive_ambient),
            diffuse_texture=kwargs.get("diffuse_texture", self.diff_tex_id),
            vertID=kwargs.get("vertID", self.vert_id),
            fragID=kwargs.get("fragID", self.frag_id),
        )

    @staticmethod
    def get_shader_program(vert_path : [int|str], frag_path : [int|str], src_dir):
        if type(vert_path) == str:
            vert_shader = MeshShader.compile_shader(vert_path, GL_VERTEX_SHADER, shader_folder=src_dir)
        else:
            vert_shader = vert_path

        if type(frag_path) == str:
            frag_shader = MeshShader.compile_shader(frag_path, GL_FRAGMENT_SHADER, shader_folder=src_dir)
        else:
            frag_shader = frag_path

        progID = glCreateProgram()

        assert progID != 0, print("Couldn't create program")

        glAttachShader(progID, vert_shader)
        glAttachShader(progID, frag_shader)
        glLinkProgram(progID)

        assert glGetProgramiv(progID, GL_LINK_STATUS) == 1, print("Couldn't link program")

        return progID, vert_shader, frag_shader

    @staticmethod
    def compile_shader(shader_file: str, shader_type: int, use_fallback = True, shader_folder: str = ""):
        if not shader_type in [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER]:
            return -1

        lookup = MeshShader.compiled_vert_shaders if shader_type == GL_VERTEX_SHADER else MeshShader.compile_frag_shaders

        if shader_file in lookup:
            print("\tShader already compiled")
            return lookup[shader_file]

        shader_id = glCreateShader(shader_type)

        if shader_id == 0:
            print("Couldn't create shader")
            return -1

        shader_path = shader_file
        if shader_folder != "":
            shader_path = path.join(shader_folder, shader_file)

        try:
            with open(shader_path) as shader_file:
                glShaderSource(shader_id, shader_file.read())
        except FileNotFoundError:
            print(f"Couldn't find shader file: '{shader_path}'")

            assert use_fallback, print("Fallback shader disabled - compilation failed")

            print("Using fallback shader")
            fallback_path = ""
            if shader_type == GL_VERTEX_SHADER:
                fallback_path = path.join(DEFAULT_SHADER_DIR, DEFAULT_VERTEX)
            elif shader_type == GL_FRAGMENT_SHADER:
                fallback_path = path.join(DEFAULT_SHADER_DIR, DEFAULT_FRAG)

            return MeshShader.compile_shader(fallback_path, shader_type, False)

        glCompileShader(shader_id)
        result = glGetShaderiv(shader_id, GL_COMPILE_STATUS)
        assert result == 1, print(f"Couldn't compile vertex shader\nShader compilation Log:\n{str(glGetShaderInfoLog(shader_id))}")

        lookup[shader_file] = shader_id

        return shader_id

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
            print(glGetProgramInfoLog(self.renderingProgramID))
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

    def set_uniform_sampler2D(self, texture_id: int, uniform_name, texture_slot = 0):
        if texture_id <= 0:
            return

        loc = self.get_uniform_loc(uniform_name)

        glActiveTexture(GL_TEXTURE0 + texture_slot)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glUniform1i(loc, texture_slot)

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

        for idx, l in enumerate(lights):
            self.set_uniform_vec3D(l.origin, f"u_lights[{idx}].position")
            self.set_uniform_float(l.radius, f"u_lights[{idx}].radius")
            self.set_uniform_color(l.color, f"u_lights[{idx}].diffuse")
            self.set_uniform_color(l.color, f"u_lights[{idx}].specular")
            self.set_uniform_color(l.ambient, f"u_lights[{idx}].ambient")

    def set_material_diffuse(self, color):
        self.set_uniform_color(color, "u_material.diffuse")

    def set_diffuse_texture(self, diff_tex_id):
        self.set_uniform_bool((diff_tex_id > 0), "u_material.has_texture")
        self.set_uniform_sampler2D(diff_tex_id, "u_material.diffuse_tex")

    def set_material_specular(self, color):
        self.set_uniform_color(color, "u_material.specular")

    def set_material_ambient(self, color):
        self.set_uniform_color(color, "u_material.ambient")

    def set_unshaded(self, state: bool):
        self.unshaded = state
        self.set_uniform_bool(state, "u_material.unshaded")

    def set_receive_ambient(self, state: bool):
        self.receive_ambient = state
        self.set_uniform_bool(state, "u_material.receive_ambient")

    def set_shininess(self, value: float):
        self.set_uniform_float(value, "u_material.shininess")

    def set_time(self, value: float):
        self.set_uniform_float(value, "u_time")
