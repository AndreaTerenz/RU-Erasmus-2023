import math
from abc import ABC, abstractmethod
from typing import Self


class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()

class AbstractVector(ABC):
    def __init__(self, components : list):
        self.components = components

    @property
    def components_count(self) -> int:
        return len(self.components)

    def __neg__(self) -> Self:
        return self.__class__.from_values([-c for c in self.components])

    def __eq__(self, other):
        if type(other) != type(self):
            return False

        return all([a == b for a, b in zip(self.components, other.components)])

    def __gt__(self, other):
        if type(other) != type(self):
            return False

        return all([a > b for a, b in zip(self.components, other.components)])

    def __lt__(self, other):
        if type(other) != type(self):
            return False

        return all([a < b for a, b in zip(self.components, other.components)])

    def __str__(self) -> str:
        return f"({', '.join([str(c) for c in self.components])})"

    def __repr__(self) -> str:
        return f"({', '.join([str(c) for c in self.components])})"

    def __getitem__(self, item):
        return self.components[item]

    def __iter__(self):
        for comp in self.components:
            yield comp

    def __abs__(self):
        return self.from_values([math.fabs(c) for c in self.components])

    @property
    def length_sq(self):
        return sum([c**2 for c in self.components])

    @property
    def length(self):
        return math.sqrt(self.length_sq)

    def __bool__(self):
        return self.length_sq > 0.

    def __add__(self, other):
        if type(other) in [int, float]:
            other = self.from_values([other for _ in range(self.components_count)])

        if type(other) == type(self):
            return self.from_values([a + b for a, b in zip(self.components, other.components)])

        return self

    def __sub__(self, other):
        return self + (other * -1.)

    def __mul__(self, other):
        if type(other) in [int, float]:
            other = self.from_values([other for _ in range(self.components_count)])

        if type(other) == type(self):
            return self.from_values([a * b for a, b in zip(self.components, other.components)])

        return self

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if type(other) in [int, float]:
            other = self.from_values([other for _ in range(self.components_count)])

        if type(other) is Vector2D:
            return self.from_values([a / b for a, b in zip(self.components, other.components)])

        return self

    def __pow__(self, exponent):
        return self.from_values([c**exponent for c in self.components])

    def map(self, f, *args, **kwargs):
        return self.from_values([f(c, *args, **kwargs) for c in self.components])

    def __floor__(self):
        return self.map(math.floor)

    def __ceil__(self):
        return self.map(math.ceil)

    def __round__(self, n):
        return self.map(round, n)

    def snap(self, step: float):
        def s(v, st):
            return round(v/st)*st

        return self.map(s, step)


    @property
    def normalized(self):
        return self.scale_to_length(1.)

    @property
    def is_normalized(self):
        return self.length_sq == 1.

    def scale_to_length(self, target_len):
        l = self.length
        if l == 0.0:
            return self

        return self * (target_len / l)

    def clamp_length(self, target_len):
        l = self.length_sq

        if l <= target_len ** 2:
            return self

        return self.scale_to_length(target_len)

    def clamped(self, min_value, max_value):
        if type(min_value) in [int, float]:
            min_value = Vector2D(min_value, min_value)
        if type(max_value) in [int, float]:
            max_value = Vector2D(max_value, max_value)

        x = min(max_value.x, max(min_value.x, self.x))
        y = min(max_value.y, max(min_value.y, self.y))

        return Vector2D(x, y)

    def is_longer_than(self, other):
        return self.length_sq > other.length_sq

    def dot(self, other):
        return sum([a * b for a, b in zip(self.components, other.components)])

    def distance_sq_to(self, other: Self):
        return (self - other).length_sq

    def distance_to(self, other: Self):
        return math.sqrt(self.distance_sq_to(other))

    def lin_interpolate(self, target: Self, weight: float):
        weight = min(1., max(0., weight))

        return target * weight + self * (1. - weight)

    def projected(self, other: Self):
        dot_p = self.dot(other)
        return other.scale_to_length(dot_p / other.length)

    def reflected(self, normal_vec):
        normal_vec = normal_vec.normalized

        return self - 2 * self.dot(normal_vec) * normal_vec

    @staticmethod
    @abstractmethod
    def from_values(values : list) -> Self:
        return None

    @abstractmethod
    def cross(self, other):
        return None

