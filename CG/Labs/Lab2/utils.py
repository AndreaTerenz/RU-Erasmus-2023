# 28.08
import math
from OpenGL.GL import *
from OpenGL.GLU import *

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "True"
import pygame as pg
from pygame.locals import *
from pygame.color import Color
from pygame.colordict import THECOLORS

class Vector2D:
    def __init__(self, x, y=None) -> None:
        if y is None:
            y = x
        
        if type(x) is tuple and len(x) >= 2:
            self.x, self.y = x[0], x[1]
        else:
            self.x, self.y = x, y

    def __neg__(self):
        return Vector2D(-self.x, -self.y)

    def __eq__(self, other):
        return type(other) is Vector2D and (self.x == other.x and self.y == other.y)

    def __add__(self, other):
        if type(other) is tuple:
            other = Vector2D(other)
            
        if type(other) is Vector2D:
            return Vector2D(self.x + other.x, self.y + other.y)
        
        return self
    
    def __sub__(self, other):
        return self + (other * -1.)
        
    def __mul__(self, other):
        if type(other) in [int, float]:
            other = Vector2D(other, other)

        if type(other) is Vector2D:
            return Vector2D(self.x * other.x, self.y * other.y)

        return self
    
    def __truediv__(self, other):
        if type(other) in [int, float]:
            other = Vector2D(other, other)

        if type(other) is Vector2D:
            return Vector2D(self.x / other.x, self.y / other.y)

        return self
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __pow__(self, exponent):
        return Vector2D(self.x**exponent, self.y**exponent)
    
    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def length_sq(self):
        return self.x**2 + self.y**2

    def length(self):
        return math.sqrt(self.length_sq())

    def angle(self):
        return math.atan2(self.y, self.x)
    
    def scale_to_length(self, target_len):
        l = self.length()
        if l == 0.0:
            return self

        return self * (target_len / l)

    def normalized(self):
        return self.scale_to_length(1.)

    def clamp_length(self, target_len):
        target_len = target_len ** 2
        l = self.length_sq()

        if l <= target_len:
            return self
        
        return self.scale_to_length(math.sqrt(target_len))
        
    def is_normalized(self):
        return self.length_sq() == 1.

    def is_longer_than(self, other):
        return self.length_sq() > other.length_sq()
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y
    
    def cross(self, other):
        """
        This is the signed area of the parallelogram formed by the two vectors.
        If the second vector is clockwise from the first vector, then
        the cross product is the positive area. If counter-clockwise,
        the cross product is the negative area.
        """

        return self.x * other.y - self.y * other.x
    
    
    def angle_with(self, other):
        cos_angle = self.dot(other) / (self.length() * other.length())

        return math.acos(cos_angle)
    
    def rotated(self, angle):
        angle = math.fmod(angle, math.tau)

        if angle == math.tau:
            return self
        
        if angle == math.tau/2.:
            return Vector2D(-self.x, -self.y)
        
        if angle == math.tau/4.:
            return Vector2D(-self.y, self.x)
        
        if angle == math.tau*3./4.:
            return Vector2D(self.y, -self.x)

        x_rot = math.cos(angle) * self.x - math.sin(angle) * self.y
        y_rot = math.sin(angle) * self.x + math.cos(angle) * self.y

        return Vector2D(x_rot, y_rot)

    def normal(self):
        return self.rotated(math.tau/4.)
    
    def projected(self, other):
        dot_p = self.dot(other)
        return dot_p / other.length()

    def reflected(self, normal_vec):
        normal_vec = normal_vec.normalized()

        dot_p = self.dot(normal_vec)

        return self - 2 * dot_p * normal_vec

def rect_contains_point(tl: Vector2D, size: Vector2D, point: Vector2D):
    return (tl.x <= point.x <= tl.x + size.x) and (tl.y <= point.y <= tl.y + size.y)

def polar_to_cartesian(radius: float, angle: float):
    return Vector2D(radius*math.cos(angle), radius*math.sin(angle))

def cartesian_to_polar(x: float, y: float):
    return Vector2D(x**2 + y**2, math.atan2(y, x))

def draw_triangle(p1, p2, p3, filled=True):
    """
    Draw a triangle given 3 points
    """
    
    if filled:
        glBegin(GL_TRIANGLES)
        glVertex2f(p1.x, p1.y)
        glVertex2f(p2.x, p2.y)
        glVertex2f(p3.x, p3.y)
        glEnd()
    else:
        draw_lines([p1,p2,p3], loop=True)

def draw_lines(pts : list, strip=False, loop=False, width=1.0):
    """
    Draw a sequence of lines
    """

    glLineWidth(width)
    
    if loop:
        glBegin(GL_LINE_LOOP)
    elif strip:
        glBegin(GL_LINE_STRIP)
    else:
        glBegin(GL_LINES)

    for p in pts:
        glVertex2f(p.x, p.y)
        
    glEnd()

    glLineWidth(1.0)

def draw_strip(points: list[Vector2D]):
    glBegin(GL_TRIANGLE_STRIP)
    
    for p in points:
        glVertex2d(p.x, p.y)

    glEnd()


def draw_fan(points: list[Vector2D]):
    glBegin(GL_TRIANGLE_FAN)
    
    for p in points:
        glVertex2d(p.x, p.y)

    glEnd()

def draw_circle(center: Vector2D, radius = 1.0, steps : int = 12, phase=0., filled=False):
    if filled:
        draw_slice(center, math.tau, radius, steps, phase)
    else:
        draw_arc(center, math.tau, radius, steps, phase, loop=True)

def draw_slice(center: Vector2D, max_angle: float, radius = 1.0, steps : int = 12, phase=0.):
    angle_step = max_angle / steps
    def __gen(center, radius, steps, angle_step, phase):
        yield center
        for s in range(steps+1):
            angle = angle_step * s + phase
            point = radius * Vector2D(math.sin(angle), math.cos(angle)) 
            point += center
            yield point

    draw_fan(__gen(center, radius, steps, angle_step, phase))

def draw_arc(center, max_angle, radius = 1.0, steps = 12, phase=0., loop=False):
    def __gen(center, radius, steps, angle_step, phase):
        for s in range(steps):
            angle = angle_step * s + phase
            point = radius * Vector2D(math.sin(angle), math.cos(angle)) 
            point += center
            yield point

    draw_lines(__gen(center, radius, steps, max_angle / steps, phase), loop=loop)

def draw_triangle(p1: Vector2D, p2: Vector2D, p3: Vector2D):
    """
    Draw a triangle given 3 points
    """
    
    glBegin(GL_TRIANGLES)
    glVertex2f(p1.x, p1.y)
    glVertex2f(p2.x, p2.y)
    glVertex2f(p3.x, p3.y)
    glEnd()

def draw_box(tl: Vector2D, size: [Vector2D | int | float], skew_x = 0.0, skew_y = 0.0, filled=True):
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
        draw_strip([bl, tl, br, tr])
    else:
        draw_lines([bl, tl, tr, br], loop=True)

def draw_box_centered(pos: Vector2D, size: Vector2D):
    tl = pos - size/2.
    draw_box(tl, size)

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