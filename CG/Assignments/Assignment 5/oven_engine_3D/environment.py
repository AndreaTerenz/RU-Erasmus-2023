from pygame import Color
from enum import Enum

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

    def __init__(self, global_ambient = Color("black"),
                 fog_color = Color("gray"),
                 start_fog = 1.,
                 end_fog = 20.,
                 fog_density = .1,
                 fog_mode = FogMode.LINEAR,
                 tonemap = Tonemapping.NONE):
        #TODO: Actually use this color..
        self.global_ambient = global_ambient
        self.fog_color = fog_color
        self.start_fog = start_fog
        self.end_fog = end_fog
        self.fog_density = fog_density
        self.fog_mode = fog_mode
        self.tonemap = tonemap

    @property
    def fog_enabled(self):
        return self.fog_mode != Environment.FogMode.DISABLED