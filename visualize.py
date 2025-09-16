import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

# Connect to SQLite
conn = sqlite3.connect("logs.db")

# Load logs and alerts into Pandas
df_logs = pd.read_sql_query("SELECT * FROM logs", conn)
df_alerts = pd.read_sql_query("SELECT * FROM alerts", conn)

# --- 1. Log Counts by Level ---
counts_logs = df_logs["level"].value_counts()
plt.bar(counts_logs.index, counts_logs.values, color="skyblue")
plt.title("Log Counts by Level")
plt.xlabel("Log Level")
plt.ylabel("Count")
plt.savefig("log_levels_bar.png")
plt.show()

# --- 2. Alerts by Level ---
if not df_alerts.empty:
    counts_alerts = df_alerts["level"].value_counts()
    plt.bar(counts_alerts.index, counts_alerts.values, color="salmon")
    plt.title("Alerts by Level")
    plt.xlabel("Alert Level")
    plt.ylabel("Count")
    plt.savefig("alerts_bar.png")
    plt.show()
else:
    print("⚠️ No alerts found in database.")

# --- 3. Alerts Over Time ---
if not df_alerts.empty:
    # Convert timestamp column to datetime
    df_alerts["timestamp"] = pd.to_datetime(df_alerts["timestamp"], errors="coerce")

    # Group by timestamp (minute-level aggregation)
    timeline = df_alerts.groupby(df_alerts["timestamp"].dt.strftime("%Y-%m-%d %H:%M")).size()

    plt.plot(timeline.index, timeline.values, marker="o", linestyle="-", color="red")
    plt.xticks(rotation=45, ha="right")
    plt.title("Alerts Over Time")
    plt.xlabel("Time")
    plt.ylabel("Number of Alerts")
    plt.tight_layout()
    plt.savefig("alerts_timeline.png")
    plt.show()
else:
    print("⚠️ No alerts found to plot over time.")

conn.close()
