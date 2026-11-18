import pytest
import numpy as np
from core.kpi.kpi_engine import kpi_registry
from core.kpi.telemetry_adapter import telemetry_service
from core.prediction.traffic_predictor import traffic_predictor
from core.digital_twin.twin_engine import digital_twin
from core.qubo.qubo_engine import qubo_engine
from core.classical.benchmark_engine import classical_benchmarks
from core.security.quantum_secure_module import quantum_secure_module

def test_kpi_calculation():
    # Test RRC SR
    res = kpi_registry.calculate("RAN_RRC_SR", {"rrc_succ": 980, "rrc_att": 1000})
    assert res["value"] == 98.0
    assert res["status"] == "NORMAL"

    # Test PRB Overload critical warning
    res2 = kpi_registry.calculate("RAN_PRB_UTIL_DL", {"used_dl_prb": 260, "total_dl_prb": 273})
    assert res2["value"] > 90.0
    assert res2["status"] == "CRITICAL"

def test_telemetry_generation():
    df = telemetry_service.generate_synthetic_telemetry(num_hours=2, towers=2, cells_per_tower=2)
    assert not df.empty
    assert "prb_utilization" in df.columns
    assert "cell_id" in df.columns
    assert len(df) > 0

def test_digital_twin_topology_and_failure():
    summary = digital_twin.get_topology_summary()
    assert summary["total_towers"] == 4
    assert summary["total_cells"] == 12

    outage = digital_twin.simulate_tower_failure("Tower_01")
    assert outage["failed_tower"] == "Tower_01"
    assert len(outage["affected_cells"]) == 3

def test_qubo_and_classical_benchmarks():
    cells = ["C1", "C2"]
    channels = [1, 2]
    interferences = [(0, 1)]
    q_data = qubo_engine.build_spectrum_allocation_qubo(cells, channels, interferences, penalty=10.0)
    Q = q_data["Q_matrix"]
    assert Q.shape == (4, 4)

    # Brute force solve
    brute = classical_benchmarks.brute_force_solve(Q)
    assert "best_energy" in brute
    assert len(brute["best_bitstring"]) == 4

def test_quantum_secure_pqc_and_qkd():
    pqc = quantum_secure_module.assess_network_cryptographic_inventory()
    assert pqc["total_interfaces"] == 6
    assert pqc["pqc_migration_coverage_percent"] > 0

    qkd = quantum_secure_module.simulate_qkd_link_monitoring(distance_km=10.0)
    assert qkd["qber_percent"] < 11.0
    assert qkd["link_status"] == "OPTIMAL" or qkd["link_status"] == "DEGRADED"
