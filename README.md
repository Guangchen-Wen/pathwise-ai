# PathWise AI

PathWise AI is a Python desktop application for visualizing pathfinding on a weighted grid. It was built for the SOF106 Principles of Artificial Intelligence final group project.

## Project Title

**PathWise AI: A Weighted Pathfinding Visualizer Using A*, Dijkstra, BFS and Heuristic Search**

## Features

- Custom grid size using rows and columns.
- Interactive start and goal placement.
- Terrain editing with different movement costs:
  - Normal: cost 1
  - Grass: cost 3
  - Water: cost 5
  - Mountain: cost 8
  - Wall: blocked
- Search algorithms:
  - A*
  - Dijkstra
  - Breadth-First Search
  - Greedy Best-First Search
- Heuristic functions:
  - Manhattan distance
  - Euclidean distance
  - Chebyshev distance
- Animated visualization of explored nodes and final path.
- Algorithm comparison table with path cost, path length, visited nodes, and runtime.
- Random weighted map generation.

## How to Run

Use Python 3.10 or newer.

```bash
python app.py
```

No external libraries are required. The program uses only Python standard library modules.

## How to Test

```bash
python -m unittest test_pathfinding.py
```

## AI Concepts Covered

- State space search
- Weighted graph search
- A* evaluation function: `f(n) = g(n) + h(n)`
- Dijkstra as uniform-cost search
- BFS as an unweighted baseline
- Greedy Best-First Search using heuristic priority
- Heuristic comparison
- Validation through path cost, path length, explored nodes, and runtime

## Team Responsibility Mapping

| Member | Responsibility |
| --- | --- |
| Guangchen-Wen | Project leader, integration, testing, README |
| HXD3D0235 | UI layout and interactive grid editor |
| Tim456-cell | Terrain cost model and map generation |
| persistkun | A* and Dijkstra algorithm implementation |
| 0heh01 | BFS, Greedy search, heuristic comparison |
| zixi0427feng-source | Visualization, validation data, presentation |

## Suggested Demonstration Flow

1. Set a custom grid size.
2. Place start and goal nodes.
3. Draw walls and weighted terrain cells.
4. Run A* with Manhattan heuristic.
5. Compare A*, Dijkstra, BFS, and Greedy Best-First Search.
6. Explain why BFS may have fewer steps but higher terrain cost.
7. Show how weighted costs affect the final path.

## Repository

GitHub repository name: `pathwise-ai`
