#!/usr/bin/env python3
"""
Diagnostic script for Device Settings telemetry issue
Shows exactly what's happening when the mobile app queries data
"""

from main import SessionLocal, DeviceConfig, DeviceTelemetry, Plant
from datetime import datetime

def diagnose():
    db = SessionLocal()
    
    print("\n" + "="*70)
    print("DEVICE SETTINGS TELEMETRY DIAGNOSTIC")
    print("="*70 + "\n")
    
    device_id = "esp32-plant-01"
    
    # 1. Check if device config exists
    print(f"[STEP 1] Checking device config for: {device_id}")
    config = db.query(DeviceConfig).filter(DeviceConfig.device_id == device_id).first()
    
    if config:
        print(f"  ✅ FOUND Device Config:")
        print(f"     - ID: {config.id}")
        print(f"     - Device ID: {config.device_id}")
        print(f"     - Linked Plant ID: {config.plant_id}")
        print(f"     - Auto Water: {config.auto_water}")
    else:
        print(f"  ❌ NO Device Config found!")
        print(f"     Mobile app needs to save device settings first")
    
    # 2. Check if linked plant exists
    print(f"\n[STEP 2] Checking linked plant")
    if config and config.plant_id:
        plant = db.query(Plant).filter(Plant.id == config.plant_id).first()
        if plant:
            print(f"  ✅ FOUND Plant:")
            print(f"     - ID: {plant.id}")
            print(f"     - Name: {plant.name}")
            print(f"     - Current Moisture: {plant.moisture}%")
        else:
            print(f"  ❌ Plant {config.plant_id} not found!")
    else:
        print(f"  ⚠️  No plant linked to device yet")
        print(f"     (Device config exists but plant_id is None)")
    
    # 3. Check telemetry for this device
    print(f"\n[STEP 3] Checking telemetry for device: {device_id}")
    telemetry = db.query(DeviceTelemetry)\
        .filter(DeviceTelemetry.device_id == device_id)\
        .order_by(DeviceTelemetry.created_at.desc())\
        .limit(10)\
        .all()
    
    if telemetry:
        print(f"  ✅ FOUND {len(telemetry)} telemetry records:")
        for t in telemetry:
            age = (datetime.utcnow() - t.created_at).total_seconds()
            print(f"     - {t.soil_percent}% @ {t.created_at} ({age:.0f}s ago)")
    else:
        print(f"  ❌ NO telemetry records found!")
        print(f"     ESP32 hasn't sent data yet, OR")
        print(f"     Device ID mismatch (check ESP32 code)")
    
    # 4. Check total telemetry in database
    print(f"\n[STEP 4] Checking total telemetry in database")
    total_telem = db.query(DeviceTelemetry).count()
    print(f"  Total telemetry records: {total_telem}")
    
    if total_telem > 0:
        print(f"  Sample devices in database:")
        devices = db.query(DeviceTelemetry.device_id).distinct().all()
        for dev in devices[:5]:
            count = db.query(DeviceTelemetry).filter(DeviceTelemetry.device_id == dev[0]).count()
            print(f"     - {dev[0]}: {count} records")
    else:
        print(f"  No telemetry in database at all!")
        print(f"  → ESP32 has not connected yet")
    
    # 5. What the mobile app will receive
    print(f"\n[STEP 5] What mobile app receives when querying telemetry")
    print(f"  GET /api/iot/telemetry/?device_id={device_id}&limit=10")
    
    print(f"  Response: {len(telemetry)} items")
    if not telemetry:
        print(f"  → Shows empty array in 'Recent Telemetry' section")
    
    print("\n" + "="*70)
    print("DIAGNOSIS SUMMARY")
    print("="*70)
    
    if config:
        print("✅ Device config is saved in backend")
    else:
        print("❌ Device config NOT saved - mobile app didn't send it")
    
    if telemetry:
        print(f"✅ Telemetry data exists ({len(telemetry)} records)")
    else:
        print("❌ NO telemetry data - ESP32 hasn't connected")
    
    print("\n" + "="*70 + "\n")
    
    db.close()

if __name__ == "__main__":
    diagnose()
