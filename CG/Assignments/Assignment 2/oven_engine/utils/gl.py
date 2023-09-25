import os.path
from enum import IntEnum

import numpy as np  # Used for faster texture loading
import pygame as pg
from OpenGL.GL import *
from OpenGL.constant import IntConstant
from PIL import Image
from pygame.color import Color
from pygame.colordict import THECOLORS
from pygame.font import SysFont, Font

from .collisions import AABB
from .geometry import *


class LineMode(IntEnum):
    STANDARD = GL_LINES
    STRIP = GL_LINE_STRIP
    LOOP = GL_LINE_LOOP

def __str_to_col(col_name: str):
    return Color(THECOLORS[col_name])
def __points_colors(points: list[Vector2D], colors: [list[Color] | list[str] | str | Color] = None):
    if type(colors) is str:
        colors = [__str_to_col(colors)] * len(points)
    elif type(colors) is Color:
        colors = [colors] * len(points)
    elif type(colors) is list:
        if len(colors) > len(points):
            colors = colors[:len(points)]
        elif len(colors) < len(points):
            colors += [colors[-1]] * (len(points) - len(colors))
    else:
        colors = None

    if colors is None:
        for p in points:
            glVertex2f(p.x, p.y)
    else:
        for p, c in zip(points, colors):
            if type(c) is str:
                c = __str_to_col(c)
            glColor3f(c.r/255., c.g/255., c.b/255.)
            glVertex2d(p.x, p.y)

def draw_triangle(p1, p2, p3, colors : [list[Color]|Color] = None, filled=True):
    """
    Draw a triangle given 3 points
    """
    
    if filled:
        glBegin(GL_TRIANGLES)
        __points_colors([p1, p2, p3], colors)
        glEnd()
    else:
        draw_lines([p1,p2,p3], mode=LineMode.LOOP)

def draw_lines(pts : list, mode=LineMode.STANDARD, width=1.0, colors : [list[Color]|Color] = None):
    """
    Draw a sequence of lines
    """

    glLineWidth(width)

    glBegin(mode)

    __points_colors(pts, colors)
        
    glEnd()

    glLineWidth(1.0)

def draw_strip(points: list[Vector2D], colors : [list[Color]|Color] = None):
    glBegin(GL_TRIANGLE_STRIP)

    __points_colors(points, colors)

    glEnd()


def draw_fan(points, colors : [list[Color]|Color] = None):
    glBegin(GL_TRIANGLE_FAN)

    __points_colors(points, colors)

    glEnd()

def draw_polygon(points: list[Vector2D], colors : [list[Color]|Color] = None, filled=False):
    """
    Draw a polygon given the points on the perimeter
    """
    count = len(points)
    assert count >= 3

    if filled:
        avg_point = points[0]
        for p in points:
            avg_point += p
        avg_point /= count

        draw_fan([avg_point] + points + [points[0]], colors=colors)
    else:
        draw_lines(points, mode=LineMode.LOOP)

def draw_circle(center: Vector2D, radius = 1.0, steps : int = 12, phase=0., colors : [list[Color]|Color] = None, filled=False):
    if filled:
        draw_slice(center, math.tau, radius, steps, phase, colors=colors)
    else:
        draw_arc(center, math.tau, radius, steps, phase, loop=True)

def __generate_circle_points(c, r, s, a_s, p):
    pts = []
    for s in range(s+1):
        angle = a_s * s + p
        point = r * Vector2D(math.sin(angle), math.cos(angle))
        point += c
        pts += [point]
    return pts

def draw_slice(center: Vector2D, max_angle: float, radius = 1.0, steps : int = 12, phase=0., colors : [list[Color]|Color] = None):
    angle_step = max_angle / steps
    draw_fan([center] + __generate_circle_points(center, radius, steps, angle_step, phase), colors=colors)

def draw_arc(center, max_angle, radius = 1.0, steps = 12, phase=0., loop=False):
    mode=(LineMode.LOOP if loop else LineMode.STANDARD)
    draw_lines(__generate_circle_points(center, radius, steps, max_angle / steps, phase), mode=mode)

def draw_aabb(aabb: AABB, color : [str|Color] = "white", pos_override : [Vector2D|None] = None):
    if type(color) is str:
        color = THECOLORS[color]

    color = Color(color)

    if pos_override is None:
        pos_override = aabb.center

    draw_box(pos_override, aabb.size, colors=[color]*4, filled=False, centered=True)

