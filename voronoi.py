"""
Fortune's algorithm implementation for Voronoi diagram generation.
This file provides a robust implementation of Fortune's algorithm to generate
Voronoi diagrams from a set of points in 2 dimensional space (x, y)
"""

import math
from typing import List, Optional, Tuple
from point import Point
from line_segment import LineSegment
from parabolic_arc import ParabolicArc
from event import Event
from event_priority_queue import EventPriorityQueue

class Voronoi:
    """
    Fortune's algorithm implementation for Voronoi diagram generation
    
    Attributes:
        EPSILON: For floating-point comparisons
        output: List of generated Voronoi diagram lineSegments
        parabolicArc: Root of beachline tree
        points: Priority queue of site events
        events: Priority queue of circle events
        largest_empty_circles: List of largest empty circles found
        max_circle_radius: Maximum radius among empty circles
        x0, y0, x1, y1: Bounding box coordinates
    """

    EPSILON = 1e-10

    def __init__(self, points: List[Tuple[float, float]], bounding_box_width, bounding_box_height) -> None:
        """Initialize Voronoi diagram computation with given input points and bounding box"""
        self._initialize_structures()
        self._setup_bounds(bounding_box_width, bounding_box_height)
        self._add_points(points)

    def _initialize_structures(self) -> None:
        """Initialize internal data structures"""
        self.output: List[LineSegment] = []
        self.parabolicArc: Optional[ParabolicArc] = None
        self.points = EventPriorityQueue()
        self.events = EventPriorityQueue()
        self.largest_empty_circles: List[Tuple[Point, float, Tuple[Point, Point, Point]]] = []
        self.max_circle_radius = 0

    def _setup_bounds(self, bounding_box_width, bounding_box_height) -> None:
        """Set up bounding box"""
        self.x0, self.y0 = 0, 0
        self.x1, self.y1 = bounding_box_width, bounding_box_height

    def _add_points(self, points: List[Tuple[float, float]]) -> None:
        """Add input points to priority queue"""
        for x, y in points:
            self.points.push(Point(x, y))

    def _check_circle(self, a: Point, b: Point, c: Point) -> Tuple[bool, Optional[float], Optional[Point]]:
        """Check if points a, b, c form a circle event"""
        # Check if bc is a "right turn" from ab
        if ((b.x - a.x)*(c.y - a.y) - (c.x - a.x)*(b.y - a.y)) > 0:
            return False, None, None

        # Calculate circle center using matrix method
        A = b.x - a.x
        B = b.y - a.y
        C = c.x - a.x
        D = c.y - a.y
        E = A*(a.x + b.x) + B*(a.y + b.y)
        F = C*(a.x + c.x) + D*(a.y + c.y)
        G = 2*(A*(c.y - b.y) - B*(c.x - b.x))

        if G == 0:  # Points are collinear
            return False, None, None

        # Calculate circle center
        ox = (D*E - B*F) / G
        oy = (A*F - C*E) / G
        o = Point(ox, oy)

        # Calculate x coordinate of circle event
        x = ox + math.sqrt((a.x-ox)**2 + (a.y-oy)**2)

        return True, x, o

    def _check_potential_circle_event(self, i: ParabolicArc, x0: float) -> None:
        """Check for potential circle event at parabolic arc i"""
        # Invalidate old event
        if i.e and i.e.x != self.x0:
            i.e.valid = False
        i.e = None

        if not i.pprev or not i.pnext:
            return

        # Check for circle event
        flag, x, o = self._check_circle(i.pprev.p, i.p, i.pnext.p)
        if flag and x > x0:
            i.e = Event(x, o, i)
            self.events.push(i.e)
            
            # Calculate radius and check if it's a largest empty circle
            radius = math.sqrt((o.x - i.p.x)**2 + (o.y - i.p.y)**2)
            
            # Check if this circle is empty (contains no other points)
            is_empty = True
            for entry in self.points._entry_finder:
                if entry not in (i.pprev.p, i.p, i.pnext.p):
                    dist = math.sqrt((entry.x - o.x)**2 + (entry.y - o.y)**2)
                    if dist < radius - self.EPSILON:  # Use small epsilon for floating point comparison
                        is_empty = False
                        break
            
            if is_empty:
                if abs(radius - self.max_circle_radius) < self.EPSILON:
                    # Same radius as current max -> add to list
                    self.largest_empty_circles.append((o, radius, (i.pprev.p, i.p, i.pnext.p)))
                elif radius > self.max_circle_radius:
                    # New largest radius found -> clear list and add this one instead
                    self.max_circle_radius = radius
                    self.largest_empty_circles = [(o, radius, (i.pprev.p, i.p, i.pnext.p))]

    def _add_parabolic_parabolicArc(self, p: Point) -> None:
        """Insert new parabolic arc"""
        if not self.parabolicArc:
            self.parabolicArc = ParabolicArc(p)
            return

        # Find intersecting parabolic arc
        i = self.parabolicArc
        while i:
            flag, z = self._check_intersection(p, i)
            if flag:
                # Split the parabolic arc
                flag, _ = self._check_intersection(p, i.pnext)
                if i.pnext and not flag:
                    i.pnext.pprev = ParabolicArc(i.p, i, i.pnext)
                    i.pnext = i.pnext.pprev
                else:
                    i.pnext = ParabolicArc(i.p, i)
                i.pnext.s1 = i.s1

                # Insert new parabolic arc
                i.pnext.pprev = ParabolicArc(p, i, i.pnext)
                i.pnext = i.pnext.pprev
                i = i.pnext

                # Create new edges
                seg = LineSegment(z)
                self.output.append(seg)
                i.pprev.s1 = i.s0 = seg

                seg = LineSegment(z)
                self.output.append(seg)
                i.pnext.s0 = i.s1 = seg

                # Check for new circle events
                self._check_potential_circle_event(i, p.x)
                self._check_potential_circle_event(i.pprev, p.x)
                self._check_potential_circle_event(i.pnext, p.x)
                return

            i = i.pnext

        # Special case: if p never intersects an parabolic arc, append it
        i = self.parabolicArc
        while i.pnext:
            i = i.pnext
        i.pnext = ParabolicArc(p, i)

        # Add new edge
        x = self.x0
        y = (i.pnext.p.y + i.p.y) / 2.0
        start = Point(x, y)
        seg = LineSegment(start)
        i.s1 = i.pnext.s0 = seg
        self.output.append(seg)

    def _find_intersection(self, p0: Point, p1: Point, l: float) -> Point:
        """Find intersection point of two parabolas"""
        p = p0
        if p0.x == p1.x:
            py = (p0.y + p1.y) / 2
        elif p1.x == l:
            py = p1.y
        elif p0.x == l:
            py = p0.y
            p = p1
        else:
            # Use quadratic formula
            z0 = 2.0 * (p0.x - l)
            z1 = 2.0 * (p1.x - l)

            a = 1/z0 - 1/z1
            b = -2.0 * (p0.y/z0 - p1.y/z1)
            c = ((p0.y**2 + p0.x**2 - l**2) / z0 -
                 (p1.y**2 + p1.x**2 - l**2) / z1)

            py = (-b - math.sqrt(b*b - 4*a*c)) / (2*a)

        px = (p.x**2 + (p.y-py)**2 - l**2) / (2*p.x-2*l)
        return Point(px, py)

    def _check_intersection(self, p: Point, i: Optional[ParabolicArc]) -> Tuple[bool, Optional[Point]]:
        """Find intersection of new parabola at p with parabolic arc i"""
        if not i or p.x == i.p.x:
            return False, None

        # Find intersections with neighboring parabolic arcs
        a = b = float('inf')
        if i.pprev:
            a = self._find_intersection(i.pprev.p, i.p, p.x).y
        if i.pnext:
            b = self._find_intersection(i.p, i.pnext.p, p.x).y

        # Check if p is between the intersections
        if ((i.pprev is None or a <= p.y) and (i.pnext is None or p.y <= b)):
            py = p.y
            px = ((i.p.x**2 + (i.p.y-py)**2 - p.x**2) /
                  (2*i.p.x - 2*p.x))
            return True, Point(px, py)
        return False, None

    def _complete_unfinished_edges(self) -> None:
        """Complete all unfinished edges to bounding box"""
        margin = max(self.x1 - self.x0, self.y1 - self.y0)
        i = self.parabolicArc
        
        while i and i.pnext:
            if i.s1:
                try:
                    # Get points defining the line
                    p1, p2 = i.p, i.pnext.p
                    
                    # Calculate midpoint
                    mx = (p1.x + p2.x) / 2
                    my = (p1.y + p2.y) / 2
                    
                    # Calculate direction vector
                    dx = p2.x - p1.x
                    dy = p2.y - p1.y
                    
                    # Skip if points are too close
                    if abs(dx) < self.EPSILON and abs(dy) < self.EPSILON:
                        i = i.pnext
                        continue
                    
                    # Calculate perpendicular vector
                    length = math.sqrt(dx*dx + dy*dy)
                    nx = -dy/length  # Normalized perpendicular vector
                    ny = dx/length
                    
                    # Find intersection with bounding box
                    # Start from the midpoint and extend in both directions
                    x1, y1 = mx, my
                    x2, y2 = mx, my
                    
                    # Extend in positive direction
                    t = margin
                    px = mx + nx * t
                    py = my + ny * t
                    
                    # Clip to bounding box
                    if px < self.x0: 
                        t = (self.x0 - mx) / nx
                    elif px > self.x1: 
                        t = (self.x1 - mx) / nx

                    if py < self.y0: 
                        t = min(t, (self.y0 - my) / ny)
                    elif py > self.y1: 
                        t = min(t, (self.y1 - my) / ny)
                    
                    x1 = mx + nx * t
                    y1 = my + ny * t
                    
                    # Extend in negative direction
                    t = margin
                    px = mx - nx * t
                    py = my - ny * t
                    
                    # Clip to bounding box
                    if px < self.x0: 
                        t = (mx - self.x0) / nx
                    elif px > self.x1: 
                        t = (mx - self.x1) / nx
                    
                    if py < self.y0: 
                        t = min(t, (my - self.y0) / ny)
                    elif py > self.y1: 
                        t = min(t, (my - self.y1) / ny)
                    
                    x2 = mx - nx * t
                    y2 = my - ny * t
                    
                    # Create end point
                    p = Point(x1, y1)
                    if i.s1.start.x == x2 and i.s1.start.y == y2:
                        p = Point(x1, y1)
                    else:
                        p = Point(x2, y2)
                    
                    i.s1.finish(p)
                    
                except Exception as e:
                    print(f"Error finishing edge: {e}")
            i = i.pnext

    def _handle_two_points_case(self) -> None:
        """Handle special case of exactly two points"""
        p1 = next(iter(self.points._entry_finder))
        self.points.pop()  # Remove first point
        p2 = next(iter(self.points._entry_finder))
        
        # Calculate perpendicular bisector
        mx = (p1.x + p2.x) / 2
        my = (p1.y + p2.y) / 2
        
        # Get vector between points
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        
        # Handle vertical/horizontal lines specially
        if abs(dx) < self.EPSILON:  # Vertical line
            start = Point(mx - self.x1, my)
            end = Point(mx + self.x1, my)
        elif abs(dy) < self.EPSILON:  # Horizontal line
            start = Point(mx, my - self.y1)
            end = Point(mx, my + self.y1)
        else:
            # Normal case
            length = math.sqrt(dx*dx + dy*dy)
            if length < self.EPSILON:
                return
                
            # Normalize and rotate 90 degrees
            dx, dy = -dy/length, dx/length
            margin = max(self.x1 - self.x0, self.y1 - self.y0)
            start = Point(mx + dx * margin, my + dy * margin)
            end = Point(mx - dx * margin, my - dy * margin)
        
        # Add the line segment
        segment = LineSegment(start)
        segment.finish(end)
        self.output.append(segment)

    def _process_all_events(self) -> None:
        """Process all site and circle events in order"""
        while not self.points.empty():
            if (not self.events.empty() and 
                self.events.top().x <= self.points.top().x):
                self._process_circle_event()
            else:
                self._process_site_event()

    def _process_remaining_events(self) -> None:
        """Process any remaining circle events"""
        while not self.events.empty():
            self._process_circle_event()

    def _process_site_event(self) -> None:
        """Process site event (new point)"""
        p = self.points.pop()
        self._add_parabolic_parabolicArc(p)

    def _process_circle_event(self) -> None:
        """Process circle event"""
        e = self.events.pop()
        if not e.valid:
            return

        # Create new edge at circle point
        s: LineSegment = LineSegment(e.p)
        self.output.append(s)

        # Update parabolicArc references
        a: ParabolicArc = e.a
        if a.pprev:
            a.pprev.pnext = a.pnext
            a.pprev.s1 = s
        if a.pnext:
            a.pnext.pprev = a.pprev
            a.pnext.s0 = s

        # Finish edges
        if a.s0:
            a.s0.finish(e.p)
        if a.s1:
            a.s1.finish(e.p)

        # Recheck circle events
        if a.pprev:
            self._check_potential_circle_event(a.pprev, e.x)
        if a.pnext:
            self._check_potential_circle_event(a.pnext, e.x)

    def generate_voronoi_diagram(self) -> None:
        """
        Process all points and generate Voronoi diagram
        
        Special cases:
        - Handles 2 points case separately
        - Processes all site and circle events
        - Complete unfinished edges at bounding box
        """
        try:
            if len(self.points._entry_finder) == 2:
                self._handle_two_points_case()
                return

            self._process_all_events()
            self._process_remaining_events()
            self._complete_unfinished_edges()

        except Exception as e:
            print(f"Error during processing: {e}")
            raise

    def get_voronoi_line_segments(self) -> List[Tuple[float, float, float, float]]:
        """Get the line segments of the Voronoi diagram in (x1, y1, x2, y2) format"""
        return [(o.start.x, o.start.y, o.end.x, o.end.y) for o in self.output if o.done]

    def get_largest_empty_circles(self) -> List[Tuple[Point, float, Tuple[Point, Point, Point]]]:
        """Return the largest empty circles found during computation in (center_point, radius, defining_points) format"""
        return self.largest_empty_circles