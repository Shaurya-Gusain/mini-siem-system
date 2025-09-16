import sqlite3
import csv
import re
import os

# Folder containing logs
LOG_FOLDER = "logs"

# Load blacklist (optional file: blacklist.txt)
BLACKLIST_IPS = set()
if os.path.exists("blacklist.txt"):
    with open("blacklist.txt") as f:
        BLACKLIST_IPS = set(line.strip() for line in f if line.strip())

# Connect to SQLite
conn = sqlite3.connect("logs.db")
cursor = conn.cursor()

# Drop old tables (fresh start each run)
cursor.execute("DROP TABLE IF EXISTS logs")
cursor.execute("DROP TABLE IF EXISTS alerts")

# Logs table
cursor.execute("""
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    level TEXT,
    message TEXT,
    user TEXT,
    ip TEXT,
    source_file TEXT
)
""")

# Alerts table
cursor.execute("""
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    level TEXT,
    message TEXT,
    user TEXT,
    ip TEXT,
    source_file TEXT
)
""")

# Regex: handles both normal logs and optional user/IP info
pattern = r"\[(.*?)\]\s+(INFO|ERROR|WARNING|DEBUG|CRITICAL):\s+(.*?)(?:\s+user\s+'(\w+)'(?:\s+from\s+([\d\.]+))?)?$"

# Alert keywords
ALERT_KEYWORDS = ["failed login", "invalid", "unauthorized", "brute force", "critical", "timeout"]

alerts = []

# Process all log files
for filename in os.listdir(LOG_FOLDER):
    if filename.endswith(".log"):
        filepath = os.path.join(LOG_FOLDER, filename)
        with open(filepath, "r") as f:
            for line in f:
                match = re.match(pattern, line.strip())
                if match:
                    timestamp, level, message, user, ip = match.groups()

                    # Insert into logs
                    cursor.execute(
                        "INSERT INTO logs (timestamp, level, message, user, ip, source_file) VALUES (?, ?, ?, ?, ?, ?)",
                        (timestamp, level, message, user, ip, filename)
                    )

                    # Check alert conditions
                    alert_flag = False
                    if level == "CRITICAL":
                        alert_flag = True
                    if any(kw in message.lower() for kw in ALERT_KEYWORDS):
                        alert_flag = True
                    if ip and ip in BLACKLIST_IPS:
                        alert_flag = True

                    # Insert alert
                    if alert_flag:
                        cursor.execute(
                            "INSERT INTO alerts (timestamp, level, message, user, ip, source_file) VALUES (?, ?, ?, ?, ?, ?)",
                            (timestamp, level, message, user, ip, filename)
                        )
                        alerts.append((timestamp, level, message, user, ip, filename))

conn.commit()

# Export logs to CSV
cursor.execute("SELECT timestamp, level, message, user, ip, source_file FROM logs")
rows = cursor.fetchall()
with open("logs.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "level", "message", "user", "ip", "source_file"])
    writer.writerows(rows)

# Export alerts to CSV
with open("alerts.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "level", "message", "user", "ip", "source_file"])
    writer.writerows(alerts)

# Show counts
cursor.execute("SELECT level, COUNT(*) FROM logs GROUP BY level")
print("Log counts by level:", cursor.fetchall())

cursor.execute("SELECT COUNT(*) FROM alerts")
print("🚨 Total alerts generated:", cursor.fetchone()[0])

print("✅ Logs & alerts successfully processed. Check logs.csv and alerts.csv.")

conn.close()
