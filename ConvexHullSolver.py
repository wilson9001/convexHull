from operator import methodcaller
from enum import Enum, auto
from Hull import Hull

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF, QThread, pyqtSignal
elif PYQT_VER == 'PYQT4':
    from PyQt4.QtCore import QLineF, QPointF, QThread, pyqtSignal
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

class Side(Enum):
    L = auto()
    R = auto()
    W = auto()

class ConvexHullSolver:

    def sort_points_by_x(self, points):
        points.sort(key=methodcaller('x'))

    def calculate_slope(self, left_point, right_point):
        rise = right_point.y - left_point.y
        run = right_point.x - left_point.x

        return rise / run

    def combine_hulls(self, left_points, left_hull, right_points, right_hull, side):
        left_changed = True
        right_changed = True
        first_evaluation = True

        left_index, right_index = 0, 0

        slope_current = self.calculate_slope(left_points[0], right_points[0])

        #find new top line
        while left_changed or right_changed:
            if right_changed:
                slope_new = self.calculate_slope(left_points[left_index+1], right_points[right_index])
                if(slope_new < slope_current):
                    slope_current = slope_new
                    left_index += 1
                    left_changed = True
                else:
                    left_changed = False

            if left_changed or first_evaluation:
                slope_new = self.calculate_slope(left_points[left_index], right_points[right_index])
                if slope_new > slope_current:
                    slope_current = slope_new
                    right_index += 1
                    right_changed = True
                else:
                    right_changed = False

            first_evaluation = False

        new_top_edge = QLineF(left_points[left_index], right_points[right_index])

        #TODO: Find bottom line and then combine hulls

        return Hull()

    def compute_hull(self, points, side=Side.W):  # returns hull, points
        lines = []
        completed_hull = None

        if len(points == 2):
            lines.append(QLineF(points[0], points[1]))

            if side == Side.L:
                points.reverse()

            completed_hull = Hull(lines)

        elif len(points) == 3:
            for i in range(3):
                lines.append(QLineF(points[i], points[i+1 % 3]))

            if side == Side.L:
                right_most_point = points.pop(points[2])

                points.sort(key=lambda point: self.calculate_slope(point, right_most_point))
                points.insert(0, right_most_point)
            elif side == Side.R:
                left_most_point = points.pop(points[0])

                points.sort(key=lambda point: self.calculate_slope(left_most_point, point), reverse=True)
                points.insert(0, left_most_point)

            completed_hull = Hull(lines)
        elif len(points) > 3:
            left_points, right_points = points[:len(points)//2], points[len(points)//2:]
            left_hull = self.compute_hull(left_points, Side.L)
            right_hull = self.compute_hull(right_points, Side.R)

            completed_hull = self.combine_hulls(left_points, left_hull, right_points, right_hull)

        return completed_hull