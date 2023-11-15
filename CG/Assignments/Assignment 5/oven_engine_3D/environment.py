from enum import Enum

from pygame import Color

from oven_engine_3D.entities import Skybox


class Environment:
    class FogMode(Enum):
        DISABLED = -1
        LINEAR = 0
        EXP = 1
        EXP2 = 2

    class Tonemapping(Enum):
        NONE = -1
        ACES = 0
        REINHARD = 1
        UNCHARTED = 2

    class GlobalAmbientMode(Enum):
        NONE = 0
        CLEAR_COLOR = 1
        SKYBOX = 2

    def __init__(self,
                 fog_color = "gray",
                 start_fog = 1.,
                 end_fog = 20.,
                 clear_color = "black",
                 fog_density = .1,
                 global_ambient_strength = .2,
                 global_ambient_mode = GlobalAmbientMode.SKYBOX,
                 fog_mode = FogMode.LINEAR,
                 tonemap = Tonemapping.NONE):
        self.clear_color = Color(clear_color)
        self.fog_color = fog_color
        self.start_fog = start_fog
        self.end_fog = end_fog
        self.fog_density = fog_density
        self.fog_mode = fog_mode
        self.tonemap = tonemap
        self.global_ambient_mode = global_ambient_mode
        self.global_ambient_strength = global_ambient_strength

        self.skybox = None

    def generate_skybox(self, app, sky_textures):
        if type(sky_textures) is dict:
            self.skybox = Skybox(parent_app=app, sky_textures=sky_textures)

    @property
    def sky_color(self):
        return self.skybox.sky_color

    @property
    def global_ambient(self):
        if self.skybox is None and self.global_ambient_mode == Environment.GlobalAmbientMode.SKYBOX:
            return self.clear_color

        match self.global_ambient_mode:
            case Environment.GlobalAmbientMode.NONE:
                return "black"
            case Environment.GlobalAmbientMode.CLEAR_COLOR:
                return self.clear_color
            case Environment.GlobalAmbientMode.SKYBOX:
                return self.sky_color

    @property
    def fog_enabled(self):
        return self.fog_mode != Environment.FogMode.DISABLED