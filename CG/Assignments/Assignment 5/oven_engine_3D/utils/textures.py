import os

from OpenGL.GL import *
from OpenGL.constant import IntConstant
from oven_engine_3D.utils.geometry import Vector2D
from PIL import Image
import pygame.image as img

import numpy as np

class TexturesManager:
    textures = {}

    @staticmethod
    def load_texture(path, filtering=GL_NEAREST, clamping=GL_REPEAT, color_format=GL_RGBA, pixel_format=GL_RGBA):
        print(f"Loading texture from '{path}'...", end="")

        if path in TexturesManager.textures.keys():
            print("done (texture already loaded)")
            return TexturesManager.textures[path]

        if not os.path.exists(path):
            print(f"Failed ('{path}' does not exist)")
            path = "res/textures/DB_missing_texture.png"

        surf = img.load(path)
        tex_str = img.tostring(surf, "RGBA", 1)
        size = Vector2D(surf.get_size())

        if not (filtering in [GL_NEAREST, GL_LINEAR]):
            filtering = GL_NEAREST

        textID = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, textID)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filtering)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filtering)

        if type(clamping) is IntConstant:
            clamping = (clamping, clamping)

        if clamping[0] in [GL_CLAMP_TO_EDGE, GL_MIRRORED_REPEAT, GL_REPEAT, GL_CLAMP_TO_BORDER]:
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, clamping[0])
        if clamping[1] in [GL_CLAMP_TO_EDGE, GL_MIRRORED_REPEAT, GL_REPEAT, GL_CLAMP_TO_BORDER]:
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, clamping[1])

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)

        glTexImage2D(GL_TEXTURE_2D, 0, color_format, size.x, size.y, 0, pixel_format, GL_UNSIGNED_BYTE, tex_str)

        textID = int(textID)

        if textID != -1:
            TexturesManager.textures[path] = textID

        print("done")

        return textID

    @staticmethod
    def is_texture_valid(tex):
        return tex in TexturesManager.textures.values()

    @staticmethod
    def unload_texture(textureID: int):
        if not TexturesManager.is_texture_valid(textureID):
            print(f"Invalid texture ID {textureID}")
            return False

        glDeleteTextures(textureID, 1)
        return True