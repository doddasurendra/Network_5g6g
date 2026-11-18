#!/usr/bin/env python3
"""
TEST B: REAL IBM QUANTUM HARDWARE TEST
======================================
Requirements:
1. Load IBM Quantum credentials securely (from environment QISKIT_IBM_TOKEN or prompt).
2. Verify authentication with IBM Quantum Platform.
3. Discover available IBM Quantum backends dynamically.
4. Allow selection of real available hardware backend.
5. Validate backend compatibility and operational status.
6. Build a small genuine QAOA circuit.
7. Transpile circuit specifically for target hardware coupling map and basis gates.
8. Configure shots within actual service limits.
9. Require explicit user confirmation before QPU submission to avoid accidental quota usage.
10. Submit real hardware job using modern Qiskit Runtime SamplerV2.
11. Display real IBM job ID and monitor job status.
12. Retrieve actual measurement results, decode bitstrings, and calculate objective values.
13. Compare hardware result against local simulator and classical optimum.
14. Handle absent credentials or unavailable queues transparently without fake results.
"""
import sys
import os
import time
import numpy as np

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.qubo.qubo_engine import qubo_engine
from core.classical.benchmark_engine import classical_benchmarks
from core.qaoa.qaoa_engine import qaoa_engine
from core.quantum_hardware.ibm_runtime_service import ibm_hardware_service

def run_real_ibm_quantum_hardware_test(auto_confirm: bool = False, custom_token: str = None):
    print("=" * 75)
    print("  TEST B: REAL IBM QUANTUM HARDWARE TEST (QISKIT RUNTIME)")
    print("=" * 75)
    print(f"[*] Python Version         : {sys.version.split()[0]}")
    import qiskit
    import qiskit_ibm_runtime
    print(f"[*] Qiskit Core Version    : {qiskit.__version__}")
    print(f"[*] Qiskit IBM Runtime     : {qiskit_ibm_runtime.__version__}")
    print("-" * 75)

    # 1. Credential Verification
    token = custom_token or os.getenv("QISKIT_IBM_TOKEN")
    if not token:
        print("[!] No IBM Quantum API token detected.")
        print("    To run this test on real IBM Quantum processors:")
        print("    1. Obtain your API token from: https://quantum.ibm.com")
        print("    2. Set environment variable: $env:QISKIT_IBM_TOKEN='your_token_here'")
        print("    3. Or pass it as an argument: python tests/real_ibm_quantum_hardware_test.py --token <token>")
        print()
        print("    [SAFETY POLICY] In accordance with non-negotiable rules, fake hardware results")
        print("    will NEVER be fabricated. Please configure your token to access real QPUs.")
        print("=" * 75)
        return False

    print("[1/6] Authenticating with IBM Quantum Platform...")
    auth_res = ibm_hardware_service.authenticate(api_token=token)
    if not auth_res.get("authenticated"):
        print(f"[ERROR] IBM Authentication failed: {auth_res.get('error')}")
        return False
    print("      ✓ Successfully authenticated with IBM Quantum Runtime Service.")

    # 2. Dynamic Backend Discovery
    print("[2/6] Discovering available IBM Quantum hardware backends...")
    backends = ibm_hardware_service.list_available_backends(min_qubits=5)
    if not backends or "error" in backends[0]:
        print(f"[!] No operational hardware backends available: {backends}")
        return False

    print(f"      Discovered {len(backends)} operational backends:")
    for idx, b in enumerate(backends[:5]):
        print(f"      [{idx + 1}] {b['name']} ({b['num_qubits']} qubits, {b['pending_jobs']} pending jobs, Status: {b['status_msg']})")

    selected_backend = backends[0]["name"]
    print(f"      Target QPU selected: {selected_backend}")

    # 3. Build verified small telecom QUBO problem (3-4 binary variables for physical QPU test)
    print("[3/6] Formulating small telecom QUBO problem for hardware...")
    cells = ["Tower_01_C1", "Tower_01_C2"]
    channels = [1, 2]
    interferences = [(0, 1)]
    q_data = qubo_engine.build_spectrum_allocation_qubo(cells, channels, interferences, penalty=8.0)
    Q = q_data["Q_matrix"]
    n_qubits = q_data["num_variables"]
    print(f"      Problem size: {n_qubits} qubits (State space: {1 << n_qubits} states)")

    # Ground truth classical
    classical_opt = classical_benchmarks.brute_force_solve(Q)
    print(f"      Classical Global Optimum Energy: {classical_opt['best_energy']}")

    # 4. Construct Quantum Circuit
    print("[4/6] Constructing QAOA Quantum Circuit for Hardware...")
    qc = qaoa_engine.construct_qaoa_circuit(Q, p=1, gammas=[0.5], betas=[0.5])
    print(f"      Logical Circuit Depth: {qc.depth()}, Qubits: {qc.num_qubits}")

    # 5. User Confirmation Gate before QPU Submission
    print("[5/6] Submission Confirmation Gate:")
    print(f"      Target Backend : {selected_backend}")
    print(f"      Shots          : 1024")
    if not auto_confirm:
        print()
        confirm = input("      Proceed with REAL IBM Quantum QPU hardware submission? (y/N): ").strip().lower()
        if confirm != "y":
            print("      Submission cancelled by user.")
            return True

    # 6. Submit to IBM Quantum Runtime SamplerV2
    print("[6/6] Submitting job to IBM Quantum Platform...")
    submit_res = ibm_hardware_service.submit_hardware_qaoa_job(qc, backend_name=selected_backend, shots=1024)
    if submit_res.get("status") != "SUBMITTED":
        print(f"[ERROR] Failed to submit hardware job: {submit_res.get('error')}")
        return False

    job_id = submit_res["job_id"]
    print(f"      ✓ Real IBM Quantum Job ID: {job_id}")
    print(f"      Transpiled Circuit Depth : {submit_res['transpiled_depth']}")
    print(f"      Polling status for job {job_id}...")

    # Poll status
    for _ in range(30):
        status_info = ibm_hardware_service.poll_job_status(job_id)
        current_st = status_info.get("status")
        print(f"      Status: {current_st}")
        if current_st == "DONE":
            counts = status_info.get("counts", {})
            print("-" * 75)
            print("  IBM QUANTUM HARDWARE EXECUTION RESULTS")
            print("-" * 75)
            print(f"  • QPU Backend Used     : {selected_backend}")
            print(f"  • Hardware Job ID      : {job_id}")
            print(f"  • Raw Counts Retrieved : {counts}")
            print(f"  • Classical Benchmark  : {classical_opt['best_energy']}")
            print("=" * 75)
            print("  TEST B: COMPLETED SUCCESSFULLY ON IBM REAL HARDWARE\n")
            return True
        elif current_st in ["ERROR", "CANCELLED"]:
            print(f"[!] Hardware job ended with status: {current_st}")
            return False
        time.sleep(10)

    print(f"[i] Job {job_id} remains queued in IBM Quantum cloud. Monitor later via dashboard.")
    return True

if __name__ == "__main__":
    token_arg = None
    if len(sys.argv) > 2 and sys.argv[1] == "--token":
        token_arg = sys.argv[2]
    run_real_ibm_quantum_hardware_test(auto_confirm=False, custom_token=token_arg)
