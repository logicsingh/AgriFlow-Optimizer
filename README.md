# AgriFlow Optimizer

**MCA Semester I — Design and Analysis of Algorithms mini-project**

AgriFlow is an educational irrigation-network optimizer. It represents a farm's water source, junctions and fields as a weighted, undirected graph, then demonstrates minimum spanning trees, shortest paths and dynamic programming through a small local web dashboard.

> **Scope:** All network and crop data are synthetic. Results are for algorithm-learning and demonstration only; they are not hydraulic designs or agronomic recommendations.

## Features

- **Prim's and Kruskal's algorithms:** construct a minimum spanning tree (MST) for the candidate pipeline network.
- **Dijkstra's algorithm:** finds a minimum-weight route between two selected nodes.
- **0/1 Knapsack:** selects fields under a limited daily water budget using illustrative crop-priority scores.
- **Objective comparison:** evaluate pipeline length, estimated loss index, pumping energy, or a demonstrative combined score.
- **Benchmark view:** compare Prim and Kruskal on the same small graph.
- **Interactive dashboard:** inspect the network, selected pipelines, routes and allocation results in a browser.

## Requirements

- Python 3.9 or later
- A modern web browser
- No third-party Python packages and no internet connection required at runtime

## Run locally

1. Extract the project archive.
2. Open a terminal in the project directory.
3. Start the local server with `python server.py` (on Windows, `py server.py` is also supported).
4. Open [http://127.0.0.1:8000](http://127.0.0.1:8000).
5. Explore the pipeline network, water schedule and algorithm benchmark tabs.
6. Stop the server with `Ctrl+C`.

The server binds to `127.0.0.1` (localhost); it is intended for local demonstration, not public production hosting.

## Run tests

From the project directory:

```bash
python -m unittest discover -s tests -v
```

The test suite checks graph data, MST connectivity and agreement between Prim and Kruskal, Dijkstra path costs, and the optimality and budget constraints of the knapsack allocation.

## Algorithms and complexity

Let `V` be the number of graph vertices, `E` the number of candidate pipelines, `n` the number of field choices and `W` the integer water budget.

| Component | Technique | Time complexity |
|---|---|---|
| Minimum spanning tree | Kruskal + sorting + disjoint-set union | `O(E log E)` |
| Minimum spanning tree | Prim with adjacency list and binary heap | `O(E log V)` |
| Shortest path | Dijkstra with binary heap | `O((V + E) log V)` |
| Water allocation | 0/1 Knapsack dynamic programming | `O(nW)` |

Dijkstra is appropriate because all supported edge weights are non-negative. The knapsack implementation uses `O(W)` score storage plus a decision table for reconstruction.

## Edge-weight objectives

- `length`: pipeline length in metres.
- `loss`: `length × loss percentage / 100`, reported as an estimated loss index in metres.
- `energy`: assumed daily pumping energy in kWh.
- `balanced`: `length + 35 × loss percentage + 18 × daily energy`. This is an illustrative weighted score, not a standard engineering unit.

The MST algorithms minimize the selected edge-weight objective. The dashboard separately reports physical pipeline length, estimated loss index, energy and the minimum individual edge capacity in the selected tree. These metrics are not a hydraulic flow calculation.

## Data assumptions and limitations

Node coordinates, elevations, pipeline lengths, loss rates, capacities, energy figures, daily crop requirements and priority scores are synthetic teaching data. The network is small and illustrative. The loss index is not a hydraulic simulation. The application does not model pipe diameter, pressure, friction head, pump curves, soil moisture, evapotranspiration, rainfall forecasts, crop growth stages, water rights, valve constraints or real-terrain GIS. The schematic map is not to scale. Do not use its output as an engineering design or agronomic recommendation.

## Suggested demonstration

1. Run Prim and Kruskal with the `length` objective. Both should select `V - 1` edges and return the same MST cost.
2. Compare the `loss`, `energy` and `balanced` objectives.
3. Find a route from `RES` to `F05` using Dijkstra.
4. Generate water schedules for budgets such as 60, 90 and 120 m³/day.
5. Compare benchmark timings, noting that measurements on this small graph are illustrative and hardware-dependent.

## License

No license has been specified. Unless a license is added, the repository remains under default copyright terms; reuse is not automatically granted.
