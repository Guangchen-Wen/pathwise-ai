import unittest

from pathfinding import calculate_path_cost, run_search


class PathfindingTests(unittest.TestCase):
    def test_a_star_finds_path_on_empty_grid(self):
        grid = [["normal" for _ in range(5)] for _ in range(5)]
        result = run_search(grid, (0, 0), (4, 4), "A*", "Manhattan")
        self.assertTrue(result.found)
        self.assertEqual(result.path_length, 8)
        self.assertEqual(result.total_cost, 8)

    def test_dijkstra_avoids_expensive_cells(self):
        grid = [["normal" for _ in range(5)] for _ in range(3)]
        grid[1][1] = "water"
        grid[1][2] = "water"
        grid[1][3] = "water"
        result = run_search(grid, (1, 0), (1, 4), "Dijkstra", "Manhattan")
        self.assertTrue(result.found)
        self.assertLess(result.total_cost, 20)
        self.assertNotIn((1, 2), result.path)

    def test_bfs_is_unweighted_baseline(self):
        grid = [["normal" for _ in range(5)] for _ in range(3)]
        grid[1][1] = "water"
        grid[1][2] = "water"
        grid[1][3] = "water"
        result = run_search(grid, (1, 0), (1, 4), "BFS", "Manhattan")
        self.assertTrue(result.found)
        self.assertEqual(result.path_length, 4)
        self.assertGreaterEqual(calculate_path_cost(grid, result.path), 10)


if __name__ == "__main__":
    unittest.main()
