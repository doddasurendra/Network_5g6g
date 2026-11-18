"""Telecommunications Network Digital Twin.
Constructs a graph topology with NetworkX, simulates traffic variations, tower outages,
fiber cuts, spectrum reallocations, and exports graph state for QUBO optimization.
"""
import networkx as nx
from typing import Dict, List, Any, Optional

class TelecomDigitalTwin:
    """Network Digital Twin representing towers, cells, backhaul links, slices, and user load."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.scenarios: Dict[str, Any] = {}
        self.build_default_topology()

    def build_default_topology(self):
        """Constructs a 4-tower, 12-cell 5G/6G reference network topology."""
        self.graph.clear()
        
        # Core UPF Node
        self.graph.add_node("UPF_CORE", type="CORE", capacity_gbps=100.0, load_gbps=12.5)

        # 4 Towers
        towers = [
            {"id": "Tower_01", "lat": 17.4400, "lon": 78.3489, "power_w": 2800, "status": "ACTIVE"},
            {"id": "Tower_02", "lat": 17.4445, "lon": 78.3530, "power_w": 2650, "status": "ACTIVE"},
            {"id": "Tower_03", "lat": 17.4370, "lon": 78.3560, "power_w": 2700, "status": "ACTIVE"},
            {"id": "Tower_04", "lat": 17.4420, "lon": 78.3620, "power_w": 2500, "status": "ACTIVE"},
        ]

        for tw in towers:
            self.graph.add_node(tw["id"], type="TOWER", **tw)
            # Connect to UPF Core via optical backhaul
            self.graph.add_edge(tw["id"], "UPF_CORE", capacity_gbps=10.0, latency_ms=1.2, load_gbps=2.1, status="UP")
            self.graph.add_edge("UPF_CORE", tw["id"], capacity_gbps=10.0, latency_ms=1.2, load_gbps=2.1, status="UP")

            # 3 Sectors / Cells per Tower
            for c_idx in range(1, 4):
                cell_id = f"{tw['id']}_C{c_idx}"
                freq = "3.5GHz (n78)" if c_idx < 3 else "28GHz (n258 mmWave)"
                prb_total = 273 if c_idx < 3 else 264
                self.graph.add_node(
                    cell_id,
                    type="CELL",
                    tower=tw["id"],
                    frequency=freq,
                    total_prb=prb_total,
                    used_prb=int(prb_total * 0.45),
                    active_users=120,
                    status="ACTIVE",
                    energy_kw=1.8
                )
                # Cell to Tower local bus
                self.graph.add_edge(cell_id, tw["id"], capacity_gbps=2.5, latency_ms=0.3, status="UP")
                self.graph.add_edge(tw["id"], cell_id, capacity_gbps=2.5, latency_ms=0.3, status="UP")

        # Inter-tower Xn interfaces for handover coordination
        pairs = [("Tower_01", "Tower_02"), ("Tower_02", "Tower_03"), ("Tower_03", "Tower_04"), ("Tower_01", "Tower_03")]
        for u, v in pairs:
            self.graph.add_edge(u, v, type="Xn_HANDOVER", capacity_gbps=2.0, latency_ms=2.5, status="UP")
            self.graph.add_edge(v, u, type="Xn_HANDOVER", capacity_gbps=2.0, latency_ms=2.5, status="UP")

    def simulate_tower_failure(self, tower_id: str) -> Dict[str, Any]:
        """Simulates complete outage of a tower and isolates dependent cells."""
        if tower_id not in self.graph:
            return {"error": f"Tower {tower_id} does not exist."}

        self.graph.nodes[tower_id]["status"] = "OFFLINE"
        affected_cells = []
        for n in list(self.graph.nodes):
            if self.graph.nodes[n].get("tower") == tower_id:
                self.graph.nodes[n]["status"] = "OUTAGE"
                affected_cells.append(n)

        # Mark incident links
        for u, v in list(self.graph.edges):
            if u == tower_id or v == tower_id:
                self.graph.edges[u, v]["status"] = "DOWN"

        return {
            "scenario": "TOWER_FAILURE",
            "failed_tower": tower_id,
            "affected_cells": affected_cells,
            "required_remedy": "Traffic offload to adjacent towers via QUBO congestion rebalancing."
        }

    def simulate_congestion_surge(self, target_cell: str, user_multiplier: float = 2.5) -> Dict[str, Any]:
        """Simulates severe localized traffic surge (e.g. stadium event, transit peak)."""
        if target_cell not in self.graph:
            return {"error": f"Cell {target_cell} not found."}

        cell = self.graph.nodes[target_cell]
        orig_users = cell.get("active_users", 100)
        orig_prb = cell.get("used_prb", 100)
        total_prb = cell.get("total_prb", 273)

        new_users = int(orig_users * user_multiplier)
        new_prb = min(total_prb, int(orig_prb * user_multiplier))
        utilization = round((new_prb / total_prb) * 100.0, 2)

        cell["active_users"] = new_users
        cell["used_prb"] = new_prb
        cell["status"] = "CONGESTED" if utilization > 85.0 else "ACTIVE"

        return {
            "scenario": "CONGESTION_SURGE",
            "target_cell": target_cell,
            "active_users": new_users,
            "prb_utilization": utilization,
            "is_overloaded": utilization > 85.0
        }

    def get_topology_summary(self) -> Dict[str, Any]:
        towers = [n for n, d in self.graph.nodes(data=True) if d.get("type") == "TOWER"]
        cells = [n for n, d in self.graph.nodes(data=True) if d.get("type") == "CELL"]
        active_towers = [t for t in towers if self.graph.nodes[t].get("status") == "ACTIVE"]
        congested_cells = [c for c in cells if self.graph.nodes[c].get("status") == "CONGESTED"]

        return {
            "total_towers": len(towers),
            "active_towers": len(active_towers),
            "offline_towers": len(towers) - len(active_towers),
            "total_cells": len(cells),
            "congested_cells": len(congested_cells),
            "congested_cell_ids": congested_cells,
            "total_links": self.graph.number_of_edges(),
            "nodes": [
                {"id": n, **{k: v for k, v in d.items() if isinstance(v, (int, float, str))}}
                for n, d in self.graph.nodes(data=True)
            ]
        }

digital_twin = TelecomDigitalTwin()
