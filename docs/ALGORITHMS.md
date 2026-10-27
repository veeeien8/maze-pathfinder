# Algorithm Notes

## Search problem formulation

The maze is modelled as a state-space search problem.

- **State:** the agent's current `(row, column)` coordinate.
- **Initial state:** the cell marked `A`.
- **Actions:** `U`, `D`, `L`, and `R`.
- **Transition model:** move one cell in the chosen direction when the destination cell is inside the maze and is not a wall.
- **Goal test:** the current state equals the location of `B`.
- **Path cost:** every movement costs one unit.

## Iterative Deepening Search (IDS)

IDS repeatedly performs depth-limited depth-first search. It begins at depth 0 and raises the limit until a solution is found.

Its main advantage is low memory usage compared with breadth-first search, but shallow states are revisited across iterations. The original assignment implementation used a fixed maximum depth of 50. The portfolio version removes that arbitrary cutoff and, by default, uses the number of traversable cells to derive a safe finite maximum for a simple path.

## A* Search

A* ranks frontier nodes using:

```text
f(n) = g(n) + h(n)
```

where:

- `g(n)` is the exact cost from the start to node `n`.
- `h(n)` estimates the remaining cost to the goal.

This project uses Manhattan distance:

```text
h(n) = |row - goal_row| + |column - goal_column|
```

For a four-direction, unit-cost grid, Manhattan distance is admissible because it never overestimates the minimum number of horizontal and vertical moves needed to reach the goal. It is also consistent because moving to one adjacent cell changes the Manhattan distance by at most one.

## Iterative Deepening A* (IDA*)

IDA* combines A*'s `f = g + h` evaluation with iterative deepening. Instead of a depth limit, each search iteration uses an `f`-cost threshold.

Nodes whose `f` value exceeds the current threshold are postponed. If no goal is found, the smallest exceeded `f` value becomes the next threshold.

This can use much less frontier memory than A*, but repeated iterations may expand the same states multiple times.

## Comparison

| Algorithm | Search type | Heuristic | Main trade-off |
| --- | --- | --- | --- |
| IDS | Uninformed | No | Low memory, repeated exploration |
| A* | Informed | Manhattan distance | Strong guidance, larger frontier memory |
| IDA* | Informed | Manhattan distance | Lower memory than A*, repeated threshold searches |
