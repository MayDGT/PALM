import math
import random
import sys
import matplotlib.pyplot as pl
import matplotlib.patches as patches
import matplotlib as mpl
from typing import List, Tuple, Optional

def random_rectangle(center_x, center_y, radius, eps=0.1) -> Tuple[float, float, float, float, float]:
    """Generate a random rectangle inside a given circle.

    Args:
        center_x: X-coordinate of the circle center.
        center_y: Y-coordinate of the circle center.
        radius: Radius of the circle.
        eps: Lower bound factor for the rectangle side length relative to the radius.

    Returns:
        A 5-tuple `(x, y, l, w, r)` where:
        - x, y: Center of the rectangle (same as the circle center).
        - l, w: Full length and width of the rectangle (not half-lengths).
        - r: Rotation in degrees (counterclockwise).
    """
    min_length = eps * radius
    max_length = (1 - eps) * radius
    length = random.uniform(min_length, max_length) 
    width = math.sqrt(radius ** 2 - length ** 2) 
    rotation = random.uniform(0, 90)
    scalar = 0.999 # make it a bit smaller
    return (center_x, center_y, scalar * length * 2, scalar * width * 2, rotation)

def get_subrectangles(x, y, l, w, r, count=4) -> List[Tuple[float, float, float, float, float]]:
    """Subdivide a rectangle along x and y directions into `count^2` sub-rectangles.

    Args:
        x, y: Center of the original rectangle.
        l, w: Full length and width of the original rectangle.
        r: Rotation of the rectangle in degrees (counterclockwise).
        count: Number of splits per axis (default: 4).

    Returns:
        A list of sub-rectangles, each as `(x_i, y_i, l_i, w_i, r)`, where
        `l_i = l / count`, `w_i = w / count`, and `(x_i, y_i)` is the center
        of the sub-rectangle after considering rotation.
    """
    r_radian = math.pi * r / 180
    x1 = x - l / 2
    x2 = x + l / 2
    xmin = min([x1, x2])
    xmax = max([x1, x2])
    xdiff = xmax - xmin

    y1 = y - w / 2
    y2 = y + w / 2
    ymin = min([y1, y2])
    ymax = max([y1, y2])
    ydiff = ymax - ymin

    rectangles = []
    for i in range(count):
        for j in range(count):
            rxmin = xmin + i * xdiff / count
            rx = rxmin + xdiff / (2 * count)
            rymin = ymin + j * ydiff / count
            ry = rymin + (ydiff / (2 * count))
            rl = l / count
            rw = w / count

            dx = rx - x
            dy = ry - y

            # Rotation matrix c, -s; s, c
            newdx = math.cos(r_radian) * dx - math.sin(r_radian) * dy
            newdy = math.sin(r_radian) * dx + math.cos(r_radian) * dy

            rectangles.append((x + newdx, y + newdy, rl, rw, r))

    return rectangles


def single_circle_coverage(x, y, l, w, r) -> Tuple[float, float, float]:
    """Compute the minimal enclosing circle for a given rectangle.

    Args:
        x, y: Center of the rectangle.
        l, w: Full length and width of the rectangle.
        r: Rectangle rotation in degrees (kept for API consistency, not used).

    Returns:
        A circle `(center_x, center_y, radius)` whose center is the same as the
        rectangle center and whose radius is `sqrt((l/2)^2 + (w/2)^2)`.
    """
    return (x, y, math.sqrt((l/2) ** 2 + (w/2) ** 2))


def circle_coverage(x, y, l, w, r, subdivision_count=4) -> List[Tuple[float, float, float]]:
    """Approximate a rotated rectangle by circles obtained from its sub-rectangles.

    The rectangle is split into `subdivision_count^2` sub-rectangles. For each
    sub-rectangle, the minimal enclosing circle is computed.

    Args:
        x, y: Center of the rectangle.
        l, w: Full length and width of the rectangle.
        r: Rotation of the rectangle in degrees (counterclockwise).
        subdivision_count: Number of splits per axis (default: 4).

    Returns:
        A list of circles `(center_x, center_y, radius)`.
    """

    circles = []
    for subrectangle in get_subrectangles(x, y, l, w, r, subdivision_count):
        circles.append(single_circle_coverage(*subrectangle))

    return circles

