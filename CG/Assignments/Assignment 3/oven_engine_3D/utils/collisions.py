from oven_engine_3D.utils.geometry import Vector2D


class LineCollider:
    def __init__(self, pA: Vector2D, pB: Vector2D):
        self.pointA = pA
        self.pointB = pB

    @property
    def direction(self):
        return (self.pointB - self.pointA).normalized

    @property
    def normal(self):
        return self.direction.orthogonal

    @property
    def length(self):
        return (self.pointB - self.pointA).length

    def distance_to(self, point: Vector2D):
        return abs(self.normal.dot(point - self.pointA))

    def __str__(self):
        return f"LineCollider({self.pointA}, {self.pointB})"

    def __repr__(self):
        return str(self)