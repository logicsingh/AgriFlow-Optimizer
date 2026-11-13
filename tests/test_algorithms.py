import itertools
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import EDGES, G, NODES, irrigation_schedule, kruskal, mst_result, prim, shortest_path


class IrrigationTests(unittest.TestCase):
    def test_graph_data_references_known_nodes_and_positive_weights(self):
        self.assertGreater(len(NODES), 0)
        self.assertGreater(len(EDGES), 0)
        for edge in EDGES:
            self.assertIn(edge["u"], NODES)
            self.assertIn(edge["v"], NODES)
            self.assertGreater(edge["length"], 0)
            self.assertGreaterEqual(edge["loss"], 0)
            self.assertGreaterEqual(edge["energy"], 0)
            self.assertGreaterEqual(edge["capacity"], 0)

    def test_mst_connects_every_node(self):
        for algorithm in (kruskal, prim):
            edges, _, _ = algorithm("length")
            self.assertEqual(len(edges), len(NODES) - 1)
            self.assertEqual(len({node for edge in edges for node in (edge["u"], edge["v"])}), len(NODES))

    def test_prim_and_kruskal_costs_match_for_all_objectives(self):
        for objective in ("length", "loss", "energy", "balanced"):
            self.assertAlmostEqual(kruskal(objective)[1], prim(objective)[1], places=7)

    def test_dijkstra_path_has_valid_edges_and_cost(self):
        path, cost, _, expanded = shortest_path("RES", "F05", "length")
        self.assertEqual(path[0], "RES")
        self.assertEqual(path[-1], "F05")
        self.assertGreater(cost, 0)
        self.assertGreater(expanded, 0)
        path_cost = 0
        for start, end in zip(path, path[1:]):
            edge = next(edge for edge in G[start] if edge[0] == end)[1]
            path_cost += edge["length"]
        self.assertEqual(path_cost, cost)

    def test_dijkstra_returns_zero_cost_for_same_node(self):
        path, cost, _, _ = shortest_path("RES", "RES", "length")
        self.assertEqual(path, ["RES"])
        self.assertEqual(cost, 0)

    def test_schedule_respects_budget_and_matches_exhaustive_optimum(self):
        crops = [(node, data) for node, data in NODES.items() if data["type"] == "field"]
        for budget in (0, 40, 60, 90, 120, 150, 200):
            result = irrigation_schedule(budget)
            self.assertLessEqual(result["allocated_m3"], budget)
            self.assertEqual(result["allocated_m3"], sum(item["water_m3"] for item in result["selected"]))
            best_score = 0
            for selection in itertools.product((False, True), repeat=len(crops)):
                used = sum(int(data["need"]) for selected, (_, data) in zip(selection, crops) if selected)
                score = sum(int(data["need"] * data["priority"]) for selected, (_, data) in zip(selection, crops) if selected)
                if used <= budget:
                    best_score = max(best_score, score)
            self.assertEqual(result["total_crop_priority_score"], best_score)

    def test_mst_api_shape(self):
        result = mst_result("Kruskal", "length")
        self.assertTrue(result["connected"])
        self.assertEqual(len(result["edges"]), len(NODES) - 1)
        self.assertEqual(result["algorithm"], "Kruskal")


if __name__ == "__main__":
    unittest.main(verbosity=2)
