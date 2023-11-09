from enum import Enum
from typing import Collection

from oven_engine_3D.utils.geometry import Vector3D


class BezierPoint:
    def __init__(self, position, handle):
        self.position = position
        self.__handle = handle

    @property
    def handle(self):
        return self.position + self.__handle.normalized

class BezierCurve:
    class LoopMode(Enum):
        NONE = 0
        LOOP = 1
        BOUNCE = 2

    def __init__(self, points: Collection[BezierPoint], loop_mode=LoopMode.NONE):
        assert len(points) >= 2, "A bezier curve must have at least 2 points"

        self.points = list(points)
        self.loop_mode = loop_mode
        self.__lengths = [] # [self.segment_length(i) for i in range(len(self) - 1)]
        self.current_t = 0.
        # self.direction = 1.
        self.current_segment = 0
        self.done = False

    @staticmethod
    def from_file(src_file, loop_mode=LoopMode.NONE):
        with open(src_file, "r") as f:
            lines = f.readlines()

        points = []
        for line in lines:
            if line.startswith("#"):
                continue

            data = line.split(" ")
            points.append(BezierPoint(Vector3D(*[float(x) for x in data[:3]]),
                                      Vector3D(*[float(x) for x in data[3:6]])))

        return BezierCurve(points, loop_mode)

    def __getitem__(self, item):
        return self.points[item]

    def __len__(self):
        return len(self.points)

    def interpolate_segment(self, start_idx: int, t: float):
        start = self.points[start_idx]
        end = self.points[start_idx + 1]

        p1, p2 = start.position, start.handle
        # Unless this is the first segment,
        # the start handle is the reflection of the previous end handle
        if start_idx != 0:
            p2 = 2*p1 - p2

        if t <= 0.:
            return p1, p2

        p3, p4 = end.handle, end.position
        if t >= 1.:
            return p4, p3

        t_cube = t**3
        t_square = t**2

        # Bernstein polynomials
        output = p1 * (-t_cube + 3*t_square - 3*t + 1) + \
               p2 * (3*t_cube - 6*t_square + 3*t) + \
               p3 * (-3*t_cube + 3*t_square) + \
               p4 * t_cube

        # Compute derivative
        output_deriv = (p1 * (-t_square - 2*t + 1) +
                        p2 * (3*t_square - 4*t + 1) +
                        p3 * (-3*t_square + 2*t) +
                        p4 * (3*t_square)) * 3

        return output, output_deriv.normalized

    """def add_point(self, point: BezierPoint, index: int = -1):
        if index == -1:
            self.points.append(point)
        else:
            self.points.insert(index, point)

        if index == 0:
            self.__lengths.insert(0, self.segment_length(0))
        elif index == -1:
            self.__lengths.append(self.segment_length(len(self) - 2))
        else:
            self.__lengths.insert(index, self.segment_length(index - 1))

    def remove_point(self, point_idx: [int|BezierPoint]):
        self.points.remove(point_idx)
        self.__lengths.remove(point_idx)

    def replace_point(self, point_idx: [int|BezierPoint], new_point: BezierPoint):
        self.points[point_idx] = new_point
        self.__lengths[point_idx] = self.segment_length(point_idx)"""

    def segment_length(self, start_idx: int, epsilon=.001):
        last_p = self.interpolate_segment(start_idx, 0.)
        total_dist = 0.

        for t in range(0, int(1./epsilon)):
            next_p = self.interpolate_segment(start_idx, t * epsilon)
            total_dist += (next_p - last_p).length

        return total_dist

    def reset(self):
        self.current_t = 0.
        # self.direction = 1.
        self.current_segment = 0
        self.done = False

    @property
    def last_start_idx(self):
        return len(self) - 1

    @property
    def at_beginning(self):
        return self.current_segment == 0 and self.current_t == 0.

    @property
    def at_end(self):
        return self.current_segment == self.last_start_idx and self.current_t == 1.

    def interpolate_next(self, time_delta: float):
        assert not self.done, "Bezier curve is done"
        """if self.done:
            return self.points[-1].position, self.points[-1].handle"""

        self.current_t += time_delta
        output = self.interpolate_segment(self.current_segment, self.current_t)

        # Check end of segment
        if self.current_t >= 1.:
            self.current_t = 0.
            self.current_segment += 1

        # Check end of curve
        if self.current_segment == self.last_start_idx:
            if self.loop_mode == BezierCurve.LoopMode.NONE:
                self.done = True
            else:
                self.current_segment = 0
            """if self.loop_mode == BezierCurve.LoopMode.NONE:
                self.current_t = 1.
                self.current_segment = len(self) - 2
            elif self.loop_mode == BezierCurve.LoopMode.LOOP:
                self.reset()"""

        return output