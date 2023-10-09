import os.path as path
from abc import ABC, abstractmethod

import numpy as np
from OpenGL.GL import *
from OpenGL.error import GLError
from pygame import Color

from oven_engine_3D.matrices import Matrix
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

class Shader3D(ABC):
    compiled_vert_shaders = {}
    compile_frag_shaders = {}

    def __init__(self, vert_shader_path = None, frag_shader_path = None, shader_folder : str = None, halt_on_error = False):
        if vert_shader_path is None:
            vert_shader_path = DEFAULT_VERTEX
        if frag_shader_path is None:
            frag_shader_path = DEFAULT_FRAG
        if shader_folder is None:
            shader_folder = DEFAULT_SHADER_DIR

        print("Compiling shaders...")

        if vert_shader_path in Shader3D.compiled_vert_shaders:
            vert_shader = Shader3D.compiled_vert_shaders[vert_shader_path]
            print("\tVertex shader already compiled")
        else:
            vert_shader = Shader3D.compile_shader(vert_shader_path, GL_VERTEX_SHADER, shader_folder=shader_folder)

            assert vert_shader != -1 or not halt_on_error, f"Couldn't load vertex shader '{vert_shader_path}'"
            print(f"\tVertex shader {'ok' if vert_shader != -1 else 'failed'}")
            Shader3D.compiled_vert_shaders[vert_shader_path] = vert_shader

        if frag_shader_path in Shader3D.compile_frag_shaders:
            frag_shader = Shader3D.compile_frag_shaders[frag_shader_path]
            print("\tFrag shader already compiled")
        else:
            frag_shader = Shader3D.compile_shader(frag_shader_path, GL_FRAGMENT_SHADER, shader_folder=shader_folder)

            assert frag_shader != -1 or not halt_on_error, f"Couldn't load fragment shader '{frag_shader_path}'"
            print(f"\tFragment shader {'ok' if frag_shader != -1 else 'failed'}")
            Shader3D.compile_frag_shaders[frag_shader_path] = frag_shader

        self.renderingProgramID = glCreateProgram()

        assert self.renderingProgramID != 0, print("Couldn't create program")

        glAttachShader(self.renderingProgramID, vert_shader)
        glAttachShader(self.renderingProgramID, frag_shader)
        glLinkProgram(self.renderingProgramID)

        assert glGetProgramiv(self.renderingProgramID, GL_LINK_STATUS) == 1, print("Couldn't link program")

        self.uniform_locations = {}
        self.uniform_values = {}

    @staticmethod
    def compile_shader(shader_file: str, shader_type: int, use_fallback = True, shader_folder: str = ""):
        if not shader_type in [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER]:
            return -1

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

            if not use_fallback:
                return -1

            print("Using fallback shader")
            fallback_path = ""
            if shader_type == GL_VERTEX_SHADER:
                fallback_path = path.join(DEFAULT_SHADER_DIR, DEFAULT_VERTEX)
            elif shader_type == GL_FRAGMENT_SHADER:
                fallback_path = path.join(DEFAULT_SHADER_DIR, DEFAULT_FRAG)

            return Shader3D.compile_shader(fallback_path, shader_type, False)

        glCompileShader(shader_id)
        result = glGetShaderiv(shader_id, GL_COMPILE_STATUS)
        if result != 1:  # shader didn't compile
            print(f"Couldn't compile vertex shader\nShader compilation Log:\n{str(glGetShaderInfoLog(shader_id))}")
            return -1

        return shader_id

    def enable_attrib_array(self, attrib_name):
        attrib_loc = self.get_attrib_loc(attrib_name)
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

    def get_uniform_int(self, uniform_name, count):
        return self.get_uniform_value(uniform_name, count, ctypes.c_int)

    def get_uniform_float(self, uniform_name, count):
        return self.get_uniform_value(uniform_name, count, ctypes.c_float)

    def get_uniform_value(self, uniform_name, count, datatype):
        loc = self.get_uniform_loc(uniform_name)
        output = (datatype * count)()

        if loc == -1:
            return None

        glGetUniformfv(self.renderingProgramID, loc, output)

        return list(output) if count > 1 else output[0]

    #@uniform_updater
    def set_uniform_color(self, color, uniform_name):
        loc = self.get_uniform_loc(uniform_name)

        if type(color) is Color:
            color = color.normalize()
        elif type(color) in [int, float]:
            color = color, color, color, 1.

        if len(color) == 3:
            color = (*color, 1.)

        glUniform4f(loc, *color)

    #@uniform_updater
    def set_uniform_matrix(self, matrix: Matrix, uniform_name):
        loc = self.get_uniform_loc(uniform_name)
        glUniformMatrix4fv(loc, 1, True, matrix.values)

    #@uniform_updater
    def set_uniform_vec3D(self, vector: Vector3D, uniform_name, homogenous=True, w=1.0):
        loc = self.get_uniform_loc(uniform_name)

        if homogenous:
            glUniform4f(loc, *vector, w)
        else:
            glUniform3f(loc, *vector)

    #@uniform_updater
    def set_uniform_float(self, value: float, uniform_name):
        loc = self.get_uniform_loc(uniform_name)
        glUniform1f(loc, value)

    #@uniform_updater
    def set_uniform_int(self, value: int, uniform_name):
        loc = self.get_uniform_loc(uniform_name)
        glUniform1i(loc, value)

    def set_uniform_bool(self, value: bool, uniform_name):
        self.set_uniform_int(int(value), uniform_name)

    def set_camera_uniforms(self, camera: 'Camera'):
        self.set_projection_matrix(camera.projection_matrix)
        self.set_view_matrix(camera.view_matrix)

    def set_model_matrix(self, matrix):
        self.set_uniform_matrix(matrix, self.model_mat_name)

    def set_projection_matrix(self, matrix):
        self.set_uniform_matrix(matrix, self.projection_mat_name)

    def set_view_matrix(self, matrix):
        self.set_uniform_matrix(matrix, self.view_mat_name)

    @property
    @abstractmethod
    def model_mat_name(self):
        return ""

    @property
    @abstractmethod
    def projection_mat_name(self):
        return ""

    @property
    @abstractmethod
    def view_mat_name(self):
        return ""

