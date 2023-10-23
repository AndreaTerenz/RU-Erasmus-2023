from typing import Collection


class Color:
    def __init__(self, r: [str|Collection|float], g=None, b=None, a=1.):
        if isinstance(r, str):
            r, g, b, a = Color.hex_to_rgb(r)
        elif isinstance(r, Collection):
            if len(r) == 3:
                r, g, b = r
                a = 1.
            elif len(r) == 4:
                r, g, b, a = r

        self.r = r
        self.g = g
        self.b = b
        self.a = a

    @staticmethod
    def hex_to_rgb(hex_str):
        hex_str = hex_str.lstrip("#")
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))