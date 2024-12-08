from dataclasses import dataclass
from typing import Optional
from point import Point
from line_segment import LineSegment

@dataclass
class ParabolicArc:
    """Represents a beachline parabolic arc in Fortune's algorithm"""
    p: Point  # Site/point associated with this arc
    pprev: Optional['ParabolicArc'] = None  # Previous arc in the beachline
    pnext: Optional['ParabolicArc'] = None  # Next arc in the beachline
    e: Optional['Event'] = None  # Associated circle event (if any)
    s0: Optional['LineSegment'] = None  # Starting edge
    s1: Optional['LineSegment'] = None  # Ending edge
