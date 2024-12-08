from dataclasses import dataclass
from typing import Optional
from point import Point

@dataclass
class Event:
    """Represents a site or circle event in Fortune's algorithm"""
    x: float  # X coordinate of the event (sweep line position)
    p: Point  # Associated point
    a: Optional['ParabolicArc']  # Related arc in the beachline
    valid: bool = True  # Validity flag

    def __hash__(self) -> int:
        """Compute a hash based on x and p coordinates"""
        return hash((self.x, self.p))

    def __eq__(self, other: object) -> bool:
        """Check equality based on x and p"""
        if not isinstance(other, Event):
            return False
        return self.x == other.x and self.p == other.p