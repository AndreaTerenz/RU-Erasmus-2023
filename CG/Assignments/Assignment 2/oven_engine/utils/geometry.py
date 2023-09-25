import math

class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()

class Vector2D:
    def __init__(self, x: [tuple|float], y : [float|None] = None):
        if y is None:
            y = x
        
        if type(x) is tuple and len(x) >= 2:
            self.x, self.y = x[0], x[1]
        else:
            self.x, self.y = x, y

    @staticmethod
    def from_polar(angle: float, radius = 1.):
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        return Vector2D(x, y)

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

    def __neg__(self):
        return Vector2D(-self.x, -self.y)

    def __eq__(self, other):
        return type(other) is Vector2D and (self.x == other.x and self.y == other.y)

    def __gt__(self, other):
        return self.x > other.x and self.y > other.y

    def __lt__(self, other):
        return self.x < other.x and self.y < other.y
    
    def __abs__(self):
        return Vector2D(math.fabs(self.x), math.fabs(self.y))

    def __bool__(self):
        return self.length_sq > 0.

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

    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __truediv__(self, other):
        if type(other) in [int, float]:
            other = Vector2D(other, other)

        if type(other) is Vector2D:
            return Vector2D(self.x / other.x, self.y / other.y)

        return self
    
    def __pow__(self, exponent):
        return Vector2D(self.x**exponent, self.y**exponent)
    
    def __floor__(self):
        return self.map(math.floor)

    def __ceil__(self):
        return self.map(math.ceil)
    
    def __round__(self, n):
        return self.map(round, n)
    
    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y

        raise IndexError

    def __iter__(self):
        yield self.x
        yield self.y

    @property
    def length_sq(self):
        return self.x**2 + self.y**2

    @property
    def length(self):
        return math.sqrt(self.length_sq)

    @property
    def angle(self):
        return math.atan2(self.y, self.x)

    @property
    def normalized(self):
        return self.scale_to_length(1.)

    @property
    def is_normalized(self):
        return self.length_sq == 1.

    @property
    def aspect_ratio(self):
        return self.x / self.y

    @property
    def orthogonal(self):
        return self.rotated(math.tau/4.)

    def snap(self, step: float):
        def s(v, st):
            return round(v/st)*st

        return self.map(s, step)

    def map(self, f, *args, **kwargs):
        return Vector2D(f(self.x, *args, **kwargs), f(self.y, *args, **kwargs))
    
    def scale_to_length(self, target_len):
        l = self.length
        if l == 0.0:
            return self

        return self * (target_len / l)

    def reshape_with_ratio(self, amount: float):
        output = Vector2D(0.)

        if self.x < self.y:
            output.x = amount
            output.y = amount * self.aspect_ratio
        else:
            output.y = amount
            output.x = amount * self.aspect_ratio

        return output

    def clamp_length(self, target_len):
        l = self.length_sq

        if l <= target_len ** 2:
            return self
        
        return self.scale_to_length(target_len)

    def clamped(self, min_value, max_value):
        """
        Clamp vector components
        """

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
        return self.x * other.x + self.y * other.y
    
    def cross(self, other):
        """
        This is the signed area of the parallelogram formed by the two vectors.
        If the second vector is clockwise from the first vector, then
        the cross product is the positive area. If counter-clockwise,
        the cross product is the negative area.
        """

        return self.x * other.y - self.y * other.x
    
    def distance_sq_to(self, other: 'Vector2D'):
        return (self - other).length_sq
    
    def distance_to(self, other: 'Vector2D'):
        return math.sqrt(self.distance_sq_to(other))
    
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
    
    def lin_interpolate(self, target: 'Vector2D', weight: float):
        weight = min(1., max(0., weight))

        return target * weight + self * (1. - weight)

    def projected(self, other: 'Vector2D'):
        dot_p = self.dot(other)
        return other.scale_to_length(dot_p / other.length)

    def reflected(self, normal_vec):
        normal_vec = normal_vec.normalized

        return self - 2 * self.dot(normal_vec) * normal_vec
    
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