def draw_box(pos: Vector2D,
             size: [Vector2D | int | float],
             skew_x : [Vector2D|float] = 0.0, skew_y : [Vector2D|float] = 0.0,
             colors : [list[Color]|Color] = None, filled=True, centered=False):
    tl = pos
    if centered:
        tl -= size/2. 

    if type(skew_x) is Vector2D:
        skew_y = skew_x.y
        skew_x = skew_x.x

    if type(size) in [int, float]:
        size = Vector2D(size, size)

    br = tl + size

    tr = Vector2D(br.x, tl.y)
    bl = Vector2D(tl.x, br.y)

    tl.x += skew_x
    tr.x += skew_x
    bl.x -= skew_x
    br.x -= skew_x

    tl.y += skew_y
    bl.y += skew_y
    tr.y -= skew_y
    br.y -= skew_y

    if filled:
        draw_strip([bl, tl, br, tr], colors=colors)
    else:
        draw_lines([bl, tl, tr, br], mode=LineMode.LOOP)

#############

def load_texture(texture_path,
                 filtering=GL_LINEAR, clamping : [list[int]|int] = GL_CLAMP_TO_BORDER,
                 color_format=GL_RGBA8, pixel_format=GL_RGBA):
    try:
        text = Image.open(texture_path)
    except IOError:
        print(f"Failed to load texture '{texture_path}'")
        return -1

    if not(filtering in [GL_NEAREST, GL_LINEAR]):
        filtering = GL_NEAREST

    textData = np.array(list(text.getdata()))
    text.close()

    textID = create_texture(textData, Vector2D(text.width, text.height), filtering, clamping, color_format, pixel_format)

    print("done")

    return textID

def unload_texture(textureID: int):
    if not is_texture_valid(textureID):
        print(f"Invalid texture ID {textureID}")
        return False

    glDeleteTextures(textureID, 1)
    return True

def surface_to_texture(surf: pg.Surface,
                       filtering=GL_NEAREST, clamping : [list[int]|int] = GL_CLAMP_TO_BORDER,
                       color_format=GL_RGBA8, pixel_format=GL_RGBA):
    w, h = surf.get_size()
    data = pg.image.tostring(surf, "RGBA", True)

    if not(filtering in [GL_NEAREST, GL_LINEAR]):
        filtering = GL_NEAREST

    return create_texture(data, Vector2D(w, h), filtering, clamping, color_format, pixel_format)

def create_texture(texture_data, size: Vector2D,
                   filtering=GL_NEAREST, clamping : [list[IntConstant]|IntConstant] = GL_CLAMP_TO_BORDER,
                   color_format=GL_RGBA8, pixel_format=GL_RGBA):
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


    glTexImage2D(GL_TEXTURE_2D, 0, color_format, size.x, size.y, 0, pixel_format, GL_UNSIGNED_BYTE, texture_data)

    return int(textID)

def is_texture_valid(textureID: int):
    return glGetIntegerv(GL_TEXTURE_BINDING_2D, textureID).value != -1

def draw_texture(textureID: int,
                 center: Vector2D, scale: [Vector2D|float] = Vector2D(10.),
                 flipH = False, flipV = False, scale_relative=False,
                 skew : [Vector2D|float] = Vector2D(0.),
                 img_tl : Vector2D = Vector2D(0.,0.), img_br : Vector2D = Vector2D(1.,1.),
                 colors : [list[Color]|Color] = None, invert=False):
    if not is_texture_valid(textureID):
        print(f"Invalid texture ID {textureID}")
        return

    if type(scale) is float:
        scale = Vector2D(scale)

    if scale_relative:
        scale *= get_texture_size(textureID)

    if flipH:
        scale.x *= -1.
    if flipV:
        scale.y *= -1.

    if type(skew) is float:
        skew = Vector2D(skew)

    img_tr = Vector2D(img_br.x, img_tl.y)
    img_bl = Vector2D(img_tl.x, img_br.y)

    verts = (Vector2D(1, 1) + Vector2D(-1, -1)*skew,
             Vector2D(1, -1) + Vector2D(1, -1)*skew,
             Vector2D(-1, -1) + Vector2D(1, 1)*skew,
             Vector2D(-1, 1) + Vector2D(-1, 1)*skew)
    texts = (img_tr,
             img_br,
             img_bl,
             img_tl)
    surf = (0, 1, 2, 3)

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Bind textureID as the ID of the texture currently drawn
    glBindTexture(GL_TEXTURE_2D, textureID)

    glBegin(GL_QUADS)
    for i in surf:
        glTexCoord2f(texts[i].x, texts[i].y)

        if not colors is None:
            glColor3f(colors[i].r/255., colors[i].g/255., colors[i].b/255.)

        vertex = center + verts[i]*scale
        glVertex2f(vertex.x, vertex.y)
    glEnd()

    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)

def __get_texparam(textureID: int, param: int, mipmap_level : int = 0, count : int = 1, isInt : bool = True):
    if not is_texture_valid(textureID):
        print(f"Invalid texture ID {textureID}")
        return []

    datatype = ctypes.c_int if isInt else ctypes.c_float
    func = glGetTextureLevelParameteriv if isInt else glGetTextureLevelParameterfv

    output = (datatype * count)()
    func(textureID, mipmap_level, param, output)

    return output[:]

