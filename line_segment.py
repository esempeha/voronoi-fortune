from dataclasses import dataclass
from typing import Optional
from point import Point

@dataclass
class LineSegment:
    """Represents a line segment in the Voronoi diagram."""
    start: Point  # Starting point
    end: Optional['Point'] = None  # Ending point
    done: bool = False  # Is the segment complete?

    def finish(self, p: Point) -> None:
        """Mark line segment as complete and set its endpoint."""
        if self.done:
            return
        self.end = p
        self.done = True