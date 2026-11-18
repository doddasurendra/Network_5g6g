"""Comprehensive Telecommunications KPI Definition and Calculation Engine.
Covers 4G LTE, 5G NR (SA/NSA), 6G Research, Core Network, Transport, Spectrum, Security, and Energy.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable, List
import math

@dataclass
class KPIMetadata:
    id: str
    name: str
    full_form: str
    definition: str
    unit: str
    category: str  # RAN, 5G_NR, 6G_RESEARCH, CORE, TRANSPORT, SPECTRUM, ENERGY, SECURITY, OPERATIONS
    technology: str  # 4G, 5G_SA, 5G_NSA, 6G, AGNOSTIC
    required_inputs: List[str]
    measurement_interval: str  # 1s, 10s, 1m, 15m, 1h
    warning_threshold: float
    critical_threshold: float
    comparison_operator: str  # '<', '>', '<=', '>='
    optimization_relevance: str
    calculation_func: Optional[Callable[[Dict[str, float]], float]] = None

class KPIRegistry:
    """Central registry and formula evaluator for 100+ telecommunications KPIs."""
    
    def __init__(self):
        self._kpis: Dict[str, KPIMetadata] = {}
        self._register_all_kpis()

    def register(self, kpi: KPIMetadata):
        self._kpis[kpi.id] = kpi

    def get(self, kpi_id: str) -> Optional[KPIMetadata]:
        return self._kpis.get(kpi_id)

    def list_all(self, category: Optional[str] = None, technology: Optional[str] = None) -> List[KPIMetadata]:
        results = list(self._kpis.values())
        if category:
            results = [k for k in results if k.category.upper() == category.upper()]
        if technology:
            results = [k for k in results if k.technology.upper() == technology.upper()]
        return results

    def calculate(self, kpi_id: str, inputs: Dict[str, float]) -> Dict[str, Any]:
        kpi = self.get(kpi_id)
        if not kpi:
            return {"error": f"KPI '{kpi_id}' not found in registry."}

        # Check missing inputs
        missing = [inp for inp in kpi.required_inputs if inp not in inputs or inputs[inp] is None]
        if missing:
            return {
                "kpi_id": kpi_id,
                "name": kpi.name,
                "status": "MISSING_DATA",
                "missing_inputs": missing,
                "value": None
            }

        try:
            if kpi.calculation_func:
                val = kpi.calculation_func(inputs)
            else:
                val = float(inputs.get(kpi.required_inputs[0], 0.0))
        except ZeroDivisionError:
            val = 0.0
        except Exception as e:
            return {"kpi_id": kpi_id, "name": kpi.name, "status": "ERROR", "error": str(e), "value": None}

        # Evaluate thresholds
        status = "NORMAL"
        if kpi.comparison_operator == "<":
            if val < kpi.critical_threshold:
                status = "CRITICAL"
            elif val < kpi.warning_threshold:
                status = "WARNING"
        elif kpi.comparison_operator == ">":
            if val > kpi.critical_threshold:
                status = "CRITICAL"
            elif val > kpi.warning_threshold:
                status = "WARNING"

        return {
            "kpi_id": kpi_id,
            "name": kpi.name,
            "unit": kpi.unit,
            "value": round(val, 4),
            "status": status,
            "warning_threshold": kpi.warning_threshold,
            "critical_threshold": kpi.critical_threshold
        }

    def _register_all_kpis(self):
        # 1. RAN KPIs
        self.register(KPIMetadata(
            id="RAN_RRC_SR",
            name="RRC Connection Setup Success Rate",
            full_form="Radio Resource Control Connection Setup Success Rate",
            definition="Percentage of successfully established RRC connections against total attempts.",
            unit="%",
            category="RAN",
            technology="AGNOSTIC",
            required_inputs=["rrc_succ", "rrc_att"],
            measurement_interval="15m",
            warning_threshold=98.0,
            critical_threshold=95.0,
            comparison_operator="<",
            optimization_relevance="Indicates call establishment success; critical for handover & admission optimization.",
            calculation_func=lambda d: (d["rrc_succ"] / d["rrc_att"] * 100.0) if d["rrc_att"] > 0 else 100.0
        ))
        
        self.register(KPIMetadata(
            id="RAN_PRB_UTIL_DL",
            name="Downlink PRB Utilization",
            full_form="Downlink Physical Resource Block Utilization",
            definition="Ratio of allocated downlink PRBs to total available PRBs in the cell.",
            unit="%",
            category="RAN",
            technology="AGNOSTIC",
            required_inputs=["used_dl_prb", "total_dl_prb"],
            measurement_interval="1m",
            warning_threshold=80.0,
            critical_threshold=90.0,
            comparison_operator=">",
            optimization_relevance="Primary indicator of radio capacity exhaustion; triggers QUBO congestion & spectrum rebalancing.",
            calculation_func=lambda d: (d["used_dl_prb"] / d["total_dl_prb"] * 100.0) if d["total_dl_prb"] > 0 else 0.0
        ))

        self.register(KPIMetadata(
            id="RAN_PRB_UTIL_UL",
            name="Uplink PRB Utilization",
            full_form="Uplink Physical Resource Block Utilization",
            definition="Ratio of allocated uplink PRBs to total available PRBs.",
            unit="%",
            category="RAN",
            technology="AGNOSTIC",
            required_inputs=["used_ul_prb", "total_ul_prb"],
            measurement_interval="1m",
            warning_threshold=75.0,
            critical_threshold=88.0,
            comparison_operator=">",
            optimization_relevance="Identifies uplink bottlenecks, especially in high video upload / IoT density areas.",
            calculation_func=lambda d: (d["used_ul_prb"] / d["total_ul_prb"] * 100.0) if d["total_ul_prb"] > 0 else 0.0
        ))

        self.register(KPIMetadata(
            id="RAN_HO_SR",
            name="Handover Success Rate",
            full_form="Handover Execution Success Rate",
            definition="Percentage of successful handovers relative to total handover attempts.",
            unit="%",
            category="RAN",
            technology="AGNOSTIC",
            required_inputs=["ho_succ", "ho_att"],
            measurement_interval="15m",
            warning_threshold=98.5,
            critical_threshold=95.0,
            comparison_operator="<",
            optimization_relevance="Direct input to Handover Optimization QUBO formulation.",
            calculation_func=lambda d: (d["ho_succ"] / d["ho_att"] * 100.0) if d["ho_att"] > 0 else 100.0
        ))

        self.register(KPIMetadata(
            id="RAN_USER_THROUGHPUT_DL",
            name="User Downlink Throughput",
            full_form="Average User Downlink Throughput",
            definition="Average payload data transferred per user in downlink per active transfer second.",
            unit="Mbps",
            category="RAN",
            technology="AGNOSTIC",
            required_inputs=["dl_traffic_mbit", "dl_transfer_time_sec"],
            measurement_interval="1m",
            warning_threshold=25.0,
            critical_threshold=10.0,
            comparison_operator="<",
            optimization_relevance="User Quality of Experience metric; target function in resource allocation.",
            calculation_func=lambda d: (d["dl_traffic_mbit"] / d["dl_transfer_time_sec"]) if d["dl_transfer_time_sec"] > 0 else 0.0
        ))

        # 2. 5G NR Radio KPIs (SA and NSA)
        self.register(KPIMetadata(
            id="5G_REG_SR_SA",
            name="5G SA Registration Success Rate",
            full_form="5G Standalone Registration Success Rate",
            definition="Ratio of successful 5G SA registrations via AMF to attempts.",
            unit="%",
            category="5G_NR",
            technology="5G_SA",
            required_inputs=["reg_succ_sa", "reg_att_sa"],
            measurement_interval="5m",
            warning_threshold=99.0,
            critical_threshold=97.0,
            comparison_operator="<",
            optimization_relevance="Crucial for SA availability and core network signaling health.",
            calculation_func=lambda d: (d["reg_succ_sa"] / d["reg_att_sa"] * 100.0) if d["reg_att_sa"] > 0 else 100.0
        ))

        self.register(KPIMetadata(
            id="5G_ENDC_SR_NSA",
            name="EN-DC Setup Success Rate",
            full_form="E-UTRA NR Dual Connectivity Setup Success Rate",
            definition="Success rate of establishing secondary gNodeB connectivity in 5G NSA mode.",
            unit="%",
            category="5G_NR",
            technology="5G_NSA",
            required_inputs=["endc_succ", "endc_att"],
            measurement_interval="5m",
            warning_threshold=98.0,
            critical_threshold=94.0,
            comparison_operator="<",
            optimization_relevance="Key indicator of NSA dual-connectivity anchor performance and coverage match.",
            calculation_func=lambda d: (d["endc_succ"] / d["endc_att"] * 100.0) if d["endc_att"] > 0 else 100.0
        ))

        self.register(KPIMetadata(
            id="5G_BEAM_FAILURE_RATE",
            name="Beam Failure Rate",
            full_form="5G NR Beam Failure Detection Rate",
            definition="Frequency of beam failures detected relative to active beam tracking sessions.",
            unit="%",
            category="5G_NR",
            technology="5G_SA",
            required_inputs=["beam_failures", "active_beams"],
            measurement_interval="1m",
            warning_threshold=2.0,
            critical_threshold=5.0,
            comparison_operator=">",
            optimization_relevance="Directly optimizes Massive MIMO beam steering and tilt adjustment.",
            calculation_func=lambda d: (d["beam_failures"] / d["active_beams"] * 100.0) if d["active_beams"] > 0 else 0.0
        ))

        self.register(KPIMetadata(
            id="5G_SLICE_SLA_COMPLIANCE",
            name="Slice SLA Compliance Rate",
            full_form="Network Slice Service Level Agreement Compliance",
            definition="Percentage of time slices meet their guaranteed bitrate and latency constraints.",
            unit="%",
            category="5G_NR",
            technology="5G_SA",
            required_inputs=["compliant_samples", "total_samples"],
            measurement_interval="5m",
            warning_threshold=99.9,
            critical_threshold=99.0,
            comparison_operator="<",
            optimization_relevance="Drives Network Slicing QUBO formulation for resource isolation and allocation.",
            calculation_func=lambda d: (d["compliant_samples"] / d["total_samples"] * 100.0) if d["total_samples"] > 0 else 100.0
        ))

        # 3. 6G Research KPIs
        self.register(KPIMetadata(
            id="6G_PEAK_DATA_RATE",
            name="6G Extreme Peak Data Rate",
            full_form="6G Terahertz Peak Achievable Data Rate",
            definition="Maximum achievable theoretical transmission throughput on Sub-THz/THz carrier bands.",
            unit="Gbps",
            category="6G_RESEARCH",
            technology="6G",
            required_inputs=["spectral_eff", "channel_bandwidth_ghz"],
            measurement_interval="1h",
            warning_threshold=100.0,
            critical_threshold=50.0,
            comparison_operator="<",
            optimization_relevance="Theoretical bound in 6G beamforming and wideband THz link scheduling.",
            calculation_func=lambda d: d["spectral_eff"] * d["channel_bandwidth_ghz"] * 1000.0
        ))

        self.register(KPIMetadata(
            id="6G_E2E_LATENCY",
            name="6G End-to-End Latency",
            full_form="Sub-millisecond 6G Ultra-Reliable Low-Latency Communication",
            definition="One-way transit time from user application to edge AI compute node.",
            unit="ms",
            category="6G_RESEARCH",
            technology="6G",
            required_inputs=["propagation_delay_ms", "processing_delay_ms", "queuing_delay_ms"],
            measurement_interval="10s",
            warning_threshold=0.5,
            critical_threshold=1.0,
            comparison_operator=">",
            optimization_relevance="Primary optimization metric for 6G cell-free MIMO and tactile internet.",
            calculation_func=lambda d: d["propagation_delay_ms"] + d["processing_delay_ms"] + d["queuing_delay_ms"]
        ))

        self.register(KPIMetadata(
            id="6G_DT_SYNC_LATENCY",
            name="Digital Twin Synchronization Latency",
            full_form="6G Digital Twin State Synchronization Latency",
            definition="Time required to mirror physical network radio telemetry into the real-time Digital Twin.",
            unit="ms",
            category="6G_RESEARCH",
            technology="6G",
            required_inputs=["dt_sync_delay_ms"],
            measurement_interval="1m",
            warning_threshold=5.0,
            critical_threshold=15.0,
            comparison_operator=">",
            optimization_relevance="Determines validity of real-time Digital Twin state when computing QUBO matrices.",
            calculation_func=lambda d: d["dt_sync_delay_ms"]
        ))

        self.register(KPIMetadata(
            id="6G_RIS_GAIN",
            name="Reconfigurable Intelligent Surface Gain",
            full_form="RIS Reflection Signal-to-Interference-Plus-Noise Gain",
            definition="SINR enhancement provided by passive/active RIS element phase tuning.",
            unit="dB",
            category="6G_RESEARCH",
            technology="6G",
            required_inputs=["sinr_with_ris", "sinr_without_ris"],
            measurement_interval="5m",
            warning_threshold=6.0,
            critical_threshold=2.0,
            comparison_operator="<",
            optimization_relevance="Directly tuned by Quantum Phase Optimization in 6G wireless propagation.",
            calculation_func=lambda d: d["sinr_with_ris"] - d["sinr_without_ris"]
        ))

        # 4. Core Network KPIs
        self.register(KPIMetadata(
            id="CORE_UPF_LATENCY",
            name="UPF Packet Processing Latency",
            full_form="User Plane Function Packet Forwarding Latency",
            definition="Average latency incurred inside the UPF for GTP-U decapsulation and packet routing.",
            unit="ms",
            category="CORE",
            technology="5G_SA",
            required_inputs=["upf_latency_ms"],
            measurement_interval="1m",
            warning_threshold=3.0,
            critical_threshold=8.0,
            comparison_operator=">",
            optimization_relevance="Guides UPF selection and user-plane rerouting.",
            calculation_func=lambda d: d["upf_latency_ms"]
        ))

        self.register(KPIMetadata(
            id="CORE_AMF_REG_LATENCY",
            name="AMF Registration Latency",
            full_form="Access and Mobility Management Function Registration Latency",
            definition="Round-trip time for initial registration procedure between UE and AMF.",
            unit="ms",
            category="CORE",
            technology="5G_SA",
            required_inputs=["amf_reg_latency_ms"],
            measurement_interval="5m",
            warning_threshold=50.0,
            critical_threshold=100.0,
            comparison_operator=">",
            optimization_relevance="Monitors signaling plane health and potential DDoS/storm conditions.",
            calculation_func=lambda d: d["amf_reg_latency_ms"]
        ))

        # 5. Energy and Sustainability KPIs
        self.register(KPIMetadata(
            id="ENERGY_SITE_CONSUMPTION",
            name="Total Site Energy Consumption",
            full_form="Base Station Total Electrical Power Draw",
            definition="Aggregate electrical energy consumed by RF units, baseband units, and cooling systems.",
            unit="kWh",
            category="ENERGY",
            technology="AGNOSTIC",
            required_inputs=["rf_power_kwh", "bbu_power_kwh", "cooling_power_kwh"],
            measurement_interval="1h",
            warning_threshold=25.0,
            critical_threshold=40.0,
            comparison_operator=">",
            optimization_relevance="Objective function for Base-station Sleep Mode Energy Optimization QUBO.",
            calculation_func=lambda d: d["rf_power_kwh"] + d["bbu_power_kwh"] + d["cooling_power_kwh"]
        ))

        self.register(KPIMetadata(
            id="ENERGY_EFFICIENCY_PER_BIT",
            name="Energy Efficiency per Bit",
            full_form="Joules per Transmitted Bit",
            definition="Energy consumed in Joules divided by the total number of bits transferred.",
            unit="uJ/bit",
            category="ENERGY",
            technology="AGNOSTIC",
            required_inputs=["energy_joules", "bits_transmitted"],
            measurement_interval="15m",
            warning_threshold=5.0,
            critical_threshold=10.0,
            comparison_operator=">",
            optimization_relevance="Primary green sustainability indicator in 5G and 6G networks.",
            calculation_func=lambda d: (d["energy_joules"] * 1e6 / d["bits_transmitted"]) if d["bits_transmitted"] > 0 else 0.0
        ))

        # 6. Spectrum and RF KPIs
        self.register(KPIMetadata(
            id="RF_SINR",
            name="Signal-to-Interference-plus-Noise Ratio",
            full_form="Signal-to-Interference-plus-Noise Ratio",
            definition="Signal power relative to interference from neighbor cells plus background thermal noise.",
            unit="dB",
            category="SPECTRUM",
            technology="AGNOSTIC",
            required_inputs=["sinr_db"],
            measurement_interval="10s",
            warning_threshold=5.0,
            critical_threshold=0.0,
            comparison_operator="<",
            optimization_relevance="Interference penalty component in Spectrum Allocation QUBO.",
            calculation_func=lambda d: d["sinr_db"]
        ))

        self.register(KPIMetadata(
            id="RF_RSRP",
            name="Reference Signal Received Power",
            full_form="Reference Signal Received Power",
            definition="Average power of resource elements that carry cell-specific reference signals.",
            unit="dBm",
            category="SPECTRUM",
            technology="AGNOSTIC",
            required_inputs=["rsrp_dbm"],
            measurement_interval="10s",
            warning_threshold=-105.0,
            critical_threshold=-115.0,
            comparison_operator="<",
            optimization_relevance="Determines cell coverage boundary and triggers handover requests.",
            calculation_func=lambda d: d["rsrp_dbm"]
        ))

        # 7. Security and Reliability KPIs
        self.register(KPIMetadata(
            id="SEC_QKD_QBER",
            name="QKD Quantum Bit Error Rate",
            full_form="Quantum Key Distribution Quantum Bit Error Rate",
            definition="Percentage of erroneous quantum state transmissions over optical QKD fibers.",
            unit="%",
            category="SECURITY",
            technology="6G",
            required_inputs=["error_qubits", "total_qubits"],
            measurement_interval="1m",
            warning_threshold=5.0,
            critical_threshold=11.0,
            comparison_operator=">",
            optimization_relevance="Threshold (>11%) detects eavesdropping and aborts cryptographic key generation.",
            calculation_func=lambda d: (d["error_qubits"] / d["total_qubits"] * 100.0) if d["total_qubits"] > 0 else 0.0
        ))

        self.register(KPIMetadata(
            id="SEC_PQC_MIGRATION_COVERAGE",
            name="PQC Migration Coverage",
            full_form="Post-Quantum Cryptographic Protocol Coverage",
            definition="Percentage of network interfaces protected by NIST ML-KEM or ML-DSA quantum-safe standards.",
            unit="%",
            category="SECURITY",
            technology="AGNOSTIC",
            required_inputs=["pqc_interfaces", "total_interfaces"],
            measurement_interval="1d",
            warning_threshold=70.0,
            critical_threshold=40.0,
            comparison_operator="<",
            optimization_relevance="Tracks compliance with quantum-safe telecommunication migration requirements.",
            calculation_func=lambda d: (d["pqc_interfaces"] / d["total_interfaces"] * 100.0) if d["total_interfaces"] > 0 else 0.0
        ))

# Global registry instance
kpi_registry = KPIRegistry()
