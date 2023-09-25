import math
from abc import abstractmethod

import pygame as pg
from OpenGL.GL import *

from oven_engine.entities import Entity
from oven_engine.utils.collisions import *
from oven_engine.utils.geometry import Vector2D
from oven_engine.utils.gl import draw_texture, get_texture_size
from oven_engine.utils.utils import clamp, sign, is_key_pressed, is_key_released


class Ball(Entity):
    def __init__(self, position, parent, speed=50.) -> None:
        super().__init__(position, parent, color="white", name="Ball", collision_mode=CollisionMode.ENABLED)

        self.direction = Vector2D.from_polar(math.tau/6.)
        self.last_ok_pos = position
        self.speed = speed
        self.speed_mult = 1.
        self.radius = 12.
        self.collider = CircleCollider(self.radius, self)
        self.debug_draw = False

        self.texture = self.parent_app.tm.load_texture("assets/sprites/img.png", filtering=GL_NEAREST)

        self.text_size = get_texture_size(self.texture).reshape_with_ratio(self.radius)

    def update(self, delta):
        coll_norm = self.parent_app.cm.total_collision_normal(self)

        if coll_norm != Vector2D.ZERO:
            self.direction = self.direction.reflected(coll_norm)
            self.position = self.last_ok_pos
        else:
            self.last_ok_pos = self.position

        # Apply
        self.position += self.direction * self.speed * self.speed_mult * delta

    def reset(self):
        # Could reset direction too, but keeping the last direction vector
        # gives it some fun unpredictability
        self.position = self.parent_app.screen_center

    def handle_event(self, ev):
        pass

    def display(self):
        draw_texture(self.texture, Vector2D.ZERO, abs(self.text_size), flipH=(sign(self.direction.x) < 0.))

    @property
    def aabb(self):
        return AABB.from_circle(self.position, self.radius)

class Paddle(Entity):
    def __init__(self, parent, color, offset=300., speed=140., name="") -> None:
        super().__init__(
            Vector2D(offset, 0.) + parent.screen_center,
            parent, color=color, name=name, collision_mode=CollisionMode.RECEIVE_ONLY)

        self.size = Vector2D(20., 100.)
        self.speed = speed
        self.direction = 0

        w_h = self.parent_app.win_size.y
        self.min_y = self.size.y/2.
        self.max_y = w_h - self.size.y/2.

        self.collider = AABBCollider(self.size, self)
        self.debug_draw = False
        self.texture = self.parent_app.tm.load_texture("assets/sprites/paddle.png", filtering=GL_NEAREST)

    def update(self, delta):
        self.direction = self.get_direction()
        new_y = self.position.y + self.speed * delta * self.direction

        self.position.y = clamp(new_y, self.min_y, self.max_y)

    def handle_event(self, ev):
        pass

    def display(self):
        draw_texture(self.texture, Vector2D.ZERO, self.size / 2.)

    @abstractmethod
    def get_direction(self):
        pass

    @property
    def aabb(self):
        return AABB(self.position - self.size/2., self.size)


class AIPaddle(Paddle):
    def __init__(self, parent, ball: Ball, speed=140., name="", speed_mult = .7):
        super().__init__(parent, speed=speed, offset=-300., color="red", name=name)

        self.ball = ball
        self.speed_mult = speed_mult

    def get_direction(self):
        # Ignore ball if it's moving away
        if self.ball_approaching():
            return 0

        return sign(self.ball.position.y - self.position.y)

    def ball_approaching(self):
        return sign(self.ball.direction.x) == sign(self.ball.position.x - self.position.x)

    def update(self, delta):
        self.speed = self.speed_mult * self.ball.speed
        super().update(delta)

class PlayerPaddle(Paddle):
    PADDLE_UP = 1
    PADDLE_STOP = 0
    PADDLE_DOWN = -1
    PADDLE_UP_D = 2
    PADDLE_DOWN_U = -2

    UP_KEYS = [pg.K_UP, pg.K_w]
    DOWN_KEYS = [pg.K_DOWN, pg.K_s]
    ALL_KEYS = UP_KEYS+DOWN_KEYS

    def __init__(self, parent, speed=140., name=""):
        super().__init__(parent, speed=speed*1.1, offset=300., color="green", name=name)

        self.state = PlayerPaddle.PADDLE_STOP

    def handle_event(self, ev):
        super().handle_event(ev)

        if not (ev.type in [pg.KEYDOWN, pg.KEYUP] and ev.key in PlayerPaddle.ALL_KEYS):
            return

        if self.state == PlayerPaddle.PADDLE_STOP:
            if is_key_pressed(ev, PlayerPaddle.UP_KEYS):
                self.state = PlayerPaddle.PADDLE_UP
            if is_key_pressed(ev, PlayerPaddle.DOWN_KEYS):
                self.state = PlayerPaddle.PADDLE_DOWN

        if self.state == PlayerPaddle.PADDLE_UP:
            if is_key_pressed(ev, PlayerPaddle.DOWN_KEYS):
                self.state = PlayerPaddle.PADDLE_UP_D
            if is_key_released(ev, PlayerPaddle.UP_KEYS):
                self.state = PlayerPaddle.PADDLE_STOP

        if self.state == PlayerPaddle.PADDLE_DOWN:
            if is_key_pressed(ev, PlayerPaddle.UP_KEYS):
                self.state = PlayerPaddle.PADDLE_DOWN_U
            if is_key_released(ev, PlayerPaddle.DOWN_KEYS):
                self.state = PlayerPaddle.PADDLE_STOP

        if self.state in [PlayerPaddle.PADDLE_UP_D, PlayerPaddle.PADDLE_DOWN_U]:
            if is_key_released(ev, PlayerPaddle.DOWN_KEYS):
                self.state = PlayerPaddle.PADDLE_UP
            if is_key_released(ev, PlayerPaddle.UP_KEYS):
                self.state = PlayerPaddle.PADDLE_DOWN

    def get_direction(self):
        return sign(self.state)