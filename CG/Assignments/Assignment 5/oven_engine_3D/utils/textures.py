import os

import cv2
import numpy as np
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
        if type(path) is int:
            return path

        if path == "":
            return 0

        print(f"Loading texture from '{path}'...", end="")

        if path in TexturesManager.textures.keys():
            print("done (texture already loaded)")
            return TexturesManager.textures[path]

        if not os.path.exists(path):
            print(f"Failed ('{path}' does not exist)")
            path = MISSING_TEXTURE

        surf = img.load(path)
        form = "RGBA" if pixel_format == GL_RGBA else "RGB"
        tex_str = img.tostring(surf, form, True)
        size = Vector2D(surf.get_size())

        if not (filtering in [GL_NEAREST, GL_LINEAR]):
            filtering = GL_NEAREST

        textID = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, textID)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filtering)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filtering)

        if type(clamping) is IntConstant:
            clamping = (clamping, clamping)

        for idx in [0,1]:
            if clamping[idx] in [GL_CLAMP_TO_EDGE, GL_MIRRORED_REPEAT, GL_REPEAT, GL_CLAMP_TO_BORDER]:
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S + idx, clamping[idx])

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
    def generate_cubemap_paths(folder : str = "", ext : str = "", **kwargs):
        paths = {
            "px": "",
            "nx": "",
            "py": "",
            "ny": "",
            "pz": "",
            "nz": ""
        }
        for k, v in paths.items():
            default = f"{k}.{ext}"
            if folder != "":
                default = os.path.join(folder, default)

            paths[k] = kwargs.get(k, default)

        return list(paths.values())

    @staticmethod
    def load_cubemap(paths, compute_dom_color = False):
        print(f"Creating cubemap...")

        cubemap_total_path = "#".join(paths)

        if cubemap_total_path in TexturesManager.cubemaps.keys():
            print("done (cubemap already loaded)")
            return TexturesManager.cubemaps[cubemap_total_path]

        all_found = True
        surfaces = [None] * 6

        for idx, p in enumerate(paths):
            print(f"\tLoading face {idx} from {p}...", end="")

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

        for idx in range(len(surfaces)):
            s = surfaces[idx]
            if not all_found:
                # If we haven't found all faces, then at least one is the missing texture,
                # which is 512x512, so we need to scale all the faces to that size
                s = pg.transform.scale(s, (512, 512))

            faces_data[idx] = img.tostring(s, "RGB", False)
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

        if not compute_dom_color:
            return cmapID

        surfaces.pop(GL_TEXTURE_CUBE_MAP_NEGATIVE_Y - GL_TEXTURE_CUBE_MAP_POSITIVE_X)
        col = TexturesManager.compute_sky_color(surfaces)

        return cmapID, col

    @staticmethod
    def compute_sky_color(surfs):
        concat_data = None

        for s in surfs:
            scaling = .1
            size = Vector2D(s.get_size())

            if size[0] >= 4096:
                scaling = .125
            elif size[0] >= 2048:
                scaling = .25
            elif size[0] >= 256:
                scaling = .5

            s = pg.transform.scale(s, tuple(size * scaling))
            data = pg.surfarray.array3d(s)

            if concat_data is None:
                concat_data = data
            else:
                concat_data = np.concatenate((concat_data, data), axis=1)

        pixels = np.float32(concat_data.reshape(-1, 3))

        n_colors = 2
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, .1)
        flags = cv2.KMEANS_RANDOM_CENTERS

        _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
        _, counts = np.unique(labels, return_counts=True)

        dominant = [int(v) for v in palette[np.argmax(counts)]]
        return pg.Color(*dominant)

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