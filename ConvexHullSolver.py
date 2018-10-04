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

    # O(n log n)
    def sort_points_by_x(self, points):
        points.sort(key=methodcaller('x'))

    # O(1)
    def calculate_slope(self, left_point, right_point):
        rise = right_point.y() - left_point.y()
        run = right_point.x() - left_point.x()

        return rise / run

        # O(n/2) + O(3n/4) = O(3n/4) = O(n)
    def delete_points_and_lines(self, points, top_index, bottom_index, lines, convex_hull):
        bottom_point = points[bottom_index]
        points_to_delete = list()

        index = (top_index - 1) % len(points)

        # O(n/2) = O(n)
        while points[index] != bottom_point:
            points_to_delete.append(points.pop(index))
            index = (index - 1) % len(points)

        i = 0

        # O(3n/4) = O(n)
        while i < len(lines):
            if lines[i].p1() in points_to_delete or lines[i].p2() in points_to_delete:
                if convex_hull.pause:
                    convex_hull.erase_hull.emit([lines[i]])
                lines.pop(i)
            else:
                i += 1

    # O(n^2)
    def combine_hulls(self, left_points, left_hull, right_points, right_hull, side, convex_hull): # returns combined hull, points
        left_changed = True
        right_changed = True

        left_index_top, right_index_top = 0, 0

        # O(1)
        current_new_line = QLineF(left_points[left_index_top], right_points[right_index_top])
        if convex_hull.pause:
            convex_hull.show_hull.emit([current_new_line], (0, 255, 0))
        slope_current = self.calculate_slope(current_new_line.p1(), current_new_line.p2())

        # O(n)
        # find new top line
        while left_changed or right_changed:
            potential_new_line = QLineF(left_points[(left_index_top + 1) % len(left_points)], right_points[right_index_top])
            if convex_hull.pause:
                convex_hull.show_hull.emit([potential_new_line], (0, 0, 255))
            slope_new = self.calculate_slope(potential_new_line.p1(), potential_new_line.p2())
            if slope_new < slope_current:
                if convex_hull.pause:
                    convex_hull.erase_hull.emit([current_new_line, potential_new_line])
                current_new_line = potential_new_line
                if convex_hull.pause:
                    convex_hull.show_hull.emit([current_new_line], (0, 255, 0))
                slope_current = slope_new
                left_index_top += 1
                left_changed = True
            else:
                if convex_hull.pause:
                    convex_hull.erase_hull.emit([potential_new_line])
                left_changed = False

            potential_new_line = QLineF(left_points[left_index_top], right_points[(right_index_top + 1) % len(right_points)])
            if convex_hull.pause:
                convex_hull.show_hull.emit([potential_new_line], (0, 0, 255))
            slope_new = self.calculate_slope(potential_new_line.p1(), potential_new_line.p2())
            if slope_new > slope_current:
                if convex_hull.pause:
                    convex_hull.erase_hull.emit([current_new_line, potential_new_line])
                current_new_line = potential_new_line
                if convex_hull.pause:
                    convex_hull.show_hull.emit([current_new_line], (0, 255, 0))
                slope_current = slope_new
                right_index_top += 1
                right_changed = True
            else:
                if convex_hull.pause:
                    convex_hull.erase_hull.emit([potential_new_line])
                right_changed = False

        if convex_hull.pause:
            convex_hull.erase_hull.emit([current_new_line])
        new_top_edge = current_new_line
        if convex_hull.pause:
            convex_hull.show_hull.emit([new_top_edge], (255, 0, 0))

        # Find bottom line
        left_changed = True
        right_changed = True
        left_index_bottom, right_index_bottom = 0, 0

        # O(n)
        current_new_line = QLineF(left_points[left_index_bottom], right_points[right_index_bottom])
        if convex_hull.pause:
            convex_hull.show_hull.emit([current_new_line], (0, 255, 0))
        slope_current = self.calculate_slope(current_new_line.p1(), current_new_line.p2())
        while left_changed or right_changed:
            potential_new_line = QLineF(left_points[(left_index_bottom - 1) % len(left_points)], right_points[right_index_bottom])
            if convex_hull.pause:
                convex_hull.show_hull.emit([potential_new_line], (0, 0, 255))
            slope_new = self.calculate_slope(potential_new_line.p1(), potential_new_line.p2())
            if slope_new > slope_current:
                if convex_hull.pause:
                    convex_hull.erase_hull.emit([current_new_line, potential_new_line])
                current_new_line = potential_new_line
                if convex_hull.pause:
                    convex_hull.show_hull.emit([current_new_line], (0, 255, 0))
                slope_current = slope_new
                left_index_bottom = ((left_index_bottom - 1) % len(left_points))
                left_changed = True
            else:
                if convex_hull.pause:
                    convex_hull.erase_hull.emit([potential_new_line])
                left_changed = False

            potential_new_line = QLineF(left_points[left_index_bottom], right_points[(right_index_bottom - 1) % len(right_points)])
            if convex_hull.pause:
                convex_hull.show_hull.emit([potential_new_line], (0, 0, 255))
            slope_new = self.calculate_slope(potential_new_line.p1(), potential_new_line.p2())
            if slope_new < slope_current:
                if convex_hull.pause:
                    convex_hull.erase_hull.emit([current_new_line, potential_new_line])
                current_new_line = potential_new_line
                if convex_hull.pause:
                    convex_hull.show_hull.emit([current_new_line], (0, 255, 0))
                slope_current = slope_new
                right_index_bottom = ((right_index_bottom - 1) % len(right_points))
                right_changed = True
            else:
                if convex_hull.pause:
                    convex_hull.erase_hull.emit([potential_new_line])
                right_changed = False

        if convex_hull.pause:
            convex_hull.erase_hull.emit([current_new_line])
        new_bottom_edge = current_new_line
        if convex_hull.pause:
            convex_hull.show_hull.emit([new_bottom_edge], (255, 0, 0))

        points_to_check = [left_points[left_index_bottom], left_points[left_index_top], right_points[right_index_top], right_points[right_index_bottom]]

        # Trim point arrays and delete unneeded points & associated lines.

        # O(n)
        self.delete_points_and_lines(left_points, left_index_top, left_index_bottom, left_hull.getLines(), convex_hull)

        # O(n)
        self.delete_points_and_lines(right_points, right_index_top, right_index_bottom, right_hull.getLines(), convex_hull)

        # Arrange trimmed arrays and fuse together
        combined_points = list()

        # O(n log n)
        if side == side.L:
            # find rightmost point and pop it off the list. Combine lists and sort for CC order based on slope
            i = 1
            right_most_index = 0

            # O(n)
            while i < len(right_points):
                if right_points[i].x() > right_points[right_most_index].x():
                    right_most_index = i
                i += 1

            # O(n)
            right_most_point = right_points.pop(right_most_index)
            right_points.extend(left_points)

            # O(n log n)
            right_points.sort(key=lambda point: self.calculate_slope(point, right_most_point))
            right_points.insert(0, right_most_point)
            combined_points = right_points

        # O(n log n)
        else:
            # find leftmost point and pop it off the list. Combine lists and sort for C order based on slope
            i = 1
            left_most_index = 0

            # O(n)
            while i < len(left_points):
                if left_points[i].x() < left_points[left_most_index].x():
                    left_most_index = i
                i += 1

            left_most_point = left_points.pop(left_most_index)
            left_points.extend(right_points)

            # O(n log n)
            left_points.sort(key=lambda point: self.calculate_slope(left_most_point, point), reverse=True)
            left_points.insert(0, left_most_point)
            combined_points = left_points

        combined_lines = list()
        # O(n)
        combined_lines.extend(left_hull.getLines())
        # O(n)
        combined_lines.extend(right_hull.getLines())
        # Check points w/ newly created lines to see if there is a third middle line to delete

        # O(n^2)
        # O(n)
        for line in combined_lines:
            if line.p1() in points_to_check or line.p2() in points_to_check:
                # O(n)
                index_p1 = combined_points.index(line.p1())
                # O(n)
                index_p2 = combined_points.index(line.p2())
                distance = abs(index_p1 - index_p2)
                if distance != 1 and distance != (len(combined_points) - 1):
                    if convex_hull.pause:
                        convex_hull.erase_hull.emit([line])
                    # O(n)
                    combined_lines.remove(line)

        combined_lines.append(new_top_edge)
        combined_lines.append(new_bottom_edge)

        return [Hull(combined_lines), combined_points]

    # Master Theorem applies here: a = 2 subproblems of size n/(b = 2) and combines answers in O(n^(d = 2)). Log2(2) = 1 < d = 2, so overall O(n^(d = 2))
    def compute_hull(self, points, convex_hull, side=Side.W):  # returns hull, points
        lines = []
        completed_hull_and_points = None

        # Work at bottom of tree = O(1)
        # O(1)
        if len(points) == 2:
            new_line = QLineF(points[0], points[1])
            if convex_hull.pause:
                convex_hull.show_hull.emit([new_line], (255, 0, 0))
            lines.append(new_line)

            if side == Side.L:
                points.reverse()

            completed_hull_and_points = [Hull(lines), points]

        # O(1)
        elif len(points) == 3:
            # O(1)
            for i in range(3):
                new_line = QLineF(points[i], points[(i + 1) % 3])
                if convex_hull.pause:
                    convex_hull.show_hull.emit([new_line], (255, 0, 0))
                lines.append(new_line)

            # O(1)
            if side == Side.L:
                right_most_point = points.pop(2)

                # O(1) because there's only ever 2 points
                points.sort(key=lambda point: self.calculate_slope(point, right_most_point))
                points.insert(0, right_most_point)

            # O(1)
            elif side == Side.R:
                left_most_point = points.pop(0)
                points.sort(key=lambda point: self.calculate_slope(left_most_point, point), reverse=True)
                points.insert(0, left_most_point)

            completed_hull_and_points = [Hull(lines), points]

        # Split and combine parts = O(n^2)
        elif len(points) > 3:
            # Split parts = O(n)
            # O(n)
            left_points, right_points = points[:len(points)//2], points[len(points)//2:]
            # O(n)
            left_hull_and_points = self.compute_hull(left_points, convex_hull, Side.L)
            right_hull_and_points = self.compute_hull(right_points, convex_hull, Side.R)

            # Combine parts = O(n^2)
            completed_hull_and_points = self.combine_hulls(left_hull_and_points[1], left_hull_and_points[0], right_hull_and_points[1], right_hull_and_points[0], side, convex_hull)

        return completed_hull_and_points