import unittest
from pathlib import Path

from src.maze import Maze


ROOT = Path(__file__).resolve().parents[1]


class MazeSearchTests(unittest.TestCase):
    def test_maze1_all_algorithms_find_optimal_length_10(self):
        path = ROOT / "examples" / "maze1.txt"
        results = [Maze(path).ids(), Maze(path).a_star(), Maze(path).ida_star()]

        self.assertTrue(all(result.found for result in results))
        self.assertEqual({result.path_length for result in results}, {10})

    def test_maze2_ids_is_not_cut_off_at_depth_50(self):
        path = ROOT / "examples" / "maze2.txt"
        result = Maze(path).ids()

        self.assertTrue(result.found)
        self.assertEqual(result.path_length, 71)

    def test_maze2_informed_searches_find_length_71(self):
        path = ROOT / "examples" / "maze2.txt"
        results = [Maze(path).a_star(), Maze(path).ida_star()]

        self.assertTrue(all(result.found for result in results))
        self.assertEqual({result.path_length for result in results}, {71})

    def test_maze3_all_algorithms_find_optimal_length_4(self):
        path = ROOT / "examples" / "maze3.txt"
        results = [Maze(path).ids(), Maze(path).a_star(), Maze(path).ida_star()]

        self.assertTrue(all(result.found for result in results))
        self.assertEqual({result.path_length for result in results}, {4})

    def test_manhattan_distance_is_zero_at_goal(self):
        maze = Maze(ROOT / "examples" / "maze1.txt")
        self.assertEqual(maze.heuristic(maze.goal), 0)


if __name__ == "__main__":
    unittest.main()
