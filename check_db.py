import sqlite3

conn = sqlite3.connect('fastapi.db')
c = conn.cursor()

# Check plants
print("=== PLANTS ===")
c.execute("SELECT id, name, owner_id, moisture FROM plants LIMIT 10")
plants = c.fetchall()
if plants:
    for p in plants:
        print(f"Plant ID: {p[0]}, Name: {p[1]}, Owner: {p[2]}, Moisture: {p[3]}%")
else:
    print("No plants found")

# Check device config
print("\n=== DEVICE CONFIG ===")
c.execute("SELECT device_id, plant_id FROM device_config")
configs = c.fetchall()
if configs:
    for cfg in configs:
        print(f"Device: {cfg[0]}, Plant ID: {cfg[1]}")
else:
    print("No device config found")

# Check latest telemetry
print("\n=== LATEST TELEMETRY (last 5) ===")
c.execute("SELECT device_id, plant_id, soil_percent, created_at FROM device_telemetry ORDER BY created_at DESC LIMIT 5")
telemetry = c.fetchall()
if telemetry:
    for t in telemetry:
        print(f"Device: {t[0]}, Plant: {t[1]}, Moisture: {t[2]}%, Time: {t[3]}")
else:
    print("No telemetry found")

conn.close()
