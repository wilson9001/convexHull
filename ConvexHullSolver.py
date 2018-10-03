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

    def delete_lines_and_points(self, number_to_delete_front, number_to_delete_back, points_to_trim, lines):
        points_to_delete = set()

        for i in range(number_to_delete_front):
            points_to_delete.add(points_to_trim.pop(0))

        for i in range(number_to_delete_back):
            points_to_delete.add(points_to_trim.pop())

        for line in lines:
            if line.p1() in points_to_delete or line.p2() in points_to_delete:
                del line

    def combine_hulls(self, left_points, left_hull, right_points, right_hull, side): # returns combined hull, points
        left_changed = True
        right_changed = True
        first_evaluation = True

        left_index_top, right_index_top = 0, 0

        slope_current = self.calculate_slope(left_points[left_index_top], right_points[right_index_top])

        #find new top line
        while left_changed or right_changed:
            if right_changed:
                slope_new = self.calculate_slope(left_points[(left_index_top + 1) % len(left_points)], right_points[right_index_top])
                if slope_new < slope_current:
                    slope_current = slope_new
                    left_index_top += 1
                    left_changed = True
                else:
                    left_changed = False

            if left_changed or first_evaluation:
                slope_new = self.calculate_slope(left_points[left_index_top], right_points[(right_index_top + 1) % len(right_index_top)])
                if slope_new > slope_current:
                    slope_current = slope_new
                    right_index_top += 1
                    right_changed = True
                else:
                    right_changed = False

                first_evaluation = False

        new_top_edge = QLineF(left_points[left_index_top], right_points[right_index_top])

        # Find bottom line
        left_changed = True
        right_changed = True
        first_evaluation = True
        left_index_bottom, right_index_bottom = 0, 0

        slope_current = self.calculate_slope(left_points[left_index_bottom], right_points[right_index_bottom])
        while left_changed or right_changed:
            if right_changed:
                slope_new = self.calculate_slope(left_points[(left_index_bottom - 1) % len(left_points)], right_points[right_index_bottom])
                if slope_new > slope_current:
                    slope_current = slope_new
                    left_index_bottom = ((left_index_bottom - 1) % len(left_points))
                    left_changed = True
                else:
                    left_changed = False

            if left_changed or first_evaluation:
                slope_new = self.calculate_slope(left_points[left_index_bottom], right_points[(right_index_bottom - 1) % len(right_points)])
                if slope_new < slope_current:
                    slope_current = slope_new
                    right_index_bottom = ((right_index_bottom - 1) % len(right_points))
                    right_changed = True
                else:
                    right_changed = False

                first_evaluation = False

        new_bottom_edge = QLineF(left_points[left_index_bottom], right_points[right_index_bottom])

        # Trim point arrays and delete unneeded points & associated lines.
        number_to_delete_front = abs(0 - left_index_top)
        number_to_delete_back = (len(left_points) - 1) - left_index_bottom

        self.delete_lines_and_points(number_to_delete_front, number_to_delete_back, left_points, left_hull.getLines())

        number_to_delete_front = abs(0 - right_index_top)
        number_to_delete_back = (len(right_points) - 1) - right_index_bottom

        self.delete_lines_and_points(number_to_delete_front, number_to_delete_back, right_points, right_hull.getLines())

        # Arrange trimmed arrays and fuse together
        points_to_check = {left_points[left_index_bottom], left_points[left_index_top], right_points[right_index_top], right_points[right_index_bottom]}

        combined_points = list()

        if side == side.L:
            right_most_point_index = 0
            for i in range(len(right_points)):
                if right_points[i].x() > right_points[right_most_point_index].x():
                    right_most_point_index = i

            cc_part, c_part = right_points[:right_most_point_index + 1], right_points[right_most_point_index + 1:]
            cc_part.reverse()
            c_part.reverse()

            combined_points.extend(cc_part)
            combined_points.extend(left_points)
            combined_points.extend(c_part)

        elif side == side.R:
            left_most_point_index = 0
            for i in range(len(left_points)):
                if left_points[i].x() < left_points[left_most_point_index].x():
                    left_most_point_index = i

            c_part, cc_part = left_points[:left_most_point_index + 1], left_points[left_most_point_index:]
            cc_part.reverse()
            c_part.reverse()

            combined_points.extend(c_part)
            combined_points.extend(right_points)
            combined_points.extend(cc_part)

        else:
            combined_points.extend(left_points)
            combined_points.extend(right_points)

        # Combine hull lines from individual hulls to form new hull
        combined_lines = list()
        combined_lines.extend(left_hull.getLines())
        combined_lines.extend(right_hull.getLines())

        # Check points w/ newly created lines to see if there is a third middle line to delete

        for line in combined_lines:
            if line.p1() in points_to_check or line.p2() in points_to_check:
                index_p1 = combined_points.index(line.p1())
                index_p2 = combined_points.index(line.p2())
                distance = abs(index_p1 - index_p2)
                if distance != 1 and distance != (len(combined_points) -1):
                    del line

        return [Hull(combined_lines), combined_points]


    def compute_hull(self, points, side=Side.W):  # returns hull, points
        lines = []
        completed_hull_and_points = None

        if len(points) == 2:
            lines.append(QLineF(points[0], points[1]))

            if side == Side.L:
                points.reverse()

            completed_hull_and_points = [Hull(lines), points]

        elif len(points) == 3:
            for i in range(3):
                lines.append(QLineF(points[i], points[(i + 1) % 3]))

            if side == Side.L:
                right_most_point = points.pop(2)

                points.sort(key=lambda point: self.calculate_slope(point, right_most_point))
                points.insert(0, right_most_point)
            elif side == Side.R:
                left_most_point = points.pop(0)

                points.sort(key=lambda point: self.calculate_slope(left_most_point, point), reverse=True)
                points.insert(0, left_most_point)

            completed_hull_and_points = [Hull(lines), points]
        elif len(points) > 3:
            left_points, right_points = points[:len(points)//2], points[len(points)//2:]
            left_hull_and_points = self.compute_hull(left_points, Side.L)
            right_hull_and_points = self.compute_hull(right_points, Side.R)

            completed_hull_and_points = self.combine_hulls(left_hull_and_points[1], left_hull_and_points[0], right_hull_and_points[1], right_hull_and_points[0], side)

        return completed_hull_and_points