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
        rise = right_point.y() - left_point.y()
        run = right_point.x() - left_point.x()

        return rise / run

    def delete_points_and_lines(self, points, top_index, bottom_index, lines, convex_hull):
        bottom_point = points[bottom_index]
        points_to_delete = list()

        index = (top_index - 1) % len(points)

        while points[index] != bottom_point:
            points_to_delete.append(points.pop(index))
            index = (index - 1) % len(points)

        i = 0

        while i < len(lines):
            if lines[i].p1() in points_to_delete or lines[i].p2() in points_to_delete:
                if convex_hull.pause:
                    convex_hull.erase_hull.emit([lines[i]])
                lines.pop(i)
            else:
                i += 1

    def combine_hulls(self, left_points, left_hull, right_points, right_hull, side, convex_hull): # returns combined hull, points
        left_changed = True
        right_changed = True

        left_index_top, right_index_top = 0, 0

        current_new_line = QLineF(left_points[left_index_top], right_points[right_index_top])
        if convex_hull.pause:
            convex_hull.show_hull.emit([current_new_line], (0, 255, 0))
        slope_current = self.calculate_slope(current_new_line.p1(), current_new_line.p2())

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

        self.delete_points_and_lines(left_points, left_index_top, left_index_bottom, left_hull.getLines(), convex_hull)

        self.delete_points_and_lines(right_points, right_index_top, right_index_bottom, right_hull.getLines(), convex_hull)

        # Arrange trimmed arrays and fuse together
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
            right_points.reverse()
            combined_points.extend(right_points)

        # Combine hull lines from individual hulls to form new hull
        combined_lines = list()
        combined_lines.extend(left_hull.getLines())
        combined_lines.extend(right_hull.getLines())  # TODO: are the lines actually being deleted from the hull?
        combined_lines.append(new_top_edge)
        combined_lines.append(new_bottom_edge)  # move these below?

        # Check points w/ newly created lines to see if there is a third middle line to delete

        for line in combined_lines:
            if line.p1() in points_to_check or line.p2() in points_to_check:
                index_p1 = combined_points.index(line.p1())
                index_p2 = combined_points.index(line.p2())
                distance = abs(index_p1 - index_p2)
                if distance != 1 and distance != (len(combined_points) - 1):
                    print("Line deleted after merge")
                    if convex_hull.pause:
                        convex_hull.erase_hull.emit([line])
                    del line

        #i = 0
        #print("About to begin working on removing leftover combined lines")
        #while i < len(combined_lines):
        #    print("i =")
        #    print(i)
        #    if combined_lines[i].p1() in points_to_check or combined_lines[i].p2() in points_to_check:
        #        index_p1 = combined_points.index(combined_lines[i].p1())
        #        index_p2 = combined_points.index(combined_lines[i].p2())
        #        distance = abs(index_p1 - index_p2)
        #        if distance != 1 and distance != (len(combined_points) - 1):
        #            combined_lines.pop(i)
        #        else:
        #            i += 1
        #    else:
        #        i += 1

        print("Done working on removing combined lines")
        return [Hull(combined_lines), combined_points]

    def compute_hull(self, points, convex_hull, side=Side.W):  # returns hull, points
        lines = []
        completed_hull_and_points = None

        if len(points) == 2:
            new_line = QLineF(points[0], points[1])
            if convex_hull.pause:
                convex_hull.show_hull.emit([new_line], (255, 0, 0))
            lines.append(new_line)

            if side == Side.L:
                points.reverse()

            completed_hull_and_points = [Hull(lines), points]

        elif len(points) == 3:
            for i in range(3):
                new_line = QLineF(points[i], points[(i + 1) % 3])
                if convex_hull.pause:
                    convex_hull.show_hull.emit([new_line], (255, 0, 0))
                lines.append(new_line)

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
            left_hull_and_points = self.compute_hull(left_points, convex_hull, Side.L)
            right_hull_and_points = self.compute_hull(right_points, convex_hull, Side.R)

            completed_hull_and_points = self.combine_hulls(left_hull_and_points[1], left_hull_and_points[0], right_hull_and_points[1], right_hull_and_points[0], side, convex_hull)

        return completed_hull_and_points