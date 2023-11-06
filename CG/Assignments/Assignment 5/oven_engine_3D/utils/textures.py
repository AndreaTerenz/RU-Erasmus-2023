import os

import pygame as pg
import pygame.image as img
from OpenGL.GL import *
from OpenGL.constant import IntConstant

from oven_engine_3D.utils.geometry import Vector2D

MISSING_TEXTURE = "res/textures/DB_missing_texture.png"

class TexturesManager:
    textures = {}
    cubemaps = {}

    @staticmethod
    def load_texture(path, filtering=GL_NEAREST, clamping=GL_REPEAT, color_format=GL_RGBA, pixel_format=GL_RGBA):
        print(f"Loading texture from '{path}'...", end="")

        if path in TexturesManager.textures.keys():
            print("done (texture already loaded)")
            return TexturesManager.textures[path]

        if not os.path.exists(path):
            print(f"Failed ('{path}' does not exist)")
            path = MISSING_TEXTURE

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

        glBindTexture(GL_TEXTURE_2D, 0)

        textID = int(textID)

        if textID != -1:
            TexturesManager.textures[path] = textID

        print("done")

        return textID

    @staticmethod
    def load_cubemap(px : str = MISSING_TEXTURE, nx : str = MISSING_TEXTURE,
                     py : str = MISSING_TEXTURE, ny : str = MISSING_TEXTURE,
                     pz : str = MISSING_TEXTURE, nz : str = MISSING_TEXTURE,
                     folder : str = None):
        print(f"Creating cubemap...")

        paths = [px, nx, py, ny, pz, nz]
        if folder is not None:
            paths = [os.path.join(folder, p) for p in paths]

        cubemap_total_path = "#".join(paths)

        if cubemap_total_path in TexturesManager.cubemaps.keys():
            print("done (cubemap already loaded)")
            return TexturesManager.cubemaps[cubemap_total_path]

        all_found = True
        surfaces = [None] * 6

        for idx in range(len(paths)):
            print(f"\tLoading face {idx} from {paths[idx]}...", end="")
            p = paths[idx]

            found = os.path.exists(p)
            if not found:
                print(f"failed (file does not exist)")
                p = MISSING_TEXTURE
                all_found = False
            else:
                print("done") # I know, it actually happens next line, dont worry about it....

            surfaces[idx] = img.load(p)

        faces_data = [""] * 6
        faces_size = [Vector2D.ZERO] * 6

        for idx, s in enumerate(surfaces):
            if not all_found:
                # If we haven't found all faces, then at least one is the missing texture,
                # which is 512x512, so we need to scale all the faces to that size
                s = pg.transform.scale(s, (512, 512))

            faces_data[idx] = (img.tostring(s, "RGB", False))
            faces_size[idx] = Vector2D(s.get_size())

        cmapID = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, cmapID)

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glTexParameterf(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

        for idx in range(6):
            w, h = faces_size[idx]
            glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + idx, 0, GL_RGB, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, faces_data[idx])

        glBindTexture(GL_TEXTURE_CUBE_MAP, 0)

        cmapID = int(cmapID)

        if cmapID != -1:
            TexturesManager.cubemaps[cubemap_total_path] = cmapID

        if all_found:
            print("done")
        else:
            print("done (failed to load some faces)")

        return cmapID

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