def random_nonintersecting_circle(center_x, center_y, upper_b, lower_b, left_b, right_b, other_circles) -> Optional[Tuple[float, float, float]]:
    """Find a maximal circle with a given center that does not intersect others and stays within bounds, then scale it randomly.

    Args:
        center_x, center_y: Center of the candidate circle.
        upper_b, lower_b, left_b, right_b: Bounds (top, bottom, left, right).
        other_circles: List of existing circles `(cx, cy, radius)`.

    Returns:
        `(center_x, center_y, radius)` where radius is the maximal feasible radius
        scaled by a random coefficient in `[0.5, 0.9]`. Returns `None` if no
        feasible radius is found.
    """
    radius = sys.float_info.max
    for (other_x, other_y, other_radius) in other_circles:
        distance = math.sqrt((other_x - center_x)**2 + (other_y - center_y)**2)
        boundary_distance = get_boundary_distance(center_x, center_y, upper_b, lower_b, left_b, right_b)
        radius = min([radius, distance - other_radius, boundary_distance])
    if radius <= 0:
        return None
    else:
        coeff = random.uniform(0.5, 0.9)
        return center_x, center_y, coeff * radius

def random_nonintersecting_rectangle(center_x, center_y, upper_b, lower_b, left_b, right_b, other_rectangles, subdivision_count=4) -> Optional[Tuple[float, float, float, float, float]]:
    """Generate a random rectangle near a given center that approximately does not intersect other rectangles.

    Method:
        Other rectangles `(x, y, l, w, r)` are approximated by circles via
        `circle_coverage`. A maximal feasible circle centered at
        `(center_x, center_y)` that does not intersect those circles and stays
        within the bounds is computed. A random rectangle is then sampled inside
        that feasible circle.

    Args:
        center_x, center_y: Desired rectangle center.
        upper_b, lower_b, left_b, right_b: Bounds (top, bottom, left, right).
        other_rectangles: Existing rectangles `(x, y, l, w, r)`.
        subdivision_count: Subdivision factor used for circle approximation (default: 4).

    Returns:
        A rectangle `(x, y, l, w, r)` if a feasible region exists, otherwise `None`.
    """
    all_other_circles = []
    print(other_rectangles)
    for other_rectangle in other_rectangles:
        all_other_circles += circle_coverage(*other_rectangle, subdivision_count)
    circle = random_nonintersecting_circle(center_x, center_y, upper_b, lower_b, left_b, right_b, all_other_circles)
    if circle is not None:
        return random_rectangle(*circle)
    else:
        return None

def get_boundary_distance(center_x, center_y, upper_b, lower_b, left_b, right_b) -> float:
    """Compute the minimum distance from a point to axis-aligned rectangular bounds.

    Args:
        center_x, center_y: Point coordinates.
        upper_b, lower_b, left_b, right_b: Bounds (top, bottom, left, right).

    Returns:
        The minimum distance to the bounds as a scalar.
    """
    upper_distance = upper_b - center_y
    lower_distance = center_y - lower_b
    left_distance = center_x - left_b
    right_distance = right_b - center_x
    return min([upper_distance, lower_distance, left_distance, right_distance])

def plot_rectangle(rectangles) -> None:
    """Visualize rectangles using matplotlib.

    Args:
        rectangles: Iterable of rectangles `(x, y, l, w, r)`.

    Notes:
        - Draws a semi-transparent rectangle for each item and marks its center.
        - Uses a fixed view window x, y in [-10, 150] for convenience.
    """
    for (x, y, l, w, r) in rectangles:
        pl.plot([x], [y], color="#FF000030", marker='o', markersize=10)
        rect = patches.Rectangle((x - l / 2, y - w / 2), l, w, color="#FF000030", alpha=0.10, angle=r, rotation_point='center')
        ax = pl.gca()
        ax.add_patch(rect)
    pl.figure()
    pl.plot()
    pl.xlim([-10, 150])
    pl.ylim([-10, 150])
    pl.show()

