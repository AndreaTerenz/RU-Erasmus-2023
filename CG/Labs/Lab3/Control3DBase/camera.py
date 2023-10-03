import math

import pygame as pg

from Control3DBase.Base3DObjects import Entity3D
from Control3DBase.Matrices import ProjectionMatrix, ViewMatrix
from Control3DBase.utils.geometry import Vector3D, Vector2D


class Camera(Entity3D):
    def __init__(self, parent_app,
                 eye = Vector3D.ZERO, look_at = Vector3D.FORWARD, up_vec=Vector3D.UP,
                 fov =math.tau / 8., ratio =16. / 9., near=.5, far=100):
        super().__init__(parent_app, origin=eye, size=0., color=None, vertex_shader=None, frag_shader=None)

        self.projection_matrix = ProjectionMatrix.perspective(fov, ratio, near=near, far=far)
        self.view_matrix = ViewMatrix()
        self.target = Vector3D.ZERO

        self.look_at(look_at, up_vec)

    def draw(self):
        pass

    def look_at(self, target, up=Vector3D.UP):
        self.target = target
        self.view_matrix.look_at(self.origin, target, up)

    def slide(self, offset):
        self.origin += offset
        self.target += offset
        self.view_matrix.slide(*offset)

class FreeLookCamera(Camera):
    def __init__(self, parent_app,
                 eye = Vector3D.ZERO, look_at = Vector3D.FORWARD, up_vec=Vector3D.UP,
                 fov =math.tau / 8., ratio =16. / 9., near=.5, far=100):
        super().__init__(parent_app, eye, look_at, up_vec, fov, ratio, near, far)

        self.slide_keys = {
            pg.K_w: Vector3D.UP,
            pg.K_s: Vector3D.DOWN,
            pg.K_a: Vector3D.LEFT,
            pg.K_d: Vector3D.RIGHT,
            pg.K_q: Vector3D.FORWARD,
            pg.K_e: Vector3D.BACKWARD,
        }

        self.rotation_keys = [
            # Pitch   # Yaw     # Roll
            pg.K_i, pg.K_k, pg.K_j, pg.K_l, pg.K_u, pg.K_o
        ]

        self.keys_states = {key: False for key in
                            list(self.slide_keys.keys()) +
                            self.rotation_keys}

    def _update(self, delta):
        slide_dir = Vector3D.ZERO
        for key, _dir in self.slide_keys.items():
            state = self.keys_states[key]
            fact = 1. if state else 0.
            slide_dir += _dir * fact

        slide_dir = slide_dir.normalized
        if slide_dir != Vector3D.ZERO:
            self.slide(slide_dir * delta * 20.)

        pitch = 0.
        if self.keys_states[pg.K_i]:
            pitch = 1.
        elif self.keys_states[pg.K_k]:
            pitch = -1.

        roll = 0.
        if self.keys_states[pg.K_u]:
            roll = 1.
        elif self.keys_states[pg.K_o]:
            roll = -1.

        yaw = 0.
        if self.keys_states[pg.K_j]:
            yaw = 1.
        elif self.keys_states[pg.K_l]:
            yaw = -1.

        self.view_matrix.rotate_x(pitch * delta)
        self.view_matrix.rotate_y(yaw * delta)
        self.view_matrix.rotate_z(roll * delta)

    def handle_event(self, event):
        if not (hasattr(event, 'key')):
            return

        if event.key in self.keys_states.keys():
            self.keys_states[event.key] = (event.type == pg.KEYDOWN)

class FPCamera(Camera):
    def __init__(self, parent_app, sensitivity = 50.,
                 eye = Vector3D.ZERO, look_at = Vector3D.FORWARD, up_vec=Vector3D.UP,
                 fov =math.tau / 8., ratio =16. / 9., near=.5, far=100):
        super().__init__(parent_app, eye, look_at, up_vec, fov, ratio, near, far)

        self.sensitivity = sensitivity

        h_dist = eye.distance_to(look_at)
        v_dist = eye.y - look_at.y
        angle_to_target = math.atan2(v_dist, h_dist)

        self.head_pitch = angle_to_target

        self.slide_keys = {
            pg.K_w: Vector3D.FORWARD,
            pg.K_s: Vector3D.BACKWARD,
            pg.K_a: Vector3D.RIGHT,
            pg.K_d: Vector3D.LEFT,
        }

        self.rotation_keys = [
            # Pitch          # Turn
            pg.K_i, pg.K_k, pg.K_j, pg.K_l
        ]

        self.keys_states = {key: False for key in
                            list(self.slide_keys.keys()) +
                            self.rotation_keys}

    def _update(self, delta):
        self.pitch(delta)
        self.turn(delta)
        self.move(delta)

    def move(self, delta):
        slide_dir = Vector3D.ZERO
        for key, _dir in self.slide_keys.items():
            state = self.keys_states[key]
            fact = 1. if state else 0.
            slide_dir += _dir * fact

        slide_dir = slide_dir.normalized
        if slide_dir != Vector3D.ZERO:
            h_dir = (self.view_matrix.eye - self.target).x0z.normalized
            angle = math.atan2(h_dir.z, h_dir.x)

            offset = (slide_dir * delta * 2.)
            offset = offset.rotate(Vector3D.UP, angle)

            self.view_matrix.eye += offset

    def pitch(self, delta):
        m_delta = self.parent_app.mouse_delta
        if m_delta != Vector2D.ZERO:
            self.view_matrix.rotate_x(m_delta.y * delta * self.sensitivity)

    def turn(self, delta):
        m_delta = self.parent_app.mouse_delta
        if m_delta != Vector2D.ZERO:
            self.view_matrix.rotate_global_y(-m_delta.x * delta * self.sensitivity)

    def handle_event(self, event):
        if not (hasattr(event, 'key')):
            return

        if event.key in self.keys_states.keys():
            self.keys_states[event.key] = (event.type == pg.KEYDOWN)

