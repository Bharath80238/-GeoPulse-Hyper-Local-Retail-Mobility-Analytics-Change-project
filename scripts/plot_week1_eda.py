import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
# Project paths
base = Path(__file__).resolve().parent.parent
reports = base / "reports" / "week1"
charts = reports / "charts"
charts.mkdir(parents=True, exist_ok=True)
# Load analysis files
top = pd.read_csv(reports / "top_10_busiest_sensors.csv")
hourly = pd.read_csv(reports / "hourly_activity.csv")
daily = pd.read_csv(reports / "day_wise_activity.csv")
# 1. Top 10 busiest sensors
top = top.sort_values("Total_Pedestrian_Count", ascending=True)
plt.figure(figsize=(12, 7))
plt.barh(top["Sensor_Name"], top["Total_Pedestrian_Count"])
plt.title("Top 10 Busiest Pedestrian Sensors")
plt.xlabel("Total Pedestrian Count")
plt.ylabel("Sensor Name")
plt.tight_layout()
plt.savefig(charts / "top_10_busiest_sensors.png", dpi=300)
plt.close()
# 2. Hourly pedestrian activity
hourly = hourly.sort_values("Hour")
plt.figure(figsize=(12, 6))
plt.bar(hourly["Hour"], hourly["Total_Count"])
plt.title("Hourly Pedestrian Activity")
plt.xlabel("Hour of Day")
plt.ylabel("Total Pedestrian Count")
plt.xticks(range(24))
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(charts / "hourly_pedestrian_activity.png", dpi=300)
plt.close()
# 3. Day-wise pedestrian activity
daily = daily.sort_values("Total_Count", ascending=False)
plt.figure(figsize=(10, 6))
plt.bar(daily["Day"], daily["Total_Count"])
plt.title("Day-wise Pedestrian Activity")
plt.xlabel("Day of Week")
plt.ylabel("Total Pedestrian Count")
plt.xticks(rotation=30)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(charts / "day_wise_pedestrian_activity.png", dpi=300)
plt.close()
print("Week 1 visualizations generated successfully!")
for file in sorted(charts.glob("*.png")):
    print(file.name, "-", file.stat().st_size, "bytes")