class MeshShader(Shader3D):

    def __init__(self, positions, normals,
                 diffuse_color=(1., 1., 1.), specular_color=(.2, .2, .2), shininess=30.,
                 unshaded=False, receive_ambient=True, halt_on_error = False):
        super().__init__("simple3D.vert", "simple3D.frag", halt_on_error=halt_on_error)

        self.current_pos = None
        self.current_normals = None

        self.positionLoc = self.enable_attrib_array("a_position")
        self.normalLoc = self.enable_attrib_array("a_normal")

        self.unshaded = unshaded
        self.receive_ambient = receive_ambient

        self.use()
        self.set_position_attribute(positions)
        self.set_normal_attribute(normals)
        self.set_material_diffuse(diffuse_color)
        self.set_material_specular(specular_color)
        self.set_unshaded(unshaded)
        self.set_receive_ambient(receive_ambient)
        self.set_shininess(shininess)

    def set_position_attribute(self, vertex_array):
        if self.current_pos is not None and np.array_equal(vertex_array, self.current_pos):
            pass #return

        self.current_pos = vertex_array
        glVertexAttribPointer(self.positionLoc, 3, GL_FLOAT, False, 0, vertex_array)

    def set_normal_attribute(self, vertex_array):
        if self.current_normals is not None and np.array_equal(vertex_array, self.current_normals):
            pass #return

        self.current_normals = vertex_array
        glVertexAttribPointer(self.normalLoc, 3, GL_FLOAT, False, 0, vertex_array)

    def set_camera_uniforms(self, camera: 'Camera'):
        super().set_camera_uniforms(camera)
        self.set_uniform_vec3D(camera.view_matrix.eye, "u_camera_position")

    def set_light_uniforms(self, light: "Light"):
        self.set_uniform_vec3D(light.origin, "u_light_position")
        self.set_uniform_color(light.color, "u_light_diffuse")
        self.set_uniform_color(light.color, "u_light_specular")

    def set_camera_position(self, pos: Vector3D):
        self.set_uniform_vec3D(pos, "u_camera_position")

    def set_light_position(self, pos: Vector3D):
        self.set_uniform_vec3D(pos, "u_light_position")

    def set_light_diffuse(self, color):
        self.set_uniform_color(color, "u_light_diffuse")

    def set_light_specular(self, color):
        self.set_uniform_color(color, "u_light_specular")

    def set_material_diffuse(self, color):
        self.set_uniform_color(color, "u_material_diffuse")

    def set_material_specular(self, color):
        self.set_uniform_color(color, "u_material_specular")

    def set_ambient(self, color):
        self.set_uniform_color(color, "u_ambient")

    def set_unshaded(self, state: bool):
        self.unshaded = state
        self.set_uniform_bool(state, "unshaded")

    def set_receive_ambient(self, state: bool):
        self.receive_ambient = state
        self.set_uniform_bool(state, "receive_ambient")

    def set_shininess(self, value: float):
        self.set_uniform_float(value, "u_shininess")

    def set_time(self, value: float):
        self.set_uniform_float(value, "u_time")

    @property
    def model_mat_name(self):
        return "u_model_matrix"

    @property
    def projection_mat_name(self):
        return "u_projection_matrix"

    @property
    def view_mat_name(self):
        return "u_view_matrix"
