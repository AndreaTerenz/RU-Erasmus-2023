from abc import ABC
from enum import Enum
from functools import reduce
from typing import Union

from shortuuid import uuid

# from oven_engine.entities import Entity
from .geometry import Vector2D


class CollisionMode(Enum):
    ENABLED = 1,
    RECEIVE_ONLY = 0,
    DISABLED = -1

class Collision:
    def __init__(self, collA: 'Collider', collB: Union['Collider', None], norm: Vector2D):
        self.collA = collA
        self.entityA = collA.parent_entity
        self.collB = collB
        self.entityB = collB.parent_entity if not collB is None else None
        self.normal = norm

class CollisionManager:
    def __init__(self, world_bounds: Union['AABB', None] = None):
        self.colliders = []
        self.last_collisions = []
        self.enabled = True
        self.world_bounds = world_bounds

        """if world_bounds is not None:
            # Add 4 AABB colliders to simulate world bounds
            width = world_bounds.size.x
            height = world_bounds.size.y
            self.add_collider(AABBCollider(Vector2D(width, 1.), None, offset=Vector2D(0., height)))
            self.add_collider(AABBCollider(Vector2D(width, 1.), None, offset=Vector2D(0., -1.)))
            self.add_collider(AABBCollider(Vector2D(1., height), None, offset=Vector2D(width, 0.)))
            self.add_collider(AABBCollider(Vector2D(1., height), None, offset=Vector2D(-1., 0.)))"""

    def add_collider(self, collider: 'Collider'):
        self.colliders.append(collider)

    def update_collisions(self):
        if not self.enabled or len(self.colliders) < 2:
            return []

        self.last_collisions = []
        checked = 0

        #TODO: There are definetely fancier and faster ways to check collisions
        for c in self.colliders:
            if c.mode != CollisionMode.ENABLED:
                continue

            if not self.world_bounds is None:
                #TODO: do this with actual AABBCollider(s)
                u = self.world_bounds.union_with(c.aabb)
                if u != self.world_bounds:
                    norm = self.world_bounds.closest_side_normal(c.position)
                    self.last_collisions.append(Collision(c, None, norm))

            others = [o for o in self.colliders if
                        o != c and
                        o.mode != CollisionMode.DISABLED and
                        not (c.mode == CollisionMode.RECEIVE_ONLY and o.mode == CollisionMode.RECEIVE_ONLY)]

            for o in others:
                norm = self.check_collisions_for(c, o)
                checked += 1

                if norm is None:
                    continue

                if c.mode == CollisionMode.ENABLED:
                    self.last_collisions.append(Collision(c, o, norm))
                if o.mode == CollisionMode.ENABLED:
                    self.last_collisions.append(Collision(o, c, -norm))

    def check_collisions_for(self, collA: 'Collider', collB: 'Collider'):
        if type(collA) is CircleCollider:
            if type(collB) is CircleCollider:
                return circle_circle_collision(collA.position, collA.radius, collB.position, collB.radius)
            elif type(collB) is AABBCollider:
                return aabb_circle_collision(collB.aabb, collA.position, collA.radius)
            """elif type(collB) is LineCollider:
                return circle_line_collision(collA.position, collA.radius, collB.point1, collB.point2)"""
        elif type(collA) is AABBCollider:
            if type(collB) is AABBCollider:
                return aabb_aabb_collision(collA.aabb, collB.aabb)
            """
            elif type(collB) is LineCollider:
                return aabb_line_collision(collA.aabb, collB.point1, collB.point2)
        elif type(collA) is LineCollider and type(collB) is LineCollider:
                return line_line_collision(collA.point1, collA.point2, collB.point1, collB.point2)
        """
        return self.check_collisions_for(collB, collA)

    def last_collisions_for(self, entity):
        return [c for c in self.last_collisions if c.entityA == entity]

    def total_collision_normal(self, entity):
        colls = self.last_collisions_for(entity)
        return reduce(lambda a, b: a + b.normal, colls, Vector2D.ZERO).normalized

