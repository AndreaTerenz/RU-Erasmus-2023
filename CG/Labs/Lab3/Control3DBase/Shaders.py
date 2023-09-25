
from OpenGL.GL import *
import os.path as path

class Shader3D:
    def __init__(self, vert_shader_path = "simple3D.vert", frag_shader_path = "simple3D.frag", shader_folder = "Control3DBase/Shader Files"):
        frag_shader = Shader3D.get_shader((path.join(shader_folder, vert_shader_path)), GL_VERTEX_SHADER)
        vert_shader = Shader3D.get_shader((path.join(shader_folder, frag_shader_path)), GL_FRAGMENT_SHADER)

        self.renderingProgramID = glCreateProgram()
        glAttachShader(self.renderingProgramID, vert_shader)
        glAttachShader(self.renderingProgramID, frag_shader)
        glLinkProgram(self.renderingProgramID)

        self.positionLoc = self.enable_attrib_array("a_position")
        self.normalLoc = self.enable_attrib_array("a_normal")

        self.colorLoc = self.get_uniform_loc("u_color")
        self.modelMatrixLoc = self.get_uniform_loc("u_model_matrix")
        self.projectionViewMatrixLoc = self.get_uniform_loc("u_projection_view_matrix")

    @staticmethod
    def get_shader(shader_path: str, shader_type: int):
        if not shader_type in [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER]:
            return -1

        shader_id = glCreateShader(shader_type)

        with open(shader_path) as shader_file:
            glShaderSource(shader_id, shader_file.read())

        glCompileShader(shader_id)
        result = glGetShaderiv(shader_id, GL_COMPILE_STATUS)
        if result != 1:  # shader didn't compile
            print("Couldn't compile vertex shader\nShader compilation Log:\n" + str(glGetShaderInfoLog(shader_id)))
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

    def set_solid_color(self, r, g, b):
        glUniform4f(self.colorLoc, r, g, b, 1.)

    def use(self):
        try:
            glUseProgram(self.renderingProgramID)   
        except OpenGL.error.GLError:
            print(glGetProgramInfoLog(self.renderingProgramID))
            raise

    def set_model_matrix(self, matrix_array):
        glUniformMatrix4fv(self.modelMatrixLoc, 1, True, matrix_array)

    def set_projection_view_matrix(self, matrix_array):
        glUniformMatrix4fv(self.projectionViewMatrixLoc, 1, True, matrix_array)

    def set_position_attribute(self, vertex_array):
        glVertexAttribPointer(self.positionLoc, 3, GL_FLOAT, False, 0, vertex_array)

    def set_normal_attribute(self, vertex_array):
        glVertexAttribPointer(self.normalLoc, 3, GL_FLOAT, False, 0, vertex_array)

