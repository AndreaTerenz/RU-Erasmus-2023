import os.path as path
from itertools import chain
from typing import Collection

import OpenGL.GLUT
import numpy as np
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

    def __init__(self, positions=None, normals=None, uvs=None,
                 vert_shader_path = DEFAULT_VERTEX, frag_shader_path = DEFAULT_FRAG, shader_folder : str = DEFAULT_SHADER_DIR,
                 diffuse_color=Color("white"), specular_color=(.2, .2, .2), ambient_color=(.1, .1, .1),
                 shininess=30., unshaded=False, receive_ambient=True, diffuse_texture = "", vbo=0):

        assert (positions is None or normals is None) != (vbo == 0), "Must provide either positions and normals or a vbo"

        self.diff_tex_id = -1
        if diffuse_texture != "":
            self.diff_tex_id = TexturesManager.load_texture(diffuse_texture, filtering=GL_LINEAR)

        print("Compiling shaders...")

        self.vert_path = vert_shader_path
        self.frag_path = frag_shader_path
        self.src_dir = shader_folder

        self.renderingProgramID = self.get_shader_program()

        self.uniform_locations = {}
        self.uniform_values = {}

        self.positionLoc = self.enable_attrib_array("a_position")
        self.normalLoc = self.enable_attrib_array("a_normal")
        self.uvLoc = self.enable_attrib_array("a_uv")
        self.uvs = uvs

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
        self.set_material_ambient(ambient_color)
        self.set_diffuse_texture(self.diff_tex_id)
        self.set_unshaded(unshaded)
        self.set_receive_ambient(receive_ambient)
        self.set_shininess(shininess)

        test = [Vector3D.UP, Vector3D.DOWN, Vector3D.LEFT, Vector3D.RIGHT]
        self.set_uniform_vec3Ds(test, "u_many_pos", homogenous=False)

    def get_shader_program(self):
        vert_shader = MeshShader.compile_shader(self.vert_path, GL_VERTEX_SHADER, shader_folder=self.src_dir)
        frag_shader = MeshShader.compile_shader(self.frag_path, GL_FRAGMENT_SHADER, shader_folder=self.src_dir)

        progID = glCreateProgram()

        assert progID != 0, print("Couldn't create program")
        glAttachShader(progID, vert_shader)
        glAttachShader(progID, frag_shader)
        glLinkProgram(progID)
        assert glGetProgramiv(progID, GL_LINK_STATUS) == 1, print("Couldn't link program")

        return progID

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

            if not use_fallback:
                return -1

            print("Using fallback shader")
            fallback_path = ""
            if shader_type == GL_VERTEX_SHADER:
                fallback_path = path.join(DEFAULT_SHADER_DIR, DEFAULT_VERTEX)
            elif shader_type == GL_FRAGMENT_SHADER:
                fallback_path = path.join(DEFAULT_SHADER_DIR, DEFAULT_FRAG)

            return MeshShader.compile_shader(fallback_path, shader_type, False)

        glCompileShader(shader_id)
        result = glGetShaderiv(shader_id, GL_COMPILE_STATUS)
        if result != 1:  # shader didn't compile
            print(f"Couldn't compile vertex shader\nShader compilation Log:\n{str(glGetShaderInfoLog(shader_id))}")
            return -1

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
            self._on_use()
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
        color = MeshShader.__get_color(color)

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
        self.set_projection_matrix(camera.projection_matrix)
        self.set_view_matrix(camera.view_matrix)
        self.set_uniform_vec3D(camera.view_matrix.eye, "u_camera_position")

    def set_model_matrix(self, matrix):
        self.set_uniform_matrix(matrix, self.model_mat_name)

    def set_projection_matrix(self, matrix):
        self.set_uniform_matrix(matrix, self.projection_mat_name)

    def set_view_matrix(self, matrix):
        self.set_uniform_matrix(matrix, self.view_mat_name)

    def _on_use(self):
        pass

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

        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def set_uv_attribute(self):
        if self.uvs is None:
            return

        glVertexAttribPointer(self.uvLoc, 2, GL_FLOAT, False, 0, self.uvs)

    def bind_vbo(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.pos_vbo)

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

    @property
    def model_mat_name(self):
        return "u_model_matrix"

    @property
    def projection_mat_name(self):
        return "u_projection_matrix"

    @property
    def view_mat_name(self):
        return "u_view_matrix"
