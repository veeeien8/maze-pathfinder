"""Classical AI search algorithms for solving grid mazes.

Algorithms implemented:
- Iterative Deepening Search (IDS)
- A* Search
- Iterative Deepening A* (IDA*)

Maze format:
    A = start
    B = goal
    space = open cell
    any other character = wall
"""

from __future__ import annotations

import argparse
import heapq
import itertools
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Node:
    state: tuple[int, int]
    parent: Optional["Node"]
    action: Optional[str]


@dataclass
class SearchResult:
    algorithm: str
    found: bool
    actions: list[str]
    path: list[tuple[int, int]]
    path_cost: Optional[int]
    path_length: Optional[int]
    states_explored: int
    runtime_seconds: float


class Maze:
    """Load, solve, print, and visualise a grid maze."""

    def __init__(self, filename: str | Path):
        self.filename = Path(filename)
        contents = self.filename.read_text(encoding="utf-8")

        if contents.count("A") != 1:
            raise ValueError("Maze must contain exactly one start point 'A'.")
        if contents.count("B") != 1:
            raise ValueError("Maze must contain exactly one goal point 'B'.")

        lines = contents.splitlines()
        self.height = len(lines)
        self.width = max(len(line) for line in lines)

        self.walls: list[list[bool]] = []
        self.start: tuple[int, int] | None = None
        self.goal: tuple[int, int] | None = None

        for row_index in range(self.height):
            row: list[bool] = []
            for col_index in range(self.width):
                char = lines[row_index][col_index] if col_index < len(lines[row_index]) else " "

                if char == "A":
                    self.start = (row_index, col_index)
                    row.append(False)
                elif char == "B":
                    self.goal = (row_index, col_index)
                    row.append(False)
                elif char == " ":
                    row.append(False)
                else:
                    row.append(True)

            self.walls.append(row)

        assert self.start is not None
        assert self.goal is not None

        self.solution: Optional[tuple[list[str], list[tuple[int, int]]]] = None
        self.explored: set[tuple[int, int]] = set()
        self.num_explored = 0

    def reset_search(self) -> None:
        self.solution = None
        self.explored = set()
        self.num_explored = 0

    def print_maze(self) -> None:
        """Print the maze, adding * characters along the solution path."""
        solution = set(self.solution[1]) if self.solution else set()

        print()
        for row_index, row in enumerate(self.walls):
            for col_index, is_wall in enumerate(row):
                state = (row_index, col_index)

                if is_wall:
                    print("█", end="")
                elif state == self.start:
                    print("A", end="")
                elif state == self.goal:
                    print("B", end="")
                elif state in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()

    def neighbors(self, state: tuple[int, int]) -> list[tuple[str, tuple[int, int]]]:
        """Return valid U/D/L/R moves from a state."""
        row, col = state
        candidates = [
            ("U", (row - 1, col)),
            ("D", (row + 1, col)),
            ("L", (row, col - 1)),
            ("R", (row, col + 1)),
        ]

        result = []
        for action, (next_row, next_col) in candidates:
            if (
                0 <= next_row < self.height
                and 0 <= next_col < self.width
                and not self.walls[next_row][next_col]
            ):
                result.append((action, (next_row, next_col)))

        return result

    def heuristic(self, state: tuple[int, int]) -> int:
        """Manhattan distance from state to the goal."""
        return abs(state[0] - self.goal[0]) + abs(state[1] - self.goal[1])

    @staticmethod
    def _states_in_path(node: Node) -> set[tuple[int, int]]:
        states = set()
        current: Optional[Node] = node
        while current is not None:
            states.add(current.state)
            current = current.parent
        return states

    def _set_solution(self, node: Node) -> tuple[list[str], list[tuple[int, int]]]:
        actions: list[str] = []
        cells: list[tuple[int, int]] = []

        current = node
        while current.parent is not None:
            assert current.action is not None
            actions.append(current.action)
            cells.append(current.state)
            current = current.parent

        actions.reverse()
        cells.reverse()
        self.solution = (actions, cells)
        return actions, cells

    def _make_result(
        self,
        algorithm: str,
        node: Optional[Node],
        runtime_seconds: float,
        states_explored: int,
    ) -> SearchResult:
        if node is None:
            self.solution = None
            return SearchResult(
                algorithm=algorithm,
                found=False,
                actions=[],
                path=[],
                path_cost=None,
                path_length=None,
                states_explored=states_explored,
                runtime_seconds=runtime_seconds,
            )

        actions, cells = self._set_solution(node)
        return SearchResult(
            algorithm=algorithm,
            found=True,
            actions=actions,
            path=cells,
            path_cost=len(actions),
            path_length=len(actions),
            states_explored=states_explored,
            runtime_seconds=runtime_seconds,
        )

    # ------------------------------------------------------------------
    # Iterative Deepening Search
    # ------------------------------------------------------------------

    def ids(self, max_depth: Optional[int] = None) -> SearchResult:
        """Solve the maze with Iterative Deepening Search."""
        self.reset_search()
        start_time = time.perf_counter()

        # Any shortest simple path in a finite maze has at most
        # (number of traversable cells - 1) moves. This avoids the arbitrary
        # depth-50 limit from the original assignment version.
        if max_depth is None:
            traversable_cells = sum(not cell for row in self.walls for cell in row)
            max_depth = max(0, traversable_cells - 1)

        total_explored = 0
        final_explored: set[tuple[int, int]] = set()

        for depth_limit in range(max_depth + 1):
            node, explored_count, explored_states = self._depth_limited_search(depth_limit)
            total_explored += explored_count
            final_explored = explored_states

            if node is not None:
                self.num_explored = total_explored
                self.explored = final_explored
                runtime = time.perf_counter() - start_time
                return self._make_result("IDS", node, runtime, total_explored)

        self.num_explored = total_explored
        self.explored = final_explored
        runtime = time.perf_counter() - start_time
        return self._make_result("IDS", None, runtime, total_explored)

    def _depth_limited_search(
        self, depth_limit: int
    ) -> tuple[Optional[Node], int, set[tuple[int, int]]]:
        start = Node(self.start, None, None)
        frontier: list[tuple[Node, int]] = [(start, 0)]

        explored_count = 0
        explored_states: set[tuple[int, int]] = set()

        while frontier:
            node, depth = frontier.pop()
            explored_count += 1
            explored_states.add(node.state)

            if node.state == self.goal:
                return node, explored_count, explored_states

            if depth == depth_limit:
                continue

            path_states = self._states_in_path(node)

            # Deliberately preserve the original assignment's U/D/L/R push
            # order. With a LIFO stack this means the most recently added
            # valid child is explored first.
            for action, state in self.neighbors(node.state):
                if state in path_states:
                    continue
                frontier.append((Node(state, node, action), depth + 1))

        return None, explored_count, explored_states

    # ------------------------------------------------------------------
    # A* Search
    # ------------------------------------------------------------------

    def a_star(self) -> SearchResult:
        """Solve the maze using A* with Manhattan distance."""
        self.reset_search()
        start_time = time.perf_counter()

        counter = itertools.count()
        start = Node(self.start, None, None)
        frontier: list[tuple[int, int, int, Node]] = []
        heapq.heappush(
            frontier,
            (self.heuristic(self.start), next(counter), 0, start),
        )

        g_score = {self.start: 0}
        closed: set[tuple[int, int]] = set()

        while frontier:
            _, _, g_cost, node = heapq.heappop(frontier)

            if g_cost != g_score.get(node.state):
                continue
            if node.state in closed:
                continue

            self.num_explored += 1
            self.explored.add(node.state)

            if node.state == self.goal:
                runtime = time.perf_counter() - start_time
                return self._make_result("A*", node, runtime, self.num_explored)

            closed.add(node.state)

            for action, state in self.neighbors(node.state):
                if state in closed:
                    continue

                new_g = g_cost + 1
                if new_g < g_score.get(state, float("inf")):
                    g_score[state] = new_g
                    child = Node(state, node, action)
                    new_f = new_g + self.heuristic(state)
                    heapq.heappush(
                        frontier,
                        (new_f, next(counter), new_g, child),
                    )

        runtime = time.perf_counter() - start_time
        return self._make_result("A*", None, runtime, self.num_explored)

    # ------------------------------------------------------------------
    # Iterative Deepening A*
    # ------------------------------------------------------------------

    def ida_star(self) -> SearchResult:
        """Solve the maze using Iterative Deepening A*."""
        self.reset_search()
        start_time = time.perf_counter()

        threshold = self.heuristic(self.start)
        total_explored = 0
        final_explored: set[tuple[int, int]] = set()

        while True:
            node, next_threshold, explored_count, explored_states = self._ida_iteration(
                threshold
            )

            total_explored += explored_count
            final_explored = explored_states

            if node is not None:
                self.num_explored = total_explored
                self.explored = final_explored
                runtime = time.perf_counter() - start_time
                return self._make_result("IDA*", node, runtime, total_explored)

            if next_threshold == float("inf"):
                self.num_explored = total_explored
                self.explored = final_explored
                runtime = time.perf_counter() - start_time
                return self._make_result("IDA*", None, runtime, total_explored)

            threshold = int(next_threshold)

    def _ida_iteration(
        self, threshold: int
    ) -> tuple[Optional[Node], float, int, set[tuple[int, int]]]:
        start = Node(self.start, None, None)
        frontier: list[tuple[Node, int]] = [(start, 0)]

        next_threshold = float("inf")
        explored_count = 0
        explored_states: set[tuple[int, int]] = set()

        while frontier:
            node, g_cost = frontier.pop()
            f_cost = g_cost + self.heuristic(node.state)

            explored_count += 1
            explored_states.add(node.state)

            if f_cost > threshold:
                next_threshold = min(next_threshold, f_cost)
                continue

            if node.state == self.goal:
                return node, next_threshold, explored_count, explored_states

            path_states = self._states_in_path(node)

            for action, state in self.neighbors(node.state):
                if state in path_states:
                    continue
                frontier.append((Node(state, node, action), g_cost + 1))

        return None, next_threshold, explored_count, explored_states

    # ------------------------------------------------------------------
    # Visualisation
    # ------------------------------------------------------------------

    def output_image(
        self,
        filename: str | Path,
        *,
        show_solution: bool = True,
        show_explored: bool = False,
    ) -> None:
        """Save the maze as a PNG image."""
        try:
            from PIL import Image, ImageDraw
        except ImportError as exc:
            raise RuntimeError(
                "PNG output requires Pillow. Run: pip install -r requirements.txt"
            ) from exc

        cell_size = 42
        cell_border = 2
        image = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black",
        )
        draw = ImageDraw.Draw(image)

        solution = set(self.solution[1]) if self.solution else set()

        for row_index, row in enumerate(self.walls):
            for col_index, is_wall in enumerate(row):
                state = (row_index, col_index)

                if is_wall:
                    fill = (40, 40, 40)
                elif state == self.start:
                    fill = (255, 0, 0)
                elif state == self.goal:
                    fill = (0, 171, 28)
                elif show_solution and state in solution:
                    fill = (220, 235, 113)
                elif show_explored and state in self.explored:
                    fill = (212, 97, 85)
                else:
                    fill = (237, 240, 252)

                draw.rectangle(
                    [
                        (
                            col_index * cell_size + cell_border,
                            row_index * cell_size + cell_border,
                        ),
                        (
                            (col_index + 1) * cell_size - cell_border,
                            (row_index + 1) * cell_size - cell_border,
                        ),
                    ],
                    fill=fill,
                )

        output = Path(filename)
        output.parent.mkdir(parents=True, exist_ok=True)
        image.save(output)


