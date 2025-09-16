# Mini SIEM System 🛡️

A Python-based mini Security Information and Event Management (SIEM) tool.  
This project parses log files, stores them in a SQLite database, generates alerts for suspicious activities, and visualizes logs & alerts with Matplotlib.  

---

## 📌 Features
- Parse log files from applications, authentication, databases, and servers
- Store logs in SQLite for easy querying
- Generate alerts for:
  - CRITICAL level events
  - Failed logins / invalid credentials / brute force attempts
  - Suspicious IP addresses (from `blacklist.txt`)
- Export logs and alerts to CSV
- Visualize:
  - Log distribution by level
  - Alert distribution by level
  - Alerts over time (timeline)
