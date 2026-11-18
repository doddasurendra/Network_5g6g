import os
import pandas as pd

p1 = r"C:\Users\LENOVO\.gemini\antigravity\brain\cac43fb8-6f25-4d59-9142-64d75d20f791\.user_uploaded\media_1794986849992_82e3f5e0.csv"
p2 = r"C:\Users\LENOVO\.gemini\antigravity\brain\cac43fb8-6f25-4d59-9142-64d75d20f791\.user_uploaded\media_1794986863199_beca4f88.csv"
p3 = r"C:\Users\LENOVO\.gemini\antigravity\brain\cac43fb8-6f25-4d59-9142-64d75d20f791\.user_uploaded\media_1794986879255_b99a2ae3.csv"
p4 = r"C:\Users\LENOVO\.gemini\antigravity\brain\cac43fb8-6f25-4d59-9142-64d75d20f791\.user_uploaded\media_1794986897501_8ab781fa.csv"

df1 = pd.read_csv(p1)
df1["Tower_ID"] = "Tower_1"

df2 = pd.read_csv(p2)
df2["Tower_ID"] = "Tower_2"

df3 = pd.read_csv(p3)
df3["Tower_ID"] = "Tower_3"

df4 = pd.read_csv(p4)
df4["Tower_ID"] = "Tower_4"

# Also copy the individual files with clean names into data/
data_dir = r"c:\Users\LENOVO\Desktop\Network_5g6g\data"
os.makedirs(data_dir, exist_ok=True)

df1.to_csv(os.path.join(data_dir, "telecom_kpi_Tower1.csv"), index=False)
df2.to_csv(os.path.join(data_dir, "telecom_kpi_Tower2.csv"), index=False)
df3.to_csv(os.path.join(data_dir, "telecom_kpi_Tower3.csv"), index=False)
df4.to_csv(os.path.join(data_dir, "telecom_kpi_Tower4.csv"), index=False)

combined = pd.concat([df1, df2, df3, df4], ignore_index=True)
combined.to_csv(os.path.join(data_dir, "telecom_kpi_all_towers.csv"), index=False)

print(f"Total Combined Rows: {len(combined)}")
print(f"Columns: {list(combined.columns)}")
print("Distribution per Tower:")
print(combined["Tower_ID"].value_counts())
print("\nCongestion value counts:")
print(combined["Congestion"].value_counts())
print("\nFirst 3 rows:")
print(combined.head(3))