class Vector2D(AbstractVector):

    def __init__(self, x: [tuple|float], y : [float|None] = None):
        if y is None:
            y = x
        
        if type(x) is tuple and len(x) >= 2:
            self.x, self.y = x[0], x[1]
        else:
            self.x, self.y = x, y

        super().__init__([self.x, self.y])

    @staticmethod
    def from_polar(angle: float, radius = 1.):
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        return Vector2D(x, y)

    @staticmethod
    def from_values(values : list):
        if len(values) >= 2:
            return Vector2D(values[0], values[1])
        else:
            return Vector2D(values[0])

    @classproperty
    def ONE(self):
        return Vector2D(1.)
    @classproperty
    def ZERO(self):
        return Vector2D(0.)
    @classproperty
    def UP(self):
        return Vector2D(0., 1.)
    @classproperty
    def DOWN(self):
        return Vector2D(0., -1.)
    @classproperty
    def LEFT(self):
        return Vector2D(-1., 0.)
    @classproperty
    def RIGHT(self):
        return Vector2D(1., 0.)
    @classproperty
    def UP_LEFT(self):
        return Vector2D(-1., 1.) * math.sqrt(.5)
    @classproperty
    def UP_RIGHT(self):
        return Vector2D(1., 1.) * math.sqrt(.5)
    @classproperty
    def DOWN_LEFT(self):
        return Vector2D(-1., -1.) * math.sqrt(.5)
    @classproperty
    def DOWN_RIGHT(self):
        return Vector2D(1., -1.) * math.sqrt(.5)

    @property
    def aspect_ratio(self):
        return self.x / self.y

    @property
    def orthogonal(self):
        return self.rotated(math.tau/4.)

    def reshape_with_ratio(self, amount: float):
        output = Vector2D(0.)

        if self.x < self.y:
            output.x = amount
            output.y = amount * self.aspect_ratio
        else:
            output.y = amount
            output.x = amount * self.aspect_ratio

        return output
    
    def cross(self, other):
        """
        This is the signed area of the parallelogram formed by the two vectors.
        If the second vector is clockwise from the first vector, then
        the cross product is the positive area. If counter-clockwise,
        the cross product is the negative area.
        """

        return self.x * other.y - self.y * other.x
    
    def angle_with(self, other):
        cos_angle = self.dot(other) / (self.length * other.length)

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
    
    def point_line_distance(self, p1:'Vector2D', p2:'Vector2D'):
        if p1 == p2:
            return self.distance_to(p1)

        p1p2 = p2 - p1
        p1s  = self - p1

        len_p1p2 = p1p2.length
        tmp = p1p2.dot(p1s)

        return abs(tmp) / len_p1p2
    
    def point_line_projection(self, p1:'Vector2D', p2:'Vector2D'):
        if p1 == p2:
            return self

        a = p2.x - p1.x
        b = p2.y - p1.y
        line_dist = self.point_line_distance(p1, p2)

        return Vector2D(a*line_dist, b*line_dist)

class Vector3D(AbstractVector):

    def __init__(self, x: [tuple|float], y : [float|None] = None, z : [float|None] = None):
        if y is None:
            y = x
        if z is None:
            z = x

        if type(x) is tuple and len(x) >= 3:
            self.x, self.y, self.z = x[0], x[1], x[2]
        else:
            self.x, self.y, self.z = x, y, z

        super().__init__([self.x, self.y, self.z])

    def __getattribute__(self, item: str):
        if len(item) == 2:
            comps = {
                "x": self.x,
                "y": self.y,
                "z": self.z
            }

            if item[0] in comps and item[1] in comps:
                return Vector2D(comps[item[0]], comps[item[1]])

        return super().__getattribute__(item)

    @staticmethod
    def from_Vector2D(vec: Vector2D):
        return Vector3D(vec.x, vec.y, 0.)

    @classproperty
    def ONE(self):
        return Vector3D(1.)

    @classproperty
    def ZERO(self):
        return Vector3D(0.)

    @classproperty
    def UP(self):
        return Vector3D(0., 1., 0.)

    @classproperty
    def DOWN(self):
        return Vector3D(0., -1., 0.)

    @classproperty
    def LEFT(self):
        return Vector3D(-1., 0., 0.)

    @classproperty
    def RIGHT(self):
        return Vector3D(1., 0., 0.)

    @classproperty
    def FORWARD(self):
        return Vector3D(0., 0., 1.)

    @classproperty
    def BACKWARD(self):
        return Vector3D(0., 0., -1.)

    @staticmethod
    def from_values(values: list) -> Self:
        return Vector3D(values[0], values[1], values[2])

    @staticmethod
    def from_spherical(theta: float, phi: float, radius=1.):
        x = radius * math.sin(phi) * math.cos(theta)
        y = radius * math.sin(phi) * math.sin(theta)
        z = radius * math.cos(phi)

        return Vector3D(x, y, z)

    @staticmethod
    def to_spherical(vec: 'Vector3D'):
        r = vec.length
        theta = math.atan2(vec.y, vec.x)
        phi = math.acos(vec.z / r)

        return theta, phi, r

    @staticmethod
    def from_cylindrical(theta: float, radius: float, height: float):
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)

        return Vector3D(x, y, height)

    @staticmethod
    def to_cylindrical(vec: 'Vector3D'):
        r = vec.length
        theta = math.atan2(vec.y, vec.x)
        h = vec.z

        return theta, r, h

    def cross(self, other):
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def distance_to_plane(self, plane_normal: 'Vector3D', plane_point: 'Vector3D'):
        return abs(self.dot(plane_normal) - plane_point.dot(plane_normal))

    def project_on_plane(self, plane_normal: 'Vector3D'):
        plane_normal = plane_normal.normalized
        return self - self.dot(plane_normal) * plane_normal


if __name__ == '__main__':
    v = Vector2D(-10, 10)
    q = Vector2D(10, -20)
    print(v)
    print(v.is_normalized)
    print(abs(v))
    print(v.lin_interpolate(q, .1))
    print(Vector2D.from_polar(math.tau/8., 1.))
    print(Vector2D.ONE)

    print(v + q)

    a = Vector3D(1., 2., 3.)
    b = Vector3D(4., 5., 6.)

    print(a+b)
    print(a.xy)
    print(b.zy)