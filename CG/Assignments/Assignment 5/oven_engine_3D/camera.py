import math

import numpy as np
import pygame as pg

from oven_engine_3D.entities import Entity
from oven_engine_3D.utils.geometry import Vector3D
from oven_engine_3D.utils.matrices import ProjectionMatrix, ViewMatrix


class Camera(Entity):

    def __init__(self, parent_app,
                 eye = Vector3D.ZERO, look_at = Vector3D.FORWARD, up_vec=Vector3D.UP,
                 fov =math.tau / 8., ratio =16. / 9., near=.5, far=100, local_look_at=False):
        super().__init__(parent_app, origin=eye)

        self.projection_matrix = ProjectionMatrix.perspective(fov, ratio, near=near, far=far)
        self.view_matrix = ViewMatrix()

        look_at = eye + look_at if local_look_at else self.to_global(look_at)

        self.look_at(look_at, up_vec)

    def _update(self, delta):
        pass

    def handle_event(self, ev):
        pass

    def look_at(self, target, up=Vector3D.UP, new_origin = None):
        if new_origin is not None:
            self.origin = new_origin

        self.view_matrix.look_at(self.origin, target, up)

    def slide(self, offset):
        self.view_matrix.slide(*offset)

    def move_to(self, pos):
        self.view_matrix.eye = pos

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
    def __init__(self, parent_app, sensitivity=50.,
                 eye=Vector3D.ZERO, look_at=Vector3D.FORWARD, up_vec=Vector3D.UP, speed=5.,
                 fov=math.tau / 8., ratio=16. / 9., near=.5, far=100):
        super().__init__(parent_app, eye, look_at, up_vec, fov, ratio, near, far)

        self.sensitivity = sensitivity
        self.speed = speed

        pg.mouse.set_visible(False)
        pg.event.set_grab(True)

        h_dist = eye.distance_to(look_at)
        v_dist = eye.y - look_at.y
        angle_to_target = math.atan2(v_dist, h_dist)
        self.head_pitch = angle_to_target

        h_dir = eye.direction_to(look_at)
        self.y_rot = math.atan2(h_dir.x, h_dir.z)

        self.pitch_angle = 0.

        self.slide_keys = {
            pg.K_w: Vector3D.FORWARD,
            pg.K_s: Vector3D.BACKWARD,
            pg.K_a: Vector3D.RIGHT,
            pg.K_d: Vector3D.LEFT,
            pg.K_LSHIFT: Vector3D.UP,
            pg.K_LCTRL: Vector3D.DOWN,
        }

        parent_app.add_keys(self.slide_keys.keys())

    def _update(self, delta):
        self.move(delta)
        self.pitch(delta)
        self.turn(delta)

    def translate(self, offset: Vector3D):
        super().translate(offset)
        self.view_matrix.eye += offset

        return self

    def move(self, delta):
        slide_dir = Vector3D.ZERO
        for key, _dir in self.slide_keys.items():
            state = self.parent_app.is_key_pressed(key)
            fact = 1. if state else 0.
            slide_dir += _dir * fact

            if fact != 0.:
                pass

        slide_dir = slide_dir.normalized

        if slide_dir != Vector3D.ZERO:
            slide_dir = slide_dir.rotate(Vector3D.UP, self.y_rot).normalized
            slide_offset = slide_dir * delta * self.speed

            self.translate(slide_offset)

    def pitch(self, delta):
        m_delta = self.parent_app.mouse_delta
        if m_delta.y == 0.:
            return

        angle = m_delta.y * self.sensitivity * delta

        self.view_matrix.rotate_x(angle)

    def turn(self, delta):
        m_delta = self.parent_app.mouse_delta
        if m_delta.x == 0.:
            return

        angle = -m_delta.x * delta * self.sensitivity

        self.view_matrix.rotate_global_y(angle)
        self.y_rot += angle

    def handle_event(self, event):
        pass