def print_result(result: SearchResult) -> None:
    print(f"Algorithm: {result.algorithm}")

    if result.found:
        print("Actions:", "-".join(result.actions))
        print("Path cost:", result.path_cost)
        print("Path length:", result.path_length)
    else:
        print("No solution")

    print("States explored:", result.states_explored)
    print(f"Runtime: {result.runtime_seconds:.6f} seconds")


def image_path_for_algorithm(path: Path, algorithm: str) -> Path:
    safe_algorithm = algorithm.lower().replace("*", "star")
    return path.with_name(f"{path.stem}_{safe_algorithm}{path.suffix}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Solve a text-based grid maze with IDS, A*, or IDA*."
    )
    parser.add_argument("maze", help="Path to the maze text file.")
    parser.add_argument(
        "-a",
        "--algorithm",
        choices=("ids", "astar", "idastar", "all"),
        default="astar",
        help="Search algorithm to run (default: astar).",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Optional maximum IDS depth.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Optional PNG output path.",
    )
    parser.add_argument(
        "--show-explored",
        action="store_true",
        help="Highlight explored states in generated PNG output.",
    )
    parser.add_argument(
        "--hide-maze",
        action="store_true",
        help="Suppress terminal maze printing.",
    )

    args = parser.parse_args()
    maze = Maze(args.maze)

    if not args.hide_maze:
        print("Maze:")
        maze.print_maze()
        print("Solving...\n")

    algorithms = {
        "ids": lambda: maze.ids(args.max_depth),
        "astar": maze.a_star,
        "idastar": maze.ida_star,
    }
    selected = list(algorithms) if args.algorithm == "all" else [args.algorithm]

    for index, name in enumerate(selected):
        result = algorithms[name]()
        print_result(result)

        if result.found and not args.hide_maze:
            print("\nSolution:")
            maze.print_maze()

        if args.output is not None:
            output_path = (
                image_path_for_algorithm(args.output, result.algorithm)
                if len(selected) > 1
                else args.output
            )
            maze.output_image(
                output_path,
                show_solution=True,
                show_explored=args.show_explored,
            )
            print(f"Image saved to: {output_path}")

        if index < len(selected) - 1:
            print("\n" + "-" * 60 + "\n")


if __name__ == "__main__":
    main()
