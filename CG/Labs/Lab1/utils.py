## 22/08

import math
from OpenGL.GL import *
from OpenGL.GLU import *

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "True"
import pygame as pg
from pygame.locals import *
from pygame.color import Color

class Vertex2D:
    def __init__(self, x, y=None) -> None:
        if y is None:
            y = x
        
        if type(x) is tuple and len(x) >= 2:
            self.x, self.y = x[0], x[1]
        else:
            self.x, self.y = x, y

    def __add__(self, other):
        if type(other) is tuple:
            other = Vertex2D(other)
            
        if type(other) is Vertex2D:
            return Vertex2D(self.x + other.x, self.y + other.y)
        return self
        
    def __mul__(self, other):
        if type(other) in [int, float]:
            return Vertex2D(self.x * other, self.y * other)
        elif other is Vertex2D:
            return Vertex2D(self.x * other.x, self.y * other.y)

        return self
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __pow__(self, exponent):
        return Vertex2D(self.x**exponent, self.y**exponent)
    
    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)
    
    def normalized(self):
        l = self.length()
        if l == 0.0:
            return self

        return self * (1.0 / self.length())
    

def gl_setcolor(color:Color):
    """
    Set glColor
    """

    glColor3f(color.r, color.g, color.b)


def gl_triangle(p1, p2, p3):
    """
    Draw a triangle given 3 points
    """
    
    glBegin(GL_TRIANGLES)
    glVertex2f(p1.x, p1.y)
    glVertex2f(p2.x, p2.y)
    glVertex2f(p3.x, p3.y)
    glEnd()


def gl_lines(pts : list, loop=False):
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

def gl_lines(pts : list, loop=False):
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

def gl_circle(center, radius = 1.0, steps = 12, phase=0.):
    gl_arc(center, math.tau, radius, steps, phase, loop=True)

def gl_arc(center, max_angle, radius = 1.0, steps = 12, phase=0., loop=False):
    def __line_generator(center, radius, steps, angle_step, phase):
        for s in range(steps):
            angle = angle_step * s + phase
            point = radius * Vertex2D(math.sin(angle), math.cos(angle)) 
            point += center
            yield point

    gl_lines(__line_generator(center, radius, steps, max_angle / steps, phase), loop=loop)

def gl_triangle(p1: Vertex2D, p2: Vertex2D, p3: Vertex2D):
    """
    Draw a triangle given 3 points
    """
    
    glBegin(GL_TRIANGLES)
    glVertex2f(p1.x, p1.y)
    glVertex2f(p2.x, p2.y)
    glVertex2f(p3.x, p3.y)
    glEnd()

def gl_box(tl: Vertex2D, size: Vertex2D):
    br = tl + size

    tr = Vertex2D(br.x, tl.y)
    bl = Vertex2D(tl.x, br.y)

    glBegin(GL_TRIANGLE_STRIP)
    glVertex2f(bl.x, bl.y)
    glVertex2f(tl.x, tl.y)
    glVertex2f(br.x, br.y)
    glVertex2f(tr.x, tr.y)
    glEnd()

def gl_set_drawcolor(color:Color):
    """
    Set glColor
    """

    glColor3f(color.r, color.g, color.b)

def gl_set_clearcolor(color:Color):
    """
    Set color for glClear
    """

    glClearColor(color.r, color.g, color.b, color.a)

if __name__ == "__main__":
    p = Vertex2D(1,2)
    print(p)
    p = p ** 2
    print(p)