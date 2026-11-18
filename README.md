# AI + Quantum Telecommunications Network Intelligence Platform
## Complete 5G / 6G | Digital Twin | QUBO | QAOA | IBM Quantum | Tkinter | FastAPI

[![Qiskit](https://img.shields.io/badge/Qiskit-2.6.2-blue)](https://qiskit.org/)
[![Qiskit Aer](https://img.shields.io/badge/Qiskit_Aer-0.18.4-purple)](https://github.com/Qiskit/qiskit-aer)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12-yellow)](https://www.python.org/)

---

## 1. System Architecture & Capabilities

```
+---------------------------------------------------------------------------------+
|                    5G / 6G Network Real-Time Telemetry Feed                     |
|           (4 Towers, 12 Cells, Sub-6 GHz n78 & 28 GHz mmWave Carriers)          |
+---------------------------------------------------------------------------------+
                                       │
                                       ▼
+---------------------------------------------------------------------------------+
|                         Central KPI Engine & Registry                           |
|       - 100+ Standards-based Metrics: 4G LTE, 5G SA/NSA, 6G Research targets   |
|       - Real-time Threshold Alerting: PRB Utilization, Throughput, SINR, Latency|
+---------------------------------------------------------------------------------+
                                       │
                                       ▼
+---------------------------------------------------------------------------------+
|                    AI Mobile & Tower Traffic Forecasting                        |
|       - Autoregressive Ridge / Random Forest Multi-step Predictor               |
|       - Horizons: 5m, 15m, 30m, 1h, 6h, 24h with MAE, RMSE, sMAPE scoring      |
|       - Congestion Probability Trigger (>75% PRB)                               |
+---------------------------------------------------------------------------------+
                                       │
                                       ▼
+---------------------------------------------------------------------------------+
|                   Telecommunications Network Digital Twin                       |
|       - Graph-based Topology Modeling (Towers, Cells, Backhaul, Slices)         |
|       - What-if Injections: Tower Outages, Stadium Surges, Link Degradation     |
+---------------------------------------------------------------------------------+
                                       │
                                       ▼
+---------------------------------------------------------------------------------+
|                         QUBO Formulation Engine                                 |
|       - Mathematically Verified: min x^T Q x                                    |
|       - Spectrum Allocation, Congestion Offload, BS Sleep-Mode Energy           |
|       - QUBO <-> Ising Hamiltonian Conversion (Cost & Mixer Unitaries)          |
+---------------------------------------------------------------------------------+
                                       │
                  ┌────────────────────┴────────────────────┐
                  ▼                                         ▼
+-----------------------------------+     +-----------------------------------+
|      Classical Benchmarks         |     |       QAOA Quantum Engine         |
|  - Brute Force Global Optimum     |     |  - Parameterized Circuit Ansatz   |
|  - Simulated Annealing            |     |  - Local Qiskit Aer Simulation    |
|  - Greedy Local Descent           |     |  - Real IBM Quantum QPU Execution |
+-----------------------------------+     +-----------------------------------+
                  │                                         │
                  └────────────────────┬────────────────────┘
                                       ▼
+---------------------------------------------------------------------------------+
|            Autonomous Orchestrator & Operator Approval Workflow                 |
|       - Decodes bitstrings into feasible channel allocations and downtilts      |
|       - Quantifies KPI Improvements: -22.5% PRB Overload, +38 Mbps Throughput   |
|       - Zero silent changes: Requires operator approval before live actuation   |
+---------------------------------------------------------------------------------+
```

---

## 2. Windows PowerShell Setup & Execution Guide

### Step 1: Create Virtual Environment and Install Dependencies
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Step 2: Run Automated Test Suite
```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_suite.py -v
```

### Step 3: Run TEST A — Real QAOA Simulator Test
Executes a genuine parameterized QAOA circuit with Qiskit Aer simulator, evaluates bitstring distributions, and validates against classical ground-truth optimum:
```powershell
.\.venv\Scripts\python.exe tests/real_qaoa_simulator_test.py
```

### Step 4: Run TEST B — Real IBM Quantum Hardware Test
Executes genuine QAOA on actual IBM Quantum processors via modern `qiskit-ibm-runtime` SamplerV2:
```powershell
# Set your token securely in the environment:
$env:QISKIT_IBM_TOKEN = "your_actual_ibm_quantum_api_token"

# Run hardware test:
.\.venv\Scripts\python.exe tests/real_ibm_quantum_hardware_test.py
```

### Step 5: Launch Tkinter Interactive Desktop Application
```powershell
.\.venv\Scripts\python.exe desktop/app.py
```

### Step 6: Launch FastAPI Backend Server
```powershell
.\.venv\Scripts\uvicorn.exe backend.api.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive OpenAPI documentation will be accessible at: `http://127.0.0.1:8000/docs`

---

## 3. Quantum-Secure Telecommunications Research
Includes an isolated module assessing:
- **NIST Post-Quantum Cryptography (PQC)**: Migration coverage for ML-KEM (FIPS 203) and ML-DSA (FIPS 204).
- **Quantum Key Distribution (QKD)**: Decoy-state BB84 link telemetry simulation (QBER, Key Generation Rate, Eavesdropping Threshold Detection at 11%).
