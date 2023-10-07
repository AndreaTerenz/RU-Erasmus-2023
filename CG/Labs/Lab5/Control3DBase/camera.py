import math

import numpy as np
import pygame as pg

from Control3DBase.Base3DObjects import Entity
from Control3DBase.Matrices import ProjectionMatrix, ViewMatrix
from Control3DBase.utils.geometry import Vector3D, Vector2D


class Camera(Entity):

    def __init__(self, parent_app,
                 eye = Vector3D.ZERO, look_at = Vector3D.FORWARD, up_vec=Vector3D.UP,
                 fov =math.tau / 8., ratio =16. / 9., near=.5, far=100):
        super().__init__(parent_app, origin=eye)

        self.projection_matrix = ProjectionMatrix.perspective(fov, ratio, near=near, far=far)
        self.view_matrix = ViewMatrix()
        self.target = Vector3D.ZERO

        self.look_at(look_at, up_vec)

    def _update(self, delta):
        pass

    def handle_event(self, ev):
        pass

    def look_at(self, target, up=Vector3D.UP):
        self.target = target
        self.view_matrix.look_at(self.origin, target, up)

    def slide(self, offset):
        self.target += offset
        self.view_matrix.slide(*offset)

    def get_rot_angles(self):
        # Calculate the yaw (around global Z-axis) in radians
        theta = np.arctan2(self.view_matrix.n.y, self.view_matrix.n.x)

        # Calculate the pitch (around global Y-axis) in radians
        phi = np.arctan2(-self.view_matrix.n.z, np.sqrt(self.view_matrix.n.x ** 2 + self.view_matrix.n.y ** 2))

        # Calculate the roll (around global X-axis) in radians
        psi = np.arctan2(self.view_matrix.u.z, self.view_matrix.v.z)

        return psi, phi, theta

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
    KEYBOARD = 0
    MOUSE = 1

    def __init__(self, parent_app, sensitivity = 50., mode=MOUSE,
                 eye = Vector3D.ZERO, look_at = Vector3D.FORWARD, up_vec=Vector3D.UP,
                 fov =math.tau / 8., ratio =16. / 9., near=.5, far=100):
        super().__init__(parent_app, eye, look_at, up_vec, fov, ratio, near, far)

        self.sensitivity = sensitivity
        self.mode = mode

        if self.mode == FPCamera.MOUSE:
            pg.mouse.set_visible(False)
            pg.event.set_grab(True)

        h_dist = eye.distance_to(look_at)
        v_dist = eye.y - look_at.y
        angle_to_target = math.atan2(v_dist, h_dist)
        self.head_pitch = angle_to_target
        
        h_dir = eye.direction_to(look_at)
        self.y_rot = math.atan2(h_dir.x, h_dir.z)

        self.slide_keys = {
            pg.K_w: Vector3D.FORWARD,
            pg.K_s: Vector3D.BACKWARD,
            pg.K_a: Vector3D.RIGHT,
            pg.K_d: Vector3D.LEFT,
            pg.K_LSHIFT: Vector3D.UP,
            pg.K_LCTRL: Vector3D.DOWN,
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
            slide_dir = slide_dir.rotate(Vector3D.UP, self.y_rot)

            offset = (slide_dir * delta * 4.)

            self.view_matrix.eye += offset

    def pitch(self, delta):
        if self.mode == FPCamera.MOUSE:
            m_delta = self.parent_app.mouse_delta
            if m_delta != Vector2D.ZERO:
                self.view_matrix.rotate_x(m_delta.y * delta * self.sensitivity)
        elif self.mode == FPCamera.KEYBOARD:
            _pitch = 0.
            if self.keys_states[pg.K_i]:
                _pitch = 1.
            elif self.keys_states[pg.K_k]:
                _pitch = -1.

            if _pitch != 0.:
                angle = math.tau / 10.
                self.view_matrix.rotate_x(_pitch * angle * delta)

    def turn(self, delta):
        angle = 0.

        if self.mode == FPCamera.MOUSE:
            m_delta = self.parent_app.mouse_delta
            if m_delta != Vector2D.ZERO:
                angle = -m_delta.x * delta * self.sensitivity
        elif self.mode == FPCamera.KEYBOARD:
            _turn = 0.
            if self.keys_states[pg.K_j]:
                _turn = 1.
            elif self.keys_states[pg.K_l]:
                _turn = -1.

            if _turn != 0.:
                angle = _turn * delta * math.tau / 10.

        if angle != 0.:
            self.view_matrix.rotate_global_y(angle)
            self.y_rot += angle

    def handle_event(self, event):
        if not (hasattr(event, 'key')):
            return

        if event.key in self.keys_states.keys():
            self.keys_states[event.key] = (event.type == pg.KEYDOWN)

