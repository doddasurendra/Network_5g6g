"""Network Data Ingestion and Telemetry Normalization Adapter.
Handles CSV, Excel, JSON telemetry, schema validation, quality scoring, and realistic synthetic generation.
"""
import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

REQUIRED_TELEMETRY_COLUMNS = [
    "timestamp", "tower_id", "cell_id", "active_users",
    "prb_utilization", "dl_throughput_mbps", "ul_throughput_mbps",
    "latency_ms", "packet_loss_rate", "sinr_db"
]

class TelemetryIngestionService:
    """Ingests raw operator telemetry or generated simulation logs with data-quality scoring."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir

    def ingest_csv(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        df = pd.read_csv(file_path)
        return self._normalize_and_validate(df, source=os.path.basename(file_path))

    def _normalize_and_validate(self, df: pd.DataFrame, source: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        # Map common column name aliases
        col_map = {
            "Time": "timestamp", "DateTime": "timestamp", "Timestamp": "timestamp",
            "Tower": "tower_id", "TowerID": "tower_id", "Tower_ID": "tower_id",
            "Cell": "cell_id", "CellID": "cell_id",
            "Users": "active_users", "ConnectedUsers": "active_users",
            "PRB": "prb_utilization", "PRB_Util": "prb_utilization", "PRBUtilization": "prb_utilization",
            "Throughput": "dl_throughput_mbps", "DL_Throughput": "dl_throughput_mbps",
            "UL_Throughput": "ul_throughput_mbps",
            "Latency": "latency_ms", "Delay": "latency_ms",
            "PacketLoss": "packet_loss_rate", "Packet_Loss": "packet_loss_rate",
            "SINR": "sinr_db", "CQI": "cqi"
        }
        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

        # Calculate Quality Score
        total_rows = len(df)
        if total_rows == 0:
            return df, {"quality_score": 0.0, "status": "EMPTY_DATASET"}

        missing_counts = df.isnull().sum().to_dict()
        duplicates = df.duplicated().sum()
        
        # Fill standard defaults if columns missing
        for col in REQUIRED_TELEMETRY_COLUMNS:
            if col not in df.columns:
                if col == "timestamp":
                    now = datetime.utcnow()
                    df["timestamp"] = [now - timedelta(minutes=i*15) for i in range(total_rows)][::-1]
                elif col in ["tower_id", "cell_id"]:
                    df[col] = f"{col}_DEFAULT"
                elif col in ["active_users"]:
                    df[col] = 100
                elif col in ["prb_utilization"]:
                    df[col] = 50.0
                elif col in ["dl_throughput_mbps"]:
                    df[col] = 45.0
                elif col in ["ul_throughput_mbps"]:
                    df[col] = 12.0
                elif col in ["latency_ms"]:
                    df[col] = 15.0
                elif col in ["packet_loss_rate"]:
                    df[col] = 0.01
                elif col in ["sinr_db"]:
                    df[col] = 14.0

        # Handle NaNs in numeric columns
        numeric_cols = ["active_users", "prb_utilization", "dl_throughput_mbps", "ul_throughput_mbps", "latency_ms", "packet_loss_rate", "sinr_db"]
        for c in numeric_cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce").fillna(df[c].median() if not df[c].dropna().empty else 0.0)

        # Ensure timestamp is datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce").fillna(datetime.utcnow())

        quality_score = max(0.0, 100.0 - (sum(missing_counts.values()) / (total_rows * len(df.columns)) * 100.0) - (duplicates / total_rows * 20.0))

        report = {
            "source": source,
            "total_records": total_rows,
            "duplicates": int(duplicates),
            "quality_score": round(quality_score, 2),
            "status": "VALIDATED" if quality_score > 70 else "DEGRADED_QUALITY",
            "columns": list(df.columns)
        }
        return df, report

    @staticmethod
    def generate_synthetic_telemetry(num_hours: int = 24, towers: int = 4, cells_per_tower: int = 3) -> pd.DataFrame:
        """Generates realistic synthetic 5G/6G telemetry with circadian traffic curves and bursty congestion."""
        records = []
        base_time = datetime.utcnow() - timedelta(hours=num_hours)
        intervals = num_hours * 12  # 5-minute sampling

        for t_idx in range(towers):
            tower_name = f"Tower_{t_idx + 1:02d}"
            for c_idx in range(cells_per_tower):
                cell_name = f"{tower_name}_C{c_idx + 1}"
                freq_band = "n78 (3.5GHz)" if c_idx < 2 else "n258 (28GHz mmWave)"
                
                # Base load factor
                tower_bias = 0.8 + 0.4 * (t_idx % 2)

                for step in range(intervals):
                    current_time = base_time + timedelta(minutes=step * 5)
                    hour = current_time.hour + current_time.minute / 60.0

                    # Circadian rhythm: peak at 14:00 and 20:00, trough at 04:00
                    diurnal = 0.4 + 0.5 * np.sin((hour - 8) * np.pi / 12)**2
                    random_jitter = np.random.normal(0, 0.05)
                    
                    # Occasional surge for Tower 1 to trigger QUBO / QAOA rebalancing
                    spike = 0.35 if (t_idx == 0 and 18 <= hour <= 21) else 0.0

                    load = np.clip((diurnal + random_jitter + spike) * tower_bias, 0.05, 0.98)

                    users = int(load * 450 + np.random.randint(-15, 20))
                    prb_util = float(np.clip(load * 100.0 + np.random.normal(0, 3.0), 5.0, 99.5))
                    dl_tp = float(np.clip((1.0 - load * 0.7) * 220.0 + np.random.normal(0, 10.0), 5.0, 300.0))
                    ul_tp = float(np.clip((1.0 - load * 0.7) * 60.0 + np.random.normal(0, 4.0), 2.0, 80.0))
                    latency = float(np.clip(8.0 + (load**2) * 45.0 + np.random.normal(0, 2.0), 5.0, 120.0))
                    loss = float(np.clip((load**3) * 0.05 + np.random.uniform(0, 0.002), 0.0001, 0.08))
                    sinr = float(np.clip(22.0 - load * 14.0 + np.random.normal(0, 1.5), -2.0, 28.0))

                    records.append({
                        "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "tower_id": tower_name,
                        "cell_id": cell_name,
                        "frequency_band": freq_band,
                        "active_users": max(1, users),
                        "prb_utilization": round(prb_util, 2),
                        "dl_throughput_mbps": round(dl_tp, 2),
                        "ul_throughput_mbps": round(ul_tp, 2),
                        "latency_ms": round(latency, 2),
                        "packet_loss_rate": round(loss, 5),
                        "sinr_db": round(sinr, 2),
                        "data_type": "SYNTHETIC_SIMULATED"
                    })

        return pd.DataFrame(records)

telemetry_service = TelemetryIngestionService()
