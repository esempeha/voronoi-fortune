import math
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    """Represents a site/point (2 dimensional)"""
    x: float
    y: float

    def __init__(self, x: float, y: float):
        """Initialize Point with coordinates rounded to 1 decimal place"""
        x = float(f"{x:.1f}")
        y = float(f"{y:.1f}")

        # Set attributes on a frozen dataclass
        object.__setattr__(self, 'x', x)
        object.__setattr__(self, 'y', y)

    def __hash__(self) -> int:
        """Return hash based on x and y coordinates"""
        return hash((self.x, self.y))

    def distance_to(self, other: 'Point') -> float:
        """Calculate Euclidean distance to another point"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)