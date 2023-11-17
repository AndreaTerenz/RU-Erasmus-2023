from pygame import Color

def is_collection(thing):
    return isinstance(thing, (list, tuple))


def add_missing(dict1, dict2):
    dict1.update({key: value for key, value in dict2.items() if not key in dict1})

def get_color(color):
    if type(color) is str:
        color = Color(color)

    if type(color) is Color:
        color = color.normalize()
    elif type(color) in [int, float]:
        color = color, color, color, 1.

    if len(color) == 3:
        color = (*color, 1.)
    elif len(color) == 2:
        color = [color[0]] * 3 + [color[1]]

    return color