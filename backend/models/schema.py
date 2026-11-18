"""SQLAlchemy data models for telecommunications network entities, metrics, AI, and Quantum optimization."""
import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from backend.models.database import Base

class Operator(Base):
    __tablename__ = "operators"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    mcc = Column(String(10), nullable=True)  # Mobile Country Code
    mnc = Column(String(10), nullable=True)  # Mobile Network Code
    country = Column(String(50), default="Global")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    towers = relationship("Tower", back_populates="operator")

class Tower(Base):
    __tablename__ = "towers"
    id = Column(Integer, primary_key=True, index=True)
    tower_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, default=30.0)
    power_source = Column(String(50), default="Grid+Solar")
    status = Column(String(20), default="ACTIVE")  # ACTIVE, DEGRADED, OFFLINE, SLEEP
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    operator = relationship("Operator", back_populates="towers")
    cells = relationship("Cell", back_populates="tower")

class Cell(Base):
    __tablename__ = "cells"
    id = Column(Integer, primary_key=True, index=True)
    cell_id = Column(String(50), unique=True, index=True, nullable=False)
    tower_id = Column(Integer, ForeignKey("towers.id"), nullable=False)
    technology = Column(String(20), default="5G_NR")  # 4G_LTE, 5G_NR_SA, 5G_NR_NSA, 6G_RESEARCH
    frequency_band = Column(String(50), default="n78 (3.5 GHz)")
    bandwidth_mhz = Column(Float, default=100.0)
    total_prbs = Column(Integer, default=273)
    azimuth = Column(Float, default=0.0)
    electrical_tilt = Column(Float, default=2.0)
    status = Column(String(20), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    tower = relationship("Tower", back_populates="cells")
    kpi_records = relationship("KPIRecord", back_populates="cell")

class KPIRecord(Base):
    __tablename__ = "kpi_records"
    id = Column(Integer, primary_key=True, index=True)
    cell_id = Column(Integer, ForeignKey("cells.id"), nullable=False)
    timestamp = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    
    # Radio & Performance
    prb_utilization = Column(Float, default=0.0)
    dl_throughput_mbps = Column(Float, default=0.0)
    ul_throughput_mbps = Column(Float, default=0.0)
    latency_ms = Column(Float, default=0.0)
    packet_loss_rate = Column(Float, default=0.0)
    sinr_db = Column(Float, default=0.0)
    rsrp_dbm = Column(Float, default=-95.0)
    rsrq_db = Column(Float, default=-10.0)
    cqi = Column(Float, default=10.0)
    active_users = Column(Integer, default=0)
    connected_users = Column(Integer, default=0)
    handover_success_rate = Column(Float, default=99.0)
    energy_consumption_kwh = Column(Float, default=1.5)
    
    # Extended metrics storage (JSON for arbitrary 100+ KPIs)
    metrics = Column(JSON, nullable=True)
    
    cell = relationship("Cell", back_populates="kpi_records")

class AIModelRecord(Base):
    __tablename__ = "ai_models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    target_metric = Column(String(50), nullable=False)
    model_type = Column(String(50), nullable=False)
    horizon_minutes = Column(Integer, default=30)
    mae = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    mape = Column(Float, nullable=True)
    model_path = Column(String(255), nullable=True)
    status = Column(String(20), default="READY")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class QuantumJobRecord(Base):
    __tablename__ = "quantum_jobs"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100), unique=True, index=True, nullable=False)
    execution_type = Column(String(50), nullable=False)  # CLASSICAL_BASELINE, QISKIT_AER, IBM_QUANTUM_HARDWARE
    backend_name = Column(String(100), nullable=False)
    problem_type = Column(String(100), nullable=False)
    qubits = Column(Integer, default=0)
    shots = Column(Integer, default=1024)
    qaoa_depth = Column(Integer, default=1)
    status = Column(String(50), default="SUBMITTED")  # SUBMITTED, QUEUED, RUNNING, COMPLETED, FAILED
    objective_value = Column(Float, nullable=True)
    is_feasible = Column(Boolean, default=True)
    execution_time_seconds = Column(Float, default=0.0)
    best_bitstring = Column(String(255), nullable=True)
    solution_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DigitalTwinScenario(Base):
    __tablename__ = "digital_twin_scenarios"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    scenario_type = Column(String(50), default="PEAK_TRAFFIC")
    parameters = Column(JSON, nullable=True)
    simulated_kpi_impact = Column(JSON, nullable=True)
    status = Column(String(20), default="CREATED")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
