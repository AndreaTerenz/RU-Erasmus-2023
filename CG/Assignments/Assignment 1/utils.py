# Assignment 1
import math
from OpenGL.GL import *
from OpenGL.GLU import *

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "True"
import pygame as pg
from pygame.locals import *
from pygame.color import Color

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
    
    def normalized(self):
        l = self.length()
        if l == 0.0:
            return self

        return self / l
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y

def rect_contains_point(tl: Vector2D, size: Vector2D, point: Vector2D):
    return (tl.x <= point.x <= tl.x + size.x) and (tl.y <= point.y <= tl.y + size.y)

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

def draw_lines(pts : list, loop=False):
    """
    Draw a sequence of lines (connect the 1st and last points if loop=True)
    """
    
    if not loop:
        glBegin(GL_LINES)
    else:
        glBegin(GL_LINE_LOOP)

    for p in pts:
        glVertex2f(p.x, p.y)
        
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

def draw_box(tl: Vector2D, size: Vector2D):
    br = tl + size

    tr = Vector2D(br.x, tl.y)
    bl = Vector2D(tl.x, br.y)

    glBegin(GL_TRIANGLE_STRIP)
    glVertex2f(bl.x, bl.y)
    glVertex2f(tl.x, tl.y)
    glVertex2f(br.x, br.y)
    glVertex2f(tr.x, tr.y)
    glEnd()

def draw_box_centered(pos: Vector2D, size: Vector2D):
    tl = pos - size/2.
    draw_box(tl, size)

def set_draw_color(color:Color):
    """
    Set glColor
    """

    glColor3f(color.r, color.g, color.b)

def set_clear_color(color:Color):
    """
    Set color for glClear
    """

    glClearColor(color.r, color.g, color.b, color.a)