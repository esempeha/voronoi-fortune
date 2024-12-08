from typing import List, Union
import heapq
from point import Point
from event import Event

class EventPriorityQueue:
    """Priority queue implementation for handling events in Fortune's algorithm"""
    
    def __init__(self) -> None:
        """Initialize an empty priority queue"""
        self._queue: List[List] = []  # Heap of queue entries
        self._entry_finder = {}  # Mapping of items to entries
        self._REMOVED = '<removed>'  # Placeholder for a removed item
        self._counter = 0  # Unique

    def empty(self) -> bool:
        """Check if the queue is empty"""
        return not bool(self._entry_finder)
    
    def top(self) -> Union[Point, Event]:
        """Return the lowest priority item without removing it"""
        while self._queue:
            entry = heapq.heappop(self._queue)
            if entry[-1] is not self._REMOVED:
                item = entry[-1]
                self.push(item)  # Reinsert item
                return item
    
    def push(self, item: Union[Point, Event]) -> None:
        """Add a new item to the queue"""
        if item in self._entry_finder:
            self.remove(item)
        self._counter += 1
        entry = [item.x, self._counter, item]  # Priority, count, item
        self._entry_finder[item] = entry
        heapq.heappush(self._queue, entry)

    def pop(self) -> Union[Point, Event]:
        """Remove and return the lowest priority item"""
        while self._queue:
            _, _, item = heapq.heappop(self._queue)
            if item is not self._REMOVED:
                del self._entry_finder[item]
                return item
                
    def remove(self, item: Union[Point, Event]) -> None:
        """Mark an existing item as removed"""
        entry = self._entry_finder.pop(item)
        entry[-1] = self._REMOVED