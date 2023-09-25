# Assignment 2
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "True"
import pygame as pg

from .geometry import *

def rect_contains_point(tl: Vector2D, size: Vector2D, point: Vector2D):
    return (tl.x <= point.x <= tl.x + size.x) and (tl.y <= point.y <= tl.y + size.y)

def polar_to_cartesian(radius: float, angle: float):
    return Vector2D(radius*math.cos(angle), radius*math.sin(angle))

def cartesian_to_polar(x: float, y: float):
    return Vector2D(x**2 + y**2, math.atan2(y, x))

def sign(x: float):
    if x == 0.:
        return 0.

    return 1. if (x > 0.) else -1.

def clamp(x, min_val, max_val):
    return max(min_val, min(max_val, x))

def is_key_pressed(ev, key: [int|list[int]]):
    if type(key) is int:
        key = [key]

    return ev.type == pg.KEYDOWN and ev.key in key

def is_key_released(ev, key: [int|list[int]]):
    if type(key) is int:
        key = [key]

    return ev.type == pg.KEYUP and ev.key in key