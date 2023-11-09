from abc import abstractmethod, ABC
from typing import Collection

import OpenGL.GLUT
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.error import GLError
from pygame import Color

from oven_engine_3D.utils.geometry import Vector3D, Vector2D
from oven_engine_3D.utils.misc import is_collection

DEFAULT_SHADER_DIR = "shaders"


def add_missing(dict1, dict2):
    dict1.update({key: value for key, value in dict2.items() if not key in dict1})


class BaseShader(ABC):
    compiled_vert_shaders = {}
    compiled_frag_shaders = {}

    POS_ATTRIB_ID = 0
    NORM_ATTRIB_ID = 1
    UV_ATTRIB_ID = 2

    LAST_USED = []

    class ShaderAttribute:
        def __init__(self, name: str, loc: int, elem_count: int, dtype, attrib_type: int):
            self.name = name
            self.loc = loc
            self.elem_count = elem_count
            self.data_type = dtype
            self.attrib_type = attrib_type

        @property
        def elem_size(self):
            return sizeof(self.data_type)

        @property
        def attrib_size(self):
            return self.elem_count * self.elem_size

    def __init__(self, vert_shader_path, frag_shader_path, transparent=False, **kwargs):
        self.vert_shader_path = vert_shader_path
        self.frag_shader_path = frag_shader_path
        self.renderingProgramID = BaseShader.get_shader_program(self.vert_shader_path, self.frag_shader_path)

        self.transparent = transparent

        self.uniform_locations = {}
        self.attributes = {}
        self.total_attrib_size = 0
        self.textures = {}

        def_params = self.__class__.get_default_params()

        self.material_params = {k: v for k, v in kwargs.items() if k in def_params}
        add_missing(self.material_params, def_params)

    def __enter__(self):
        BaseShader.LAST_USED.append(glGetIntegerv(GL_CURRENT_PROGRAM))
        self.use()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        to_restore = 0
        if len(BaseShader.LAST_USED) > 0:
            to_restore = BaseShader.LAST_USED.pop()

        glUseProgram(to_restore)

    def add_attribute(self, name, elem_count, dtype, atype):
        if atype in self.attributes:
            return

        loc = self.enable_attrib_array(name)
        attr = BaseShader.ShaderAttribute(name, loc, elem_count, dtype, atype)

        self.attributes[atype] = attr
        self.total_attrib_size += attr.attrib_size

        return loc

    @property
    def compiled(self):
        return self.renderingProgramID > 0

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

        assert progID != 0, "Failed to create program"

        glAttachShader(progID, vert_shader)
        glAttachShader(progID, frag_shader)
        glLinkProgram(progID)

        assert glGetProgramiv(progID, GL_LINK_STATUS) == 1, "Failed to link"

        return progID

    @staticmethod
    def compile_shader_file(shader_file: str, shader_type: int):
        assert shader_type in [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER], "Invalid shader type"

        shader_path = shader_file
        """if shader_folder != "":
            shader_path = path.join(shader_folder, shader_file)"""

        print(f"\tCompiling shader file {shader_path}...", end="")

        lookup: dict = BaseShader.compiled_vert_shaders if shader_type == GL_VERTEX_SHADER else BaseShader.compiled_frag_shaders

        if shader_path in lookup:
            print("done (already compiled)")
            return lookup[shader_path]

        shader_id = glCreateShader(shader_type)

        assert shader_id != 0, "Couldn't create shader"

        try:
            with open(shader_path) as shader_file:
                glShaderSource(shader_id, shader_file.read())
        except FileNotFoundError:
            assert False, f"Shader file '{shader_file}' not found"

        glCompileShader(shader_id)
        result = glGetShaderiv(shader_id, GL_COMPILE_STATUS)
        assert result == 1, f"Couldn't compile shader {str(shader_file)} \nShader compilation Log:\n{str(glGetShaderInfoLog(shader_id))}"

        lookup[shader_path] = shader_id

        print("done")

        return shader_id

    def link_attrib_vbo(self, vbo, ordering):
        glBindBuffer(GL_ARRAY_BUFFER, vbo)

        offset_size = 0
        for atype in ordering:
            a = self.attributes[atype]
            glVertexAttribPointer(a.loc, a.elem_count, GL_FLOAT, False, self.total_attrib_size,
                                  ctypes.c_void_p(offset_size))
            offset_size += a.attrib_size

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

    @abstractmethod
    def _ondraw(self, *args, **kwargs):
        pass

    def draw(self, *args, **kwargs):
        with self:
            self.toggle_textures()
            self._ondraw(*args, **kwargs)
            self.toggle_textures(bind=False)

    def get_uniform_loc(self, uniform_name):
        if uniform_name in self.uniform_locations:
            return self.uniform_locations[uniform_name]

        output = glGetUniformLocation(self.renderingProgramID, uniform_name)

        if output != -1:
            self.uniform_locations[uniform_name] = output

        return output

    def get_uniform_int(self, uniform_name, count=1):
        return self.get_uniform_value(uniform_name, ctypes.c_int, count)

    def get_uniform_float(self, uniform_name, count=1):
        return self.get_uniform_value(uniform_name, ctypes.c_float, count)

    def get_uniform_color(self, uniform_name):
        tmp = self.get_uniform_float(uniform_name, 4)
        return Color(*(int(v * 255.) for v in tmp))

    def get_uniform_value(self, uniform_name, datatype, count=1):
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

    def set_uniform_vec2D(self, vector: Vector2D, uniform_name):
        loc = self.get_uniform_loc(uniform_name)

        glUniform2f(loc, *vector)

    def set_uniform_float(self, value: [float | Collection], uniform_name):
        count = 1 if not is_collection(value) else len(value)

        loc = self.get_uniform_loc(uniform_name)
        glUniform1fv(loc, count, value)

    def set_uniform_int(self, value: [int | Collection], uniform_name):
        if not is_collection(value):
            value = [value]

        count = len(value)

        loc = self.get_uniform_loc(uniform_name)
        glUniform1iv(loc, count, value)

    def set_uniform_bool(self, value: [bool | Collection], uniform_name):
        if not is_collection(value):
            value = [value]

        value = [int(v) for v in value]
        self.set_uniform_int(value, uniform_name)

    def set_texture(self, texture_slot, texture_id, uniform_name, tex_flag_uniform_name="", texture_type=GL_TEXTURE_2D):
        self.textures[texture_slot] = {
            "id": texture_id,
            "type": texture_type
        }
        self.set_uniform_sampler2D(texture_slot, uniform_name)

        if tex_flag_uniform_name != "":
            self.set_uniform_bool(texture_id > 0, tex_flag_uniform_name)

    def set_uniform_sampler2D(self, texture_slot, uniform_name):
        loc = self.get_uniform_loc(uniform_name)
        glUniform1i(loc, texture_slot)

    def toggle_textures(self, bind=True):
        for idx, tex_data in self.textures.items():
            if tex_data["id"] <= 0:
                continue

            glActiveTexture(GL_TEXTURE0 + idx)
            glBindTexture(tex_data["type"], tex_data["id"] if bind else 0)