class Collider(ABC):
    def __init__(self, parent_entity, _id=None, offset=Vector2D.ZERO):
        self.parent_entity = parent_entity
        self.id = _id if not _id is None else uuid()
        self.offset = offset

    @property
    def position(self):
        return self.offset + (self.parent_entity.position if not self.parent_entity is None else Vector2D.ZERO)

    @property
    def mode(self):
        return self.parent_entity.collision_mode if not self.parent_entity is None else CollisionMode.ENABLED

    @property
    def aabb(self):
        return self.parent_entity.aabb  if not self.parent_entity is None else None

    def __eq__(self, other):
        return self.id == other.id

    def handle_collision(self, other: 'Collider', data: list):
        self.parent_entity.handle_collision(other.parent_entity, data)

class CircleCollider(Collider):
    def __init__(self, radius, parent_entity, offset=Vector2D.ZERO):
        super().__init__(parent_entity=parent_entity, offset=offset)
        self.radius = radius

    @property
    def aabb(self):
        return AABB.from_circle(self.position, self.radius)

class AABBCollider(Collider):
    def __init__(self, size: Vector2D, parent_entity, offset=Vector2D.ZERO):
        super().__init__(parent_entity=parent_entity, offset=offset)
        self.tl = -(size/2.)
        self.size = size

    @staticmethod
    def fromAABB(aabb: 'AABB', parent_entity):
        return AABBCollider(aabb.size, parent_entity, offset=aabb.tl)

    @property
    def aabb(self):
        return AABB.at_origin(self.size).move_to(self.position, move_center=True)

class LineCollider(Collider):
    def __init__(self, point1: Vector2D, point2: Vector2D, parent_entity, offset=Vector2D.ZERO):
        super().__init__(parent_entity=parent_entity, offset=offset)

        mid_point = (point1 + point2) / 2.
        point1 -= mid_point
        point2 -= mid_point

        self.point1 = point1
        self.point2 = point2

    @property
    def aabb(self):
        return AABB.from_line(self.point1, self.point2).move_to(self.position, move_center=True)


