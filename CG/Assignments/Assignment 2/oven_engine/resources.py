from oven_engine.utils.gl import *

class TexturesManager:
    def __init__(self):
        self.textures = {}

    def load_texture(self, path, filtering=GL_NEAREST, clamping=GL_REPEAT):
        print(f"Loading texture from '{path}'...", end="")

        if path in self.textures.keys():
            print("done (texture already loaded)")
            return self.textures[path]

        tex = load_texture(path, filtering=filtering, clamping=clamping)

        if tex != -1:
            self.textures[path] = tex

        return tex

    def is_texture_valid(self, tex):
        return tex in self.textures.values()