def get_texparam_float(textureID: int, param: int, mipmap_level : int = 0, count : int = 1) -> [float]:
    return __get_texparam(textureID, param, mipmap_level, count, isInt = False)

def get_texparam_int(textureID: int, param: int, mipmap_level : int = 0, count : int = 1) -> [int]:
    return __get_texparam(textureID, param, mipmap_level, count, isInt = True)

def get_texture_size(textureID: int):
    w = get_texparam_int(textureID, GL_TEXTURE_WIDTH)[0]
    h = get_texparam_int(textureID, GL_TEXTURE_HEIGHT)[0]

    return Vector2D(w,h)

#############

def set_draw_color(color:[Color|str|tuple]):
    """
    Set glColor
    """
    if type(color) is str:
        color = THECOLORS[color]

    color = Color(color)

    glColor3f(color.r/255., color.g/255., color.b/255.)

def set_clear_color(color:[Color|str|tuple]):
    """
    Set color for glClear
    """
    if type(color) is str:
        color = THECOLORS[color]
        
    color = Color(color)
    
    glClearColor(color.r/255., color.g/255., color.b/255., color.a/255.)

#############

def translate_2D(offset: Vector2D):
    glTranslate(offset.x, offset.y, 0.)

def rotate_2D(angle: float):
    glRotate(angle, 0, 0, 1)

def scale_2D(scale_fact: Vector2D):
    glScale(scale_fact.x, scale_fact.y, 1.)

def flip_h():
    scale_2D(Vector2D(-1., 1.))

def flip_v():
    scale_2D(Vector2D(1., -1.))

push_matrix = glPushMatrix
pop_matrix = glPopMatrix

#############

# note: font/background color should be specified with ranges [0-255], not [0-1]
# note: if image width/height not declared, will be set according to rendered text size
class Text:
    def __init__(self, text, fontFileName=None, fontSize=24,
                 fontColor : [Color|str] = "white", backgroundColor : [Color|str|None] = None,
                 transparent=False, antialias=True, width=0., height=0.,
                 alignHorizontal="CENTER", alignVertical="CENTER"):

        self.text = text
        if fontFileName is None or not(os.path.exists(fontFileName)):
            print(f"Font '{fontFileName}' not found - defaulting to Arial...")
            self.font = SysFont("Arial", fontSize)
        else:
            self.font = Font(fontFileName, fontSize)

        if not backgroundColor is None:
            if type(fontColor) is str:
                fontColor = THECOLORS[fontColor]
            fontColor = Color(fontColor)
            if type(backgroundColor) is str:
                backgroundColor = THECOLORS[backgroundColor]
            backgroundColor = Color(backgroundColor)

        self.fontColor = fontColor
        self.backgroundColor = backgroundColor
        self.transparent = transparent or (backgroundColor is None)
        self.antialias = antialias
        self.size = Vector2D(width, height)
        self.alignHorizontal = alignHorizontal
        self.alignVertical = alignVertical
        self.surface = None # pg.Surface((self.size.x, self.size.y), pg.SRCALPHA)

        self.reload_surface()

    def reload_surface(self):
        fontSurf = self.font.render(self.text, self.antialias, self.fontColor)
        # determine size of rendered text for alignment
        textSize = Vector2D(self.font.size(self.text))

        # if image dimensions are not specified, use font surface size as default
        if self.size.x == 0.:
            self.size.x = textSize.x
        if self.size.y == 0:
            self.size.y = textSize.y

        # create image with transparency channel
        self.surface = pg.Surface((self.size.x, self.size.y), pg.SRCALPHA)

        # background color used when not transparent
        if not self.transparent:
            self.surface.fill(self.backgroundColor)

        # values used for alignment;
        #  only has an effect if image size is set larger than rendered text size
        alignment = Vector2D(0.)
        if self.alignHorizontal == "CENTER":
            alignment.x = 0.5
        elif self.alignHorizontal == "RIGHT":
            alignment.x = 1.0

        if self.alignVertical == "MIDDLE":
            alignment.y = 0.5
        elif self.alignVertical == "BOTTOM":
            alignment.y = 1.0

        tl = alignment * (self.size - textSize)
        textRect = fontSurf.get_rect(
            topleft=(tl.x, tl.y)
        )

        self.surface.blit(fontSurf, textRect)
        return self.surface

def draw_text(text_params: Text, position: Vector2D, scale:[Vector2D | float] = 1., filtering = GL_NEAREST):
    texture = surface_to_texture(text_params.surface, filtering=filtering)

    if type(scale) is float:
        scale = Vector2D(scale)

    draw_texture(texture, position, text_params.size * scale, flipV=True)
