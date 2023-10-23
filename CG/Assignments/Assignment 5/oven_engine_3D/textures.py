from OpenGL.GL import *
from OpenGL.constant import IntConstant
from oven_engine_3D.utils.geometry import Vector2D
from PIL import Image

import numpy as np

class TexturesManager:
    def __init__(self):
        self.textures = {}

    def load_texture(self, path, filtering=GL_NEAREST, clamping=GL_REPEAT, color_format=GL_RGBA8, pixel_format=GL_RGBA):
        print(f"Loading texture from '{path}'...", end="")

        if path in self.textures.keys():
            print("done (texture already loaded)")
            return self.textures[path]

        try:
            text = Image.open(path)
        except IOError:
            print(f"Failed to load texture '{path}'")
            return -1

        if not (filtering in [GL_NEAREST, GL_LINEAR]):
            filtering = GL_NEAREST

        textData = np.array(list(text.getdata()))
        text.close()

        textID = glGenTextures(1)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glBindTexture(GL_TEXTURE_2D, textID)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filtering)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filtering)

        if type(clamping) is IntConstant:
            clamping = (clamping, clamping)

        if clamping[0] in [GL_CLAMP_TO_EDGE, GL_MIRRORED_REPEAT, GL_REPEAT, GL_CLAMP_TO_BORDER]:
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, clamping[0])
        if clamping[1] in [GL_CLAMP_TO_EDGE, GL_MIRRORED_REPEAT, GL_REPEAT, GL_CLAMP_TO_BORDER]:
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, clamping[1])

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)

        glTexImage2D(GL_TEXTURE_2D, 0, color_format, text.width, text.height, 0, pixel_format, GL_UNSIGNED_BYTE, textData)

        textID = int(textID)

        if textID != -1:
            self.textures[path] = textID

        return textID

    def is_texture_valid(self, tex):
        return tex in self.textures.values()

    def unload_texture(self, textureID: int):
        if not self.is_texture_valid(textureID):
            print(f"Invalid texture ID {textureID}")
            return False

        glDeleteTextures(textureID, 1)
        return True