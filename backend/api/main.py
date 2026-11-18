"""FastAPI Backend Application exposing all Core Intelligence & Optimization Services."""
import os
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Query, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from backend.api.dashboard_html import DASHBOARD_HTML

from core.kpi.kpi_engine import kpi_registry
from core.kpi.telemetry_adapter import telemetry_service
from core.prediction.traffic_predictor import traffic_predictor
from core.digital_twin.twin_engine import digital_twin
from core.qubo.qubo_engine import qubo_engine
from core.classical.benchmark_engine import classical_benchmarks
from core.qaoa.qaoa_engine import qaoa_engine
from core.quantum_hardware.ibm_runtime_service import ibm_hardware_service
from core.prediction.orchestrator import orchestration_pipeline
from core.security.quantum_secure_module import quantum_secure_module

app = FastAPI(
    title="AI + Quantum Telecommunications Intelligence Platform",
    description="Comprehensive 5G/6G Network Monitoring, Digital Twin, QUBO, QAOA, and IBM Quantum Runtime Backend",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Visual Interactive Dashboard -----------------
@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def get_visual_dashboard():
    return HTMLResponse(content=DASHBOARD_HTML)

@app.post("/api/desktop/launch")
def launch_desktop_gui():
    import threading
    from desktop.app import TelecomIntelligenceApp
    def _run():
        try:
            app = TelecomIntelligenceApp()
            app.mainloop()
        except Exception as e:
            print(f"Tkinter desktop error: {e}")
    threading.Thread(target=_run, daemon=True).start()
    return {"status": "SUCCESS", "message": "Desktop Tkinter application initiated."}

# ----------------- Health & Status -----------------
@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": "Telecom-AI-Quantum-Platform",
        "qiskit_available": getattr(qaoa_engine, "simulator", None) is not None,
        "ibm_runtime_authenticated": ibm_hardware_service._authenticated
    }

# ----------------- KPI Management & Calculation -----------------
@app.get("/api/kpis")
def get_kpis(category: Optional[str] = None, technology: Optional[str] = None):
    kpis = kpi_registry.list_all(category=category, technology=technology)
    return [
        {
            "id": k.id, "name": k.name, "full_form": k.full_form,
            "category": k.category, "technology": k.technology,
            "unit": k.unit, "interval": k.measurement_interval,
            "warning_threshold": k.warning_threshold,
            "critical_threshold": k.critical_threshold,
            "relevance": k.optimization_relevance
        }
        for k in kpis
    ]

@app.post("/api/kpis/{kpi_id}/calculate")
def calculate_kpi(kpi_id: str, inputs: Dict[str, float] = Body(...)):
    res = kpi_registry.calculate(kpi_id, inputs)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

# ----------------- Telemetry & Digital Twin -----------------
@app.get("/api/telemetry/live")
def get_live_telemetry(hours: int = 12):
    df = telemetry_service.generate_synthetic_telemetry(num_hours=hours, towers=4)
    return df.to_dict(orient="records")

@app.get("/api/digital-twin/topology")
def get_digital_twin_topology():
    return digital_twin.get_topology_summary()

@app.post("/api/digital-twin/simulate/failure")
def simulate_tower_failure(tower_id: str = Query(...)):
    return digital_twin.simulate_tower_failure(tower_id)

@app.post("/api/digital-twin/simulate/congestion")
def simulate_congestion(target_cell: str = Query(...), multiplier: float = 2.0):
    return digital_twin.simulate_congestion_surge(target_cell, user_multiplier=multiplier)

# ----------------- AI Traffic & Congestion Prediction -----------------
@app.post("/api/ai/predict")
def predict_traffic(cell_id: str = Query("Tower_01_C1"), metric: str = "prb_utilization", horizon_minutes: int = 30):
    df = telemetry_service.generate_synthetic_telemetry(num_hours=24, towers=4)
    cell_df = df[df["cell_id"] == cell_id]
    if cell_df.empty:
        raise HTTPException(status_code=404, detail=f"Cell {cell_id} not found in telemetry.")
    return traffic_predictor.fit_and_predict(cell_df, target_col=metric, horizon_minutes=horizon_minutes)

# ----------------- QUBO & Classical Benchmarks -----------------
@app.get("/api/qubo/formulate/spectrum")
def formulate_spectrum_qubo(penalty: float = 12.0):
    cells = ["Tower_01_C1", "Tower_01_C2", "Tower_02_C1", "Tower_02_C2"]
    channels = [1, 2]
    interferences = [(0, 1), (1, 2), (2, 3)]
    res = qubo_engine.build_spectrum_allocation_qubo(cells, channels, interferences, penalty=penalty)
    return {
        "problem": res["problem"],
        "num_variables": res["num_variables"],
        "Q_matrix_preview": res["Q_matrix"].tolist()
    }

@app.post("/api/qubo/solve/classical")
def solve_classical(problem_type: str = "SPECTRUM"):
    cells = ["Tower_01_C1", "Tower_01_C2", "Tower_02_C1", "Tower_02_C2"]
    channels = [1, 2]
    interferences = [(0, 1), (1, 2), (2, 3)]
    res = qubo_engine.build_spectrum_allocation_qubo(cells, channels, interferences)
    Q = res["Q_matrix"]
    
    brute = classical_benchmarks.brute_force_solve(Q)
    annealing = classical_benchmarks.simulated_annealing_solve(Q)
    return {
        "problem": problem_type,
        "brute_force_optimum": brute,
        "simulated_annealing": annealing
    }

# ----------------- QAOA Simulator Execution -----------------
@app.post("/api/quantum/qaoa/simulator")
def run_qaoa_simulator(shots: int = 1024, p: int = 1):
    cells = ["Tower_01_C1", "Tower_01_C2", "Tower_02_C1", "Tower_02_C2"]
    channels = [1, 2]
    interferences = [(0, 1), (1, 2), (2, 3)]
    res = qubo_engine.build_spectrum_allocation_qubo(cells, channels, interferences)
    Q = res["Q_matrix"]
    try:
        return qaoa_engine.execute_simulator(Q, p=p, shots=shots, max_iter=15)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------- IBM Quantum Real Hardware -----------------
class IBMAthenticateRequest(BaseModel):
    api_token: str
    channel: str = "ibm_quantum"

@app.post("/api/quantum/ibm/authenticate")
def authenticate_ibm(req: IBMAthenticateRequest):
    return ibm_hardware_service.authenticate(api_token=req.api_token, channel=req.channel)

@app.get("/api/quantum/ibm/backends")
def list_ibm_backends():
    return ibm_hardware_service.list_available_backends()

@app.get("/api/quantum/ibm/jobs/{job_id}")
def check_ibm_job(job_id: str):
    return ibm_hardware_service.poll_job_status(job_id)

# ----------------- End-to-End Autonomous Orchestration -----------------
@app.post("/api/orchestrator/run-cycle")
def run_orchestration_cycle(target_cell: str = Query("Tower_01_C1"), backend: str = Query("AER_SIMULATOR")):
    return orchestration_pipeline.run_automated_optimization_cycle(target_cell=target_cell, execution_backend=backend)

# ----------------- Quantum-Secure Module -----------------
@app.get("/api/security/pqc/inventory")
def get_pqc_inventory():
    return quantum_secure_module.assess_network_cryptographic_inventory()

@app.get("/api/security/qkd/link-monitoring")
def get_qkd_monitoring(distance_km: float = 12.5):
    return quantum_secure_module.simulate_qkd_link_monitoring(distance_km=distance_km)