class AABB:
    """
    Axis Aligned Bounding Box
    """

    TOP_SIDE = 0
    LEFT_SIDE = 1
    BOTTOM_SIDE = 2
    RIGHT_SIDE = 3

    def __init__(self, tl: Vector2D, size: [Vector2D|float], flipped_normals=False):
        self.tl = tl

        if type(size) is float:
            self.size = Vector2D(size)
        else:
            self.size = size

        self.flipped_normals = flipped_normals

    @staticmethod
    def from_circle(center:Vector2D, radius:float):
        return AABB(center - Vector2D(radius), radius * 2)

    @staticmethod
    def from_line(point1: Vector2D, point2: Vector2D):
        tl = Vector2D(min(point1.x, point2.x), min(point1.y, point2.y))
        br = Vector2D(max(point1.x, point2.x), max(point1.y, point2.y))
        return AABB(tl, br - tl)

    @staticmethod
    def at_origin(size: [Vector2D|float]):
        return AABB(Vector2D(0.), size)

    @property
    def br(self):
        return self.tl + self.size

    @property
    def bl(self):
        return Vector2D(self.tl.x, self.tl.y + self.size.y)

    @property
    def tr(self):
        return Vector2D(self.tl.x + self.size.x, self.tl.y)

    @property
    def center(self):
        return self.tl + self.size/2.

    @property
    def area(self):
        return self.size.x * self.size.y

    @property
    def diagonal(self):
        return self.size.length

    @property
    def centered(self):
        """
        Return an AABB of the same size but centered on the origin
        """

        return AABB(self.size / -2., self.size)

    def __str__(self) -> str:
        return f"({self.tl}, {self.size})"
    
    def __eq__(self, other):
        return type(other) is AABB and (self.tl == other.tl and self.size == other.size)
    
    def __bool__(self):
        return self.size.x > 0. and self.size.y > 0.
    
    def move_by(self, offset:Vector2D):
        return AABB(self.tl + offset, self.size)

    def move_to(self, dest:Vector2D, move_center=False):
        if move_center:
            offset = dest - self.center
        else:
            offset = dest - self.tl

        return self.move_by(offset)

    def expand_to(self, point:Vector2D):
        """
        Expand the AABB to include the given point
        """
        if aabb_has_point(self, point):
            return self

        if type(point) is Vector2D:
            tl = Vector2D(min(self.tl.x, point.x), min(self.tl.y, point.y))
            br = Vector2D(max(self.br.x, point.x), max(self.br.y, point.y))
            return AABB(tl, br - tl)

        return self
    
    def union_with(self, other: 'AABB'):
        if type(other) is AABB:
            tl = Vector2D(min(self.tl.x, other.tl.x), min(self.tl.y, other.tl.y))
            br = Vector2D(max(self.br.x, other.br.x), max(self.br.y, other.br.y))
            return AABB(tl, br - tl)
        
        return self
    
    def intersection_with(self, other: 'AABB'):
        if type(other) is AABB:
            tl = Vector2D(max(self.tl.x, other.tl.x), max(self.tl.y, other.tl.y))
            br = Vector2D(min(self.br.x, other.br.x), min(self.br.y, other.br.y))

            if tl.x > br.x or tl.y > br.y:
                return None

            return AABB(tl, br - tl)
        
        return self

    def point_closest_to(self, point: Vector2D):
        if type(point) is Vector2D:
            half_size = self.size / 2.
            diff = self.center - point
            closest = diff.clamped(-half_size, half_size)

            return closest + self.center

        return self

    def distance_to_side(self, point: Vector2D, side: int):
        if type(point) is Vector2D:
            if side == AABB.TOP_SIDE:
                return point.y - self.tl.y
            elif side == AABB.LEFT_SIDE:
                return point.x - self.tl.x
            elif side == AABB.BOTTOM_SIDE:
                return self.br.y - point.y
            elif side == AABB.RIGHT_SIDE:
                return self.br.x - point.x

        return 0.

    def closest_sides(self, point: Vector2D):
        """
        Return the closest side of the AABB to the given point
        """
        if type(point) is Vector2D:
            if point == self.center:
                return [AABB.TOP_SIDE, AABB.BOTTOM_SIDE, AABB.LEFT_SIDE, AABB.RIGHT_SIDE]

            dist_top = self.distance_to_side(point, AABB.TOP_SIDE)
            dist_bottom = self.distance_to_side(point, AABB.BOTTOM_SIDE)
            dist_right = self.distance_to_side(point, AABB.RIGHT_SIDE)
            dist_left = self.distance_to_side(point, AABB.LEFT_SIDE)

            min_dist = min(dist_top, dist_bottom, dist_right, dist_left)
            output = []

            if min_dist == dist_top:
                output += [AABB.TOP_SIDE]
            if min_dist == dist_bottom:
                output += [AABB.BOTTOM_SIDE]
            if min_dist == dist_right:
                output += [AABB.RIGHT_SIDE]
            if min_dist == dist_left:
                output += [AABB.LEFT_SIDE]

            return output

        return -1

    def is_point_on_perimeter(self, p:Vector2D):
        return (p.x == self.tl.x or p.x == self.br.x) or (p.y == self.tl.y or p.y == self.br.y)

    def closest_side_along_dir(self, point: Vector2D, direction: Vector2D):
        """
        Return the closest side of the AABB to the given point along the given direction
        """
        direction = direction.normalized

        dir_tl = direction.dot((point - self.tl).normalized)
        dir_bl = direction.dot((point - self.bl).normalized)
        dir_tr = direction.dot((point - self.tr).normalized)
        dir_br = direction.dot((point - self.br).normalized)

        if dir_tl > dir_bl:
            if dir_tl > dir_tr:
                if dir_tl > dir_br:
                    return AABB.TOP_SIDE
                else:
                    return AABB.RIGHT_SIDE
            else:
                if dir_tr > dir_br:
                    return AABB.RIGHT_SIDE
                else:
                    return AABB.BOTTOM_SIDE

    def side_normal(self, side_id: int):
        output = Vector2D.ZERO

        match side_id:
            case AABB.TOP_SIDE:
                output = Vector2D.UP
            case AABB.LEFT_SIDE:
                output = Vector2D.LEFT
            case AABB.BOTTOM_SIDE:
                output = Vector2D.DOWN
            case AABB.RIGHT_SIDE:
                output = Vector2D.RIGHT

        if self.flipped_normals:
            output *= -1.

        return output

    def closest_side_normal(self, point: Vector2D):
        closest = self.closest_sides(point)
        return self.side_normal(closest[0])

    def normal_at_point(self, p: Vector2D):
        if not self.is_point_on_perimeter(p):
            p = self.point_closest_to(p)

        closest = self.closest_sides(p)
        output = Vector2D(0.)

        for c in closest:
            output += self.side_normal(c)

        return output.normalized

