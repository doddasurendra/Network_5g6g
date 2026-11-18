"""Genuine QAOA (Quantum Approximate Optimization Algorithm) Engine using Qiskit.
Builds parameterized quantum circuits with Cost Hamiltonian and Mixer Hamiltonian.
Executes circuits on local quantum simulators (Qiskit Aer / Statevector / AerSimulator).
"""
import time
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from scipy.optimize import minimize

try:
    from qiskit import QuantumCircuit
    from qiskit.circuit import ParameterVector
    from qiskit_aer import AerSimulator
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False

class QAOAEngine:
    """Production QAOA Engine for combinatorial optimization."""

    def __init__(self):
        self.simulator = AerSimulator() if QISKIT_AVAILABLE else None

    def construct_qaoa_circuit(self, Q: np.ndarray, p: int = 1, 
                               gammas: Optional[List[float]] = None, 
                               betas: Optional[List[float]] = None) -> Any:
        """Constructs a genuine parameterized QAOA circuit for QUBO matrix Q.
        H_C = sum_{i} Q_{ii} (I - Z_i)/2 + sum_{i<j} Q_{ij} (I - Z_i)(I - Z_j)/4
        H_M = sum_i X_i
        """
        if not QISKIT_AVAILABLE:
            raise RuntimeError("Qiskit is not available in environment.")

        n = Q.shape[0]
        qc = QuantumCircuit(n, n)

        # 1. Initial State: Equal superposition |+>^n
        for q in range(n):
            qc.h(q)

        # 2. Alternating Operator Ansatz for p layers
        for layer in range(p):
            gamma = gammas[layer] if gammas is not None else 0.5
            beta = betas[layer] if betas is not None else 0.5

            # Problem Cost Unitary U(H_C, gamma) = e^{-i * gamma * H_C}
            # Diagonal terms: RZ rotation
            for i in range(n):
                coeff = Q[i, i]
                if abs(coeff) > 1e-6:
                    qc.rz(gamma * coeff, i)

            # Quadratic terms: RZZ rotation via CNOT - RZ - CNOT
            for i in range(n):
                for j in range(i + 1, n):
                    coeff = Q[i, j] + Q[j, i]
                    if abs(coeff) > 1e-6:
                        qc.cx(i, j)
                        qc.rz(gamma * coeff * 0.5, j)
                        qc.cx(i, j)

            # Mixer Unitary U(H_M, beta) = e^{-i * beta * sum_i X_i}
            for i in range(n):
                qc.rx(2.0 * beta, i)

        # 3. Measurement
        qc.measure(range(n), range(n))
        return qc

    def execute_simulator(self, Q: np.ndarray, p: int = 1, shots: int = 1024, 
                          optimizer_method: str = "COBYLA", max_iter: int = 30) -> Dict[str, Any]:
        """Runs QAOA optimization using local AerSimulator.
        Optimizes variational parameters (gamma, beta) classically.
        """
        if not QISKIT_AVAILABLE:
            raise RuntimeError("Qiskit / Qiskit Aer is required for simulator execution.")

        start_time = time.time()
        n = Q.shape[0]
        simulator = AerSimulator()

        convergence_history = []

        def objective_func(params):
            gammas = params[:p]
            betas = params[p:]
            qc = self.construct_qaoa_circuit(Q, p=p, gammas=gammas, betas=betas)
            result = simulator.run(qc, shots=shots).result()
            counts = result.get_counts()

            # Compute expectation energy
            total_energy = 0.0
            total_shots = sum(counts.values())
            for bitstr, count in counts.items():
                # Qiskit bitstring order is reversed: bitstr[0] is q_{n-1}
                x = np.array([int(b) for b in reversed(bitstr)], dtype=float)
                e = float(x.T @ Q @ x)
                total_energy += e * count

            avg_energy = total_energy / total_shots
            convergence_history.append(avg_energy)
            return avg_energy

        # Initial random parameters
        initial_params = np.random.uniform(0, np.pi, size=2*p)

        opt_res = minimize(
            objective_func,
            initial_params,
            method=optimizer_method,
            options={"maxiter": max_iter}
        )

        best_params = opt_res.x
        final_qc = self.construct_qaoa_circuit(Q, p=p, gammas=best_params[:p], betas=best_params[p:])
        final_result = simulator.run(final_qc, shots=shots).result()
        final_counts = final_result.get_counts()

        # Extract best measured bitstring
        best_measured_energy = float("inf")
        best_bitstring = None
        for bitstr, count in final_counts.items():
            x = np.array([int(b) for b in reversed(bitstr)], dtype=float)
            e = float(x.T @ Q @ x)
            if e < best_measured_energy:
                best_measured_energy = e
                best_bitstring = "".join(str(int(b)) for b in x)

        elapsed = time.time() - start_time

        return {
            "execution_type": "QISKIT_AER_SIMULATOR",
            "qubits": n,
            "qaoa_depth_p": p,
            "shots": shots,
            "optimizer": optimizer_method,
            "iterations": len(convergence_history),
            "best_objective_value": round(best_measured_energy, 6),
            "best_bitstring": best_bitstring,
            "measurement_counts": final_counts,
            "convergence_history": convergence_history,
            "circuit_depth": final_qc.depth(),
            "gate_count": dict(final_qc.count_ops()),
            "execution_time_seconds": round(elapsed, 4)
        }

qaoa_engine = QAOAEngine()
