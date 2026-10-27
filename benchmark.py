"""Benchmark IDS, A*, and IDA* on the included example mazes."""

from pathlib import Path

from src.maze import Maze


def main() -> None:
    examples = Path(__file__).parent / "examples"
    maze_files = sorted(examples.glob("maze*.txt"))

    print(
        f"{'Maze':<12} {'Algorithm':<10} {'Found':<7} "
        f"{'Path':>6} {'Explored':>10} {'Runtime (s)':>12}"
    )
    print("-" * 67)

    algorithms = [
        ("IDS", "ids"),
        ("A*", "a_star"),
        ("IDA*", "ida_star"),
    ]

    for maze_file in maze_files:
        for algorithm_name, method_name in algorithms:
            maze = Maze(maze_file)
            result = getattr(maze, method_name)()
            path = str(result.path_length) if result.path_length is not None else "-"

            print(
                f"{maze_file.name:<12} {algorithm_name:<10} {str(result.found):<7} "
                f"{path:>6} {result.states_explored:>10} "
                f"{result.runtime_seconds:>12.6f}"
            )


if __name__ == "__main__":
    main()
