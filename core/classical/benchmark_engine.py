"""Classical Optimization Benchmarks for Telecom QUBO Problems.
Implements:
1. Brute-Force / Exhaustive Search (for <= 20 variables)
2. Simulated Annealing
3. Classical Greedy / Heuristic Search
Provides rigorous benchmark baselines for comparing QAOA and IBM hardware.
"""
import time
import numpy as np
from typing import Dict, Any, List, Optional

class ClassicalBenchmarkEngine:
    """Classical baseline solvers for QUBO energy minimization."""

    @staticmethod
    def brute_force_solve(Q: np.ndarray) -> Dict[str, Any]:
        """Exhaustive evaluation of all 2^n binary configurations. Guaranteed global optimum."""
        n = Q.shape[0]
        if n > 22:
            return {"error": f"Brute force infeasible for n={n} > 22 variables."}

        start_time = time.time()
        best_energy = float("inf")
        best_bitstring = None
        evaluations = 1 << n

        for i in range(evaluations):
            # Convert integer to binary array
            x = np.array([(i >> bit) & 1 for bit in range(n)], dtype=float)
            energy = float(x.T @ Q @ x)
            if energy < best_energy:
                best_energy = energy
                best_bitstring = "".join(str(int(b)) for b in x)

        elapsed = time.time() - start_time
        return {
            "solver": "BRUTE_FORCE_GLOBAL_OPTIMUM",
            "best_energy": round(best_energy, 6),
            "best_bitstring": best_bitstring,
            "evaluations": evaluations,
            "execution_time_seconds": round(elapsed, 4)
        }

    @staticmethod
    def simulated_annealing_solve(Q: np.ndarray, initial_temp: float = 100.0, 
                                  cooling_rate: float = 0.98, max_steps: int = 2000) -> Dict[str, Any]:
        """Simulated Annealing metaheuristic for QUBO."""
        n = Q.shape[0]
        start_time = time.time()
        
        # Random initial state
        current_x = np.random.randint(0, 2, size=n).astype(float)
        current_energy = float(current_x.T @ Q @ current_x)
        
        best_x = current_x.copy()
        best_energy = current_energy
        temp = initial_temp
        evals = 0

        for step in range(max_steps):
            evals += 1
            # Flip a random bit
            flip_idx = np.random.randint(0, n)
            candidate_x = current_x.copy()
            candidate_x[flip_idx] = 1.0 - candidate_x[flip_idx]
            
            candidate_energy = float(candidate_x.T @ Q @ candidate_x)
            delta_e = candidate_energy - current_energy

            if delta_e < 0 or np.random.rand() < np.exp(-delta_e / max(temp, 1e-8)):
                current_x = candidate_x
                current_energy = candidate_energy
                if current_energy < best_energy:
                    best_energy = current_energy
                    best_x = current_x.copy()

            temp *= cooling_rate
            if temp < 1e-4:
                break

        elapsed = time.time() - start_time
        return {
            "solver": "SIMULATED_ANNEALING",
            "best_energy": round(best_energy, 6),
            "best_bitstring": "".join(str(int(b)) for b in best_x),
            "evaluations": evals,
            "execution_time_seconds": round(elapsed, 4)
        }

    @staticmethod
    def greedy_heuristic_solve(Q: np.ndarray) -> Dict[str, Any]:
        """Fast greedy single-bit flip descent."""
        n = Q.shape[0]
        start_time = time.time()
        
        x = np.zeros(n, dtype=float)
        current_energy = 0.0
        evals = 0

        improved = True
        while improved:
            improved = False
            for i in range(n):
                evals += 1
                cand = x.copy()
                cand[i] = 1.0 - cand[i]
                e = float(cand.T @ Q @ cand)
                if e < current_energy:
                    current_energy = e
                    x = cand
                    improved = True

        elapsed = time.time() - start_time
        return {
            "solver": "GREEDY_HEURISTIC",
            "best_energy": round(current_energy, 6),
            "best_bitstring": "".join(str(int(b)) for b in x),
            "evaluations": evals,
            "execution_time_seconds": round(elapsed, 4)
        }

classical_benchmarks = ClassicalBenchmarkEngine()
