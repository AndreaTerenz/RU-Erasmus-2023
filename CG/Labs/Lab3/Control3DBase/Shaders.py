import os.path as path
from abc import ABC, abstractmethod

from OpenGL.GL import *
from OpenGL.error import GLError

DEFAULT_SHADER_DIR = path.join("Control3DBase", "Shader Files")
DEFAULT_VERTEX = "simple3D.vert"
DEFAULT_FRAG = "simple3D.frag"

class Shader3D(ABC):
    def __init__(self, vert_shader_path = None, frag_shader_path = None, shader_folder : str = None, halt_on_error = False):
        if vert_shader_path is None:
            vert_shader_path = DEFAULT_VERTEX
        if frag_shader_path is None:
            frag_shader_path = DEFAULT_FRAG
        if shader_folder is None:
            shader_folder = DEFAULT_SHADER_DIR

        print("Compiling shaders...")
        vert_shader = Shader3D.get_shader(vert_shader_path, GL_VERTEX_SHADER, shader_folder=shader_folder)
        assert vert_shader != -1 or not halt_on_error, f"Couldn't load vertex shader '{vert_shader_path}'"
        print("\tVertex shader ok")

        frag_shader = Shader3D.get_shader(frag_shader_path, GL_FRAGMENT_SHADER, shader_folder=shader_folder)
        assert frag_shader != -1 or not halt_on_error, f"Couldn't load fragment shader '{frag_shader_path}'"
        print("\tFragment shader ok")

        self.renderingProgramID = glCreateProgram()
        glAttachShader(self.renderingProgramID, vert_shader)
        glAttachShader(self.renderingProgramID, frag_shader)
        glLinkProgram(self.renderingProgramID)

        self.modelMatrixLoc = self.get_uniform_loc(self.model_mat_name)
        self.projectionMatrixLoc = self.get_uniform_loc(self.projection_mat_name)
        self.viewMatrixLoc = self.get_uniform_loc(self.view_mat_name)

    def get_projview(self, camera: 'Camera'):
        self.set_projection_matrix(camera.projection_matrix.values)
        self.set_view_matrix(camera.view_matrix.values)

    def set_model_matrix(self, matrix_array):
        glUniformMatrix4fv(self.modelMatrixLoc, 1, True, matrix_array)

    def set_projection_matrix(self, matrix_array):
        glUniformMatrix4fv(self.projectionMatrixLoc, 1, True, matrix_array)

    def set_view_matrix(self, matrix_array):
        glUniformMatrix4fv(self.viewMatrixLoc, 1, True, matrix_array)

    @staticmethod
    def get_shader(shader_file: str, shader_type: int, use_fallback = True, shader_folder: str = ""):
        if not shader_type in [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER]:
            return -1

        shader_id = glCreateShader(shader_type)

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

            return Shader3D.get_shader(fallback_path, shader_type, False)

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

    def get_uniform_loc(self, uniform_name):
        return glGetUniformLocation(self.renderingProgramID, uniform_name)

    def use(self):
        try:
            glUseProgram(self.renderingProgramID)
        except OpenGL.error.GLError:
            print(glGetProgramInfoLog(self.renderingProgramID))
            raise

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

    def __init__(self, halt_on_error = False):
        super().__init__("simple3D.vert", "simple3D.frag", halt_on_error=halt_on_error)

        self.positionLoc = self.enable_attrib_array("a_position")
        self.normalLoc = self.enable_attrib_array("a_normal")

        self.colorLoc = self.get_uniform_loc("u_color")

    def set_position_attribute(self, vertex_array):
        glVertexAttribPointer(self.positionLoc, 3, GL_FLOAT, False, 0, vertex_array)

    def set_normal_attribute(self, vertex_array):
        glVertexAttribPointer(self.normalLoc, 3, GL_FLOAT, False, 0, vertex_array)

    def set_solid_color(self, r, g, b):
        glUniform4f(self.colorLoc, r, g, b, 1.)

    @property
    def model_mat_name(self):
        return "u_model_matrix"

    @property
    def projection_mat_name(self):
        return "u_projection_matrix"

    @property
    def view_mat_name(self):
        return "u_view_matrix"
