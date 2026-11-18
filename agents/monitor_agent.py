import pandas as pd

def detect_poor_network(file_path):

    df = pd.read_csv(file_path)
    bad_rows = []

    for idx, row in df.iterrows():

        issues = []

        if row["Latency"] > 100:
            issues.append("High Latency")

        if row["PacketLoss"] > 5:
            issues.append("High Packet Loss")

        if row["SINR"] < 5:
            issues.append("Low SINR")

        if row["RSRQ"] < -15:
            issues.append("Poor Signal Quality")

        if row["Throughput"] < 20:
            issues.append("Low Throughput")

        if row["CQI"] < 5:
            issues.append("Low CQI")

        if row["Congestion"] == 1:
            issues.append("Network Congestion")

        if issues:
            bad_rows.append({
                "row_index": idx,
                "data": row.to_dict(),
                "issues": issues
            })

    return bad_rows