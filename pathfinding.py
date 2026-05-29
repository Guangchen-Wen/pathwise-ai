"""Pathfinding algorithms for PathWise AI.

The module is intentionally UI-free so the algorithms can be tested and
explained independently in the project report.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count
from math import sqrt
from time import perf_counter
from typing import Callable


Position = tuple[int, int]
Grid = list[list[str]]


TERRAIN_COSTS: dict[str, int | None] = {
    "normal": 1,
    "grass": 3,
    "water": 5,
    "mountain": 8,
    "wall": None,
}


@dataclass(frozen=True)
class SearchResult:
    algorithm: str
    heuristic: str
    found: bool
    path: list[Position]
    visited_order: list[Position]
    total_cost: int
    path_length: int
    explored_nodes: int
    frontier_max: int
    runtime_ms: float
    note: str = ""


def terrain_cost(grid: Grid, position: Position) -> int | None:
    row, col = position
    return TERRAIN_COSTS.get(grid[row][col], 1)


def in_bounds(grid: Grid, position: Position) -> bool:
    row, col = position
    return 0 <= row < len(grid) and 0 <= col < len(grid[0])


def neighbors(grid: Grid, position: Position) -> list[Position]:
    row, col = position
    candidates = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
    return [pos for pos in candidates if in_bounds(grid, pos) and terrain_cost(grid, pos) is not None]


def reconstruct_path(came_from: dict[Position, Position], start: Position, goal: Position) -> list[Position]:
    if goal != start and goal not in came_from:
        return []

    current = goal
    path = [current]
    while current != start:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def calculate_path_cost(grid: Grid, path: list[Position]) -> int:
    if not path:
        return 0

    # The cost of a path is the cost paid when entering each next cell.
    return sum(terrain_cost(grid, pos) or 0 for pos in path[1:])


def heuristic_distance(name: str, current: Position, goal: Position) -> float:
    """use different function to find the distance from the current positon to the goal 
    
    and return the value"""
    
    row_diatance = abs(current[0] - goal[0])
    
    col_distance = abs(current[1] - goal[1])

    if name == "Euclidean":
        return sqrt(row_distance ** 2 + col_distance ** 2)
        #geomatric distance
    if name == "Chebyshev":
        return max(row_distance, col_distance)
        # choose the max distance between row_distance and col_distance
    else:
        return row_distanace + col_distance
        # calculate the sum of distance of row and col


def _finish(
    algorithm: str,
    heuristic: str,
    grid: Grid,
    start: Position,
    goal: Position,
    came_from: dict[Position, Position],
    visited_order: list[Position],
    frontier_max: int,
    started_at: float,
    note: str = "",
) -> SearchResult:
    path = reconstruct_path(came_from, start, goal)
    found = bool(path)
    return SearchResult(
        algorithm=algorithm,
        heuristic=heuristic,
        found=found,
        path=path,
        visited_order=visited_order,
        total_cost=calculate_path_cost(grid, path),
        path_length=max(0, len(path) - 1),
        explored_nodes=len(visited_order),
        frontier_max=frontier_max,
        runtime_ms=(perf_counter() - started_at) * 1000,
        note=note,
    )


def weighted_search(grid: Grid, start: Position, goal: Position, algorithm: str, heuristic: str) -> SearchResult:
    """Run A*, Dijkstra, or Greedy Best-First Search on a weighted grid."""
    started_at = perf_counter()  # Record start time
    frontier: list[tuple[float, int, Position]] = []  # Nodes to explore
    unique = count()  # Unique id for heap sorting
    came_from: dict[Position, Position] = {}  # Record path
    cost_so_far: dict[Position, int] = {start: 0}  # Travel cost so far
    visited: set[Position] = set()  # Visited nodes
    visited_order: list[Position] = []  # Visit sequence 
    frontier_max = 1  # Max queue size

    heappush(frontier, (0, next(unique), start))  # Add start node

    while frontier:  
        frontier_max = max(frontier_max, len(frontier))  # Update max size, to record memory usage
        _, _, current = heappop(frontier)  
        if current in visited: 
            continue

        visited.add(current)  
        visited_order.append(current)  

        if current == goal: 
            return _finish(algorithm, heuristic, grid, start, goal, came_from, visited_order, frontier_max, started_at)
        #Start iterating over the neighbors. Skip if a neighbor is an obstacle.
        for neighbor in neighbors(grid, current):  
            step_cost = terrain_cost(grid, neighbor)  
            if step_cost is None: 
                continue

            new_cost = cost_so_far[current] + step_cost  
            #There are two cases to update the node. First, the node has never been visited.
            Second, the new path has a lower cost than the recorded one.
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:  
                cost_so_far[neighbor] = new_cost  
                came_from[neighbor] = current  
                h_value = heuristic_distance(heuristic, neighbor, goal)  

                if algorithm == "Dijkstra":
                    priority = new_cost  # Priority = travel cost
                elif algorithm == "Greedy Best-First":
                    priority = h_value  # Priority = heuristic
                else:
                    priority = new_cost + h_value  # Priority = cost + heuristic

                heappush(frontier, (priority, next(unique), neighbor))  # Add to queue

    return _finish(
        algorithm,
        heuristic,
        grid,
        start,
        goal,
        came_from,
        visited_order,
        frontier_max,
        started_at,
        "No path found",
    )  # No available path


def breadth_first_search(grid: Grid, start: Position, goal: Position, heuristic: str = "None") -> SearchResult:
    """Run BFS as an unweighted baseline.

    BFS minimizes number of steps, not weighted terrain cost. This makes it a
    useful comparison algorithm when the map contains grass, water, or mountain
    cells.
    """

    started_at = perf_counter()
    frontier: deque[Position] = deque([start])
    came_from: dict[Position, Position] = {}
    visited: set[Position] = {start}
    visited_order: list[Position] = []
    frontier_max = 1

    while frontier:
        frontier_max = max(frontier_max, len(frontier))
        current = frontier.popleft()
        visited_order.append(current)

        if current == goal:
            return _finish(
                "BFS",
                heuristic,
                grid,
                start,
                goal,
                came_from,
                visited_order,
                frontier_max,
                started_at,
                "BFS ignores terrain weights",
            )

        for neighbor in neighbors(grid, current):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            came_from[neighbor] = current
            frontier.append(neighbor)

    return _finish(
        "BFS",
        heuristic,
        grid,
        start,
        goal,
        came_from,
        visited_order,
        frontier_max,
        started_at,
        "No path found",
    )


def run_search(grid: Grid, start: Position, goal: Position, algorithm: str, heuristic: str) -> SearchResult:
    runners: dict[str, Callable[[Grid, Position, Position, str], SearchResult]] = {
        "BFS": breadth_first_search,
    }

    if algorithm in runners:
        return runners[algorithm](grid, start, goal, heuristic)

    return weighted_search(grid, start, goal, algorithm, heuristic)


def run_all_algorithms(grid: Grid, start: Position, goal: Position, heuristic: str) -> list[SearchResult]:
    return [run_search(grid, start, goal, algorithm, heuristic) for algorithm in ["A*", "Dijkstra", "BFS", "Greedy Best-First"]]
