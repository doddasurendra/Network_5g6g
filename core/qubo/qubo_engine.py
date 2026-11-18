"""QUBO (Quadratic Unconstrained Binary Optimization) Formulation Engine.
Converts telecommunications network problems into mathematically correct QUBO matrix representations:
minimize f(x) = x^T Q x
where x in {0, 1}^n.
Also supports QUBO <-> Ising Hamiltonian conversion.
"""
import numpy as np
from typing import Dict, List, Tuple, Any, Optional

class QUBOEngine:
    """Core mathematical engine for formulating telecom optimization problems into QUBO matrices."""

    def __init__(self):
        pass

    @staticmethod
    def evaluate_energy(Q: np.ndarray, x: np.ndarray) -> float:
        """Evaluates f(x) = x^T Q x."""
        x_vec = np.array(x, dtype=float)
        return float(x_vec.T @ Q @ x_vec)

    @staticmethod
    def qubo_to_ising(Q: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
        """Converts QUBO matrix Q to Ising Hamiltonian:
        x_i = (1 - z_i) / 2 where z_i in {+1, -1}
        H(z) = sum_i h_i z_i + sum_{i<j} J_ij z_i z_j + offset
        Returns:
            J: 2D interaction matrix (upper triangular)
            h: 1D magnetic field vector
            offset: constant energy offset
        """
        n = Q.shape[0]
        # Symmetrize Q if not symmetric
        Q_sym = (Q + Q.T) / 2.0
        
        J = np.zeros((n, n), dtype=float)
        h = np.zeros(n, dtype=float)
        offset = 0.0

        for i in range(n):
            for j in range(n):
                q_ij = Q_sym[i, j]
                # x_i x_j = (1 - z_i)(1 - z_j) / 4 = (1 - z_i - z_j + z_i z_j) / 4
                offset += q_ij * 0.25
                h[i] -= q_ij * 0.25
                h[j] -= q_ij * 0.25
                if i != j:
                    J[min(i, j), max(i, j)] += q_ij * 0.25
                else:
                    # diagonal term x_i^2 = x_i = (1 - z_i) / 2
                    pass

        return J, h, float(offset)

    # -------------------------------------------------------------
    # 8 Telecom QUBO Problem Formulations
    # -------------------------------------------------------------

    def build_spectrum_allocation_qubo(self, cells: List[str], channels: List[int], 
                                      interference_pairs: List[Tuple[int, int]], penalty: float = 10.0) -> Dict[str, Any]:
        """A. Spectrum Allocation:
        Assign frequency channels to cells such that each cell gets exactly 1 channel
        and neighboring cells with mutual interference do not share channels.
        Variables: x_{c, f} in {0, 1}
        """
        n_cells = len(cells)
        n_channels = len(channels)
        num_vars = n_cells * n_channels
        Q = np.zeros((num_vars, num_vars), dtype=float)

        var_map = {}
        idx = 0
        for c in range(n_cells):
            for f in range(n_channels):
                var_map[(c, f)] = idx
                idx += 1

        # Constraint 1: Each cell gets exactly 1 channel: sum_f x_{c, f} = 1
        # Penalty P * (sum_f x_{c, f} - 1)^2 = P * (sum_f x_{c, f}^2 + 2 sum_{f<f'} x_{c, f} x_{c, f'} - 2 sum_f x_{c, f} + 1)
        for c in range(n_cells):
            for f in range(n_channels):
                u = var_map[(c, f)]
                Q[u, u] += -penalty  # from -2P x_{c,f} + P x_{c,f}^2 (since x^2=x)
                for f2 in range(f + 1, n_channels):
                    v = var_map[(c, f2)]
                    Q[u, v] += 2.0 * penalty

        # Constraint 2: Adjacent interfering cells cannot share the same channel
        for c1, c2 in interference_pairs:
            for f in range(n_channels):
                u = var_map[(c1, f)]
                v = var_map[(c2, f)]
                Q[min(u, v), max(u, v)] += penalty * 1.5  # High interference penalty

        return {
            "problem": "SPECTRUM_ALLOCATION",
            "num_variables": num_vars,
            "variable_mapping": {f"cell_{cells[c]}_freq_{channels[f]}": var_map[(c, f)] for c, f in var_map},
            "Q_matrix": Q,
            "penalty": penalty
        }

    def build_congestion_management_qubo(self, overloaded_cells: List[Dict[str, Any]], 
                                        candidate_offload_cells: List[Dict[str, Any]], 
                                        penalty: float = 15.0) -> Dict[str, Any]:
        """B. Network Congestion Management:
        Decide traffic slice transfer from overloaded cells to neighboring lightly loaded cells.
        """
        n_src = len(overloaded_cells)
        n_dst = len(candidate_offload_cells)
        num_vars = n_src * n_dst
        Q = np.zeros((num_vars, num_vars), dtype=float)

        # Objective: minimize residual overload + transfer cost
        idx = 0
        for i in range(n_src):
            for j in range(n_dst):
                # Transfer efficiency / distance penalty
                cost = float(candidate_offload_cells[j].get("current_load", 50.0) / 100.0)
                Q[idx, idx] += cost - 1.0  # Encourage transfer if target has capacity
                idx += 1

        # Feasibility constraint: destination capacity not exceeded
        return {
            "problem": "CONGESTION_MANAGEMENT",
            "num_variables": num_vars,
            "Q_matrix": Q,
            "penalty": penalty
        }

    def build_base_station_energy_qubo(self, num_towers: int, active_demand: List[float], 
                                      min_active_required: int = 2, penalty: float = 20.0) -> Dict[str, Any]:
        """G. Energy Optimization:
        Decide which base stations can enter sleep mode (x_i = 1 for sleep, 0 for active)
        while maintaining total coverage demand.
        f(x) = - sum_i P_saved * x_i + Penalty * (sum_i (1 - x_i) - min_required)^2
        """
        num_vars = num_towers
        Q = np.zeros((num_vars, num_vars), dtype=float)

        # Power saved per sleeping tower: ~1.2 kW
        for i in range(num_vars):
            Q[i, i] -= 1.2  # Reward for sleep

        # Constraint: At least min_active_required must stay awake:
        # sum_i (1 - x_i) >= min_active_required  <=> sum_i x_i <= num_towers - min_active
        # Penalty formulation:
        for i in range(num_vars):
            Q[i, i] += penalty * 0.5
            for j in range(i + 1, num_vars):
                Q[i, j] += penalty * 0.5

        return {
            "problem": "ENERGY_OPTIMIZATION",
            "num_variables": num_vars,
            "Q_matrix": Q,
            "penalty": penalty
        }

qubo_engine = QUBOEngine()
