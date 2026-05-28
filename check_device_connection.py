#!/usr/bin/env python3
"""
IoT Device Connection Diagnostic Script
Run this in your fast-api folder to check device connections
"""

from main import SessionLocal, DeviceTelemetry, DeviceConfig, Plant
from datetime import datetime, timedelta
import sys

def check_device_connections(device_id=None):
    """Check connection status for IoT devices"""
    
    db = SessionLocal()
    
    try:
        print("\n" + "="*70)
        print("IoT DEVICE CONNECTION DIAGNOSTIC")
        print("="*70)
        
        # Get all devices or specific device
        if device_id:
            telemetry_records = db.query(DeviceTelemetry)\
                .filter(DeviceTelemetry.device_id == device_id)\
                .order_by(DeviceTelemetry.created_at.desc())\
                .limit(100)\
                .all()
        else:
            telemetry_records = db.query(DeviceTelemetry)\
                .order_by(DeviceTelemetry.created_at.desc())\
                .limit(200)\
                .all()
        
        if not telemetry_records:
            print("\n❌ NO DEVICES FOUND!")
            print("   No telemetry data in database.")
            print("   Check if ESP32 is sending data to the backend.")
            db.close()
            return False
        
        # Group by device_id
        devices = {}
        for record in telemetry_records:
            if record.device_id not in devices:
                devices[record.device_id] = []
            devices[record.device_id].append(record)
        
        print(f"\n✅ Found {len(devices)} device(s)\n")
        
        now = datetime.utcnow()
        all_connected = True
        
        for dev_id, records in sorted(devices.items()):
            latest = records[0]
            time_since_update = (now - latest.created_at).total_seconds()
            
            # Check if device is recent (within 30 seconds = healthy)
            is_connected = time_since_update <= 30
            status_icon = "✅ CONNECTED" if is_connected else "⚠️  STALE"
            
            if not is_connected:
                all_connected = False
            
            print(f"Device ID: {dev_id}")
            print(f"  Status: {status_icon}")
            print(f"  Last Update: {time_since_update:.0f}s ago ({latest.created_at})")
            print(f"  Latest Moisture: {latest.soil_percent}% (raw: {latest.soil_raw})")
            print(f"  Pump Status: {'ON' if latest.pump else 'OFF'}")
            print(f"  Associated Plant ID: {latest.plant_id or 'None'}")
            
            # Get device config
            config = db.query(DeviceConfig)\
                .filter(DeviceConfig.device_id == dev_id)\
                .first()
            
            if config:
                print(f"  Device Config:")
                print(f"    - Auto Water: {config.auto_water}")
                print(f"    - Dry Threshold: {config.dry_threshold}")
                print(f"    - Wet Threshold: {config.wet_threshold}")
                
                if config.plant_id:
                    plant = db.query(Plant).filter(Plant.id == config.plant_id).first()
                    if plant:
                        print(f"    - Linked Plant: {plant.name} (ID: {plant.id})")
            
            print(f"  Record Count: {len(records)} entries")
            print(f"  Time Range: {records[-1].created_at} to {records[0].created_at}")
            print()
        
        print("-"*70)
        if all_connected:
            print("✅ All devices are CONNECTED and sending data!")
        else:
            print("⚠️  Some devices are stale or haven't sent data recently.")
            print("   Check ESP32 serial output for errors.")
        
        print("-"*70 + "\n")
        
        return all_connected
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    # Optional: check specific device
    device_id = sys.argv[1] if len(sys.argv) > 1 else None
    
    if device_id:
        print(f"\nChecking device: {device_id}")
    
    success = check_device_connections(device_id)
    sys.exit(0 if success else 1)
