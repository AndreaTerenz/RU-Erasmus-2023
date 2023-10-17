import os.path as path
from abc import ABC, abstractmethod
from itertools import chain
from typing import Collection

import OpenGL.GLUT
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
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

        self.vert_path = vert_shader_path
        self.frag_path = frag_shader_path
        self.src_dir = shader_folder

        if self.vert_path in Shader3D.compiled_vert_shaders:
            vert_shader = Shader3D.compiled_vert_shaders[self.vert_path]
            print("\tVertex shader already compiled")
        else:
            vert_shader = Shader3D.compile_shader(self.vert_path, GL_VERTEX_SHADER, shader_folder=self.src_dir)

            assert vert_shader != -1 or not halt_on_error, f"Couldn't load vertex shader '{self.vert_path}'"
            print(f"\tVertex shader {'ok' if vert_shader != -1 else 'failed'}")
            Shader3D.compiled_vert_shaders[self.vert_path] = vert_shader

        if self.frag_path in Shader3D.compile_frag_shaders:
            frag_shader = Shader3D.compile_frag_shaders[self.frag_path]
            print("\tFrag shader already compiled")
        else:
            frag_shader = Shader3D.compile_shader(self.frag_path, GL_FRAGMENT_SHADER, shader_folder=self.src_dir)

            assert frag_shader != -1 or not halt_on_error, f"Couldn't load fragment shader '{self.frag_path}'"
            print(f"\tFragment shader {'ok' if frag_shader != -1 else 'failed'}")
            Shader3D.compile_frag_shaders[self.frag_path] = frag_shader

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

    def get_uniform_int(self, uniform_name, count = 1):
        return self.get_uniform_value(uniform_name, ctypes.c_int, count)

    def get_uniform_float(self, uniform_name, count = 1):
        return self.get_uniform_value(uniform_name, ctypes.c_float, count)

    def get_uniform_value(self, uniform_name, datatype, count = 1):
        loc = self.get_uniform_loc(uniform_name)
        output = (datatype * count)()

        if loc == -1:
            return None

        glGetUniformfv(self.renderingProgramID, loc, output)

        return list(output) if count > 1 else output[0]

    #@uniform_updater
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

    #@uniform_updater
    def set_uniform_color(self, color, uniform_name):
        loc = self.get_uniform_loc(uniform_name)
        color = Shader3D.__get_color(color)

        glUniform4f(loc, *color)

    def set_uniform_colors(self, colors: Collection, uniform_name, count = 1):
        assert len(colors) >= count, "Tried to set too few values for uniform!"

        for color in colors:
            self.set_uniform_color(color, uniform_name)

    #@uniform_updater
    def set_uniform_vec3D(self, vector: Vector3D, uniform_name, homogenous=True, w=1.0):
        loc = self.get_uniform_loc(uniform_name)

        if homogenous:
            glUniform4f(loc, *vector, w)
        else:
            glUniform3f(loc, *vector)

    def set_uniform_vec3Ds(self, vectors: Collection[Vector3D], uniform_name, homogenous=True, w=1.0):
        for vector in vectors:
            self.set_uniform_vec3D(vector, uniform_name, homogenous, w)

    #@uniform_updater
    def set_uniform_float(self, value: [float|Collection], uniform_name):
        count = 1 if isinstance(value, float) else len(value)

        loc = self.get_uniform_loc(uniform_name)
        glUniform1fv(loc, count, value)

    #@uniform_updater
    def set_uniform_int(self, value: [int|Collection], uniform_name):
        count = 1 if isinstance(value, int) else len(value)

        loc = self.get_uniform_loc(uniform_name)
        glUniform1iv(loc, count, value)

    def set_uniform_bool(self, value: [bool|Collection], uniform_name):
        if isinstance(value, bool):
            value = [value]

        value = [int(v) for v in value]
        self.set_uniform_int(value, uniform_name)

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

    def __init__(self, positions=None, normals=None,
                 diffuse_color=(1., 1., 1.), specular_color=(.2, .2, .2), shininess=30.,
                 unshaded=False, receive_ambient=True, halt_on_error = False, vbo=0):
        super().__init__("simple3D.vert", "simple3D.frag", halt_on_error=halt_on_error)

        assert (positions is None or normals is None) != (vbo == 0), "Must provide either positions and normals or a vbo"

        self.positionLoc = self.enable_attrib_array("a_position")
        self.normalLoc = self.enable_attrib_array("a_normal")

        self.pos_vbo = vbo

        if self.pos_vbo == 0:
            tmp = [(*p,*n) for p,n in zip(positions, normals)]
            tmp = list(chain.from_iterable(tmp))

            self.pos_vbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, self.pos_vbo)
            glBufferData(GL_ARRAY_BUFFER, np.array(tmp, dtype="float32"), GL_STATIC_DRAW)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

        self.unshaded = unshaded
        self.receive_ambient = receive_ambient

        self.use()
        self.set_material_diffuse(diffuse_color)
        self.set_material_specular(specular_color)
        self.set_unshaded(unshaded)
        self.set_receive_ambient(receive_ambient)
        self.set_shininess(shininess)

        test = [Vector3D.UP, Vector3D.DOWN, Vector3D.LEFT, Vector3D.RIGHT]
        self.set_uniform_vec3Ds(test, "u_many_pos", homogenous=False)

    def set_attribute_buffers(self):
        values_per_attrib = 3
        attribs_count = 6
        attrib_size = sizeof(GLfloat)

        def offset_to_size(offset, values = values_per_attrib, size = attrib_size):
            return ctypes.c_void_p(offset * values * size)

        glBindBuffer(GL_ARRAY_BUFFER, self.pos_vbo)

        pos_offset_size = offset_to_size(0)
        glVertexAttribPointer(self.positionLoc, values_per_attrib, GL_FLOAT, False, attribs_count * attrib_size, pos_offset_size)

        norm_offset_size = offset_to_size(1)
        glVertexAttribPointer(self.normalLoc, values_per_attrib, GL_FLOAT, False, attribs_count * attrib_size, norm_offset_size)

        # Pointless to unbind because this function will basically always
        # precede a draw call where the vbo would get bound again anyway
        #glBindBuffer(GL_ARRAY_BUFFER, 0)

    def set_camera_uniforms(self, camera: 'Camera'):
        super().set_camera_uniforms(camera)
        self.set_uniform_vec3D(camera.view_matrix.eye, "u_camera_position")

    def set_light_uniforms(self, lights: ["Light"|Collection]):
        if not isinstance(lights, Collection):
            lights = [lights]

        for idx, l in enumerate(lights):
            self.set_uniform_vec3D(l.origin, f"u_light_position[{idx}]")
            self.set_uniform_float(l.radius, f"u_light_radius[{idx}]")
            self.set_uniform_color(l.color, f"u_light_diffuse[{idx}]")
            self.set_uniform_color(l.color, f"u_light_specular[{idx}]")

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

    """def set_time(self, value: float):
        self.set_uniform_float(value, "u_time")
    """
    @property
    def model_mat_name(self):
        return "u_model_matrix"

    @property
    def projection_mat_name(self):
        return "u_projection_matrix"

    @property
    def view_mat_name(self):
        return "u_view_matrix"