def aabb_has_point(box:AABB, point:Vector2D):
    return type(point) is Vector2D and box.tl.x <= point.x <= box.br.x and box.tl.y <= point.y <= box.br.y

def circle_has_point(center:Vector2D, radius:float, point:Vector2D):
    return center.distance_sq_to(point) <= (radius ** 2)
"""
def line_has_point(point1:Vector2D, point2:Vector2D, point:Vector2D, epsilon = 0.001):
    # first check if the point is inside the line's AABB
    if not aabb_has_point(AABB.from_line(point1, point2), point):
        return False

    dot_p1p = (point1 - point).dot(point2 - point)

    # The point is on the line if the dot product of the vectors from the point to the line's ends is -1
    return abs(-1. - dot_p1p) <= epsilon
"""
def aabb_aabb_collision(box1: AABB, box2: AABB):
    inters = box1.intersection_with(box2)
    if inters is None:
        return None

    closest_side = box1.closest_sides(inters.center)[0]
    closest_norm = box1.side_normal(closest_side)

    return closest_norm
"""
def aabb_line_collision(box:AABB, point1:Vector2D, point2:Vector2D):
    # first check if the box intersects with the line's AABB
    if aabb_aabb_collision(box, AABB.from_line(point1, point2)) is None:
        return False

    if aabb_has_point(box, point1) or aabb_has_point(box, point2):
        return True

    # The box contains the line if the distance of the center from the line
    # is less than half the diagonal of the box
    half_diag = box.diagonal / 2.
    dist_to_segment = box.center.point_line_distance(point1, point2)

    return dist_to_segment <= half_diag
"""
def aabb_circle_collision(box:AABB, center:Vector2D, radius:float):
    intr_box = aabb_aabb_collision(box, AABB.from_circle(center, radius))
    if intr_box is None:
        return None

    has_center = aabb_has_point(box, center)
    if not has_center:
        testX, testY = center.x, center.y

        if center.x < box.tl.x:
            testX = box.tl.x
        elif center.x > box.br.x:
            testX = box.br.x

        if center.y < box.tl.y:
            testY = box.tl.y
        elif center.y > box.br.y:
            testY = box.br.y

        distance = (center - Vector2D(testX, testY)).length

        if distance > radius:
            return None

    closest_side = box.closest_sides(center)[0]
    closest_norm = box.side_normal(closest_side)

    return closest_norm

def circle_circle_collision(center1:Vector2D, radius1:float, center2:Vector2D, radius2:float):
    dist_sq = center1.distance_sq_to(center2)
    radius_sum = radius1 + radius2

    if dist_sq > (radius_sum ** 2):
        return None

    norm = (center2 - center1).normalized

    return norm
"""
def circle_line_collision(center:Vector2D, radius:float, point1:Vector2D, point2:Vector2D):
    dist_to_segment = center.point_line_distance(point1, point2)

    return dist_to_segment <= radius

def line_line_collision(p1: Vector2D, p2: Vector2D, p3: Vector2D, p4: Vector2D):
    d1 = p2 - p1
    d2 = p4 - p3
    p1p3 = p3 - p1
    d1_x_d2 = d1.cross(d2)

    if d1_x_d2 == 0.:
        t0 = (p3 - p1).dot(d1) / d1.dot(d1)
        t1 = t0 + (d2.dot(d1) / d1.dot(d1))

        if d1.dot(d2) < 0.:
            t0, t1 = t1, t0

        # Check if they are collinear and overlapping
        if (t0 <= 0. <= t1) or (t0 <= 1. <= t1):
            return True

        return False

    t = p1p3.cross(d2) / d1_x_d2
    u = p1p3.cross(d1) / d1_x_d2

    return (d1_x_d2 != 0.) and (0. <= t <= 1.) and (0. <= u <= 1.)
"""
###############


