#!/usr/bin/env python3
"""
Mobile Data Simulator for AUTIGUARD Elite Dashboard
Simulates realistic mobile sensor data for hackathon demo
"""

import requests
import time
import random
import math
from datetime import datetime

# Backend endpoint
BACKEND_URL = "http://localhost:8000/data"

def generate_realistic_sensor_data():
    """Generate realistic mobile sensor data in SensorController format"""
    timestamp = datetime.now().isoformat()
    
    # Simulate walking activity with realistic accelerometer
    base_accel = 9.8  # Gravity
    activity_accel = random.uniform(2.0, 8.0)  # Walking movement
    
    accel_x = random.uniform(-activity_accel, activity_accel)
    accel_y = random.uniform(-activity_accel, activity_accel) 
    accel_z = base_accel + random.uniform(-2.0, 2.0)
    
    # Calculate magnitude
    accel_magnitude = math.sqrt(accel_x**2 + accel_y**2 + accel_z**2)
    
    # Simulate occasional high acceleration (fall simulation)
    if random.random() < 0.05:  # 5% chance
        # Boost magnitude for fall detection (threshold is 25.0 in AEGIS system)
        accel_x = random.uniform(-20.0, 20.0)
        accel_y = random.uniform(-20.0, 20.0)
        accel_z = random.uniform(-20.0, 20.0)
        accel_magnitude = math.sqrt(accel_x**2 + accel_y**2 + accel_z**2)
        print(f"🚨 SIMULATING FALL: {accel_magnitude:.2f} m/s²")
    
    # Simulate realistic sound levels
    base_sound = random.uniform(30, 60)  # Normal ambient
    if random.random() < 0.1:  # 10% chance of loud noise
        sound_db = random.uniform(90, 110)  # Audio warning trigger at 85.0
        print(f"🔊 SIMULATING LOUD NOISE: {sound_db:.1f} dB")
    else:
        sound_db = base_sound
    
    # Simulate GPS coordinates (Pondicherry area)
    lat = 11.9416 + random.uniform(-0.01, 0.01)
    lng = 79.8083 + random.uniform(-0.01, 0.01)
    
    # Simulate step counting
    steps = random.randint(0, 10000)
    
    # Format data as expected by SensorController (payload array format)
    return {
        "payload": [
            {
                "name": "accelerometer",
                "values": {
                    "x": accel_x,
                    "y": accel_y,
                    "z": accel_z
                }
            },
            {
                "name": "audio",
                "values": {
                    "db": sound_db
                }
            },
            {
                "name": "pedometer",
                "values": {
                    "steps": steps
                }
            },
            {
                "name": "activity",
                "values": {
                    "activity": "walking" if accel_magnitude > 12 else "stationary"
                }
            },
            {
                "name": "location",
                "values": {
                    "latitude": lat,
                    "longitude": lng,
                    "accuracy": random.uniform(5, 20)
                }
            },
            {
                "name": "battery",
                "values": {
                    "level": random.uniform(0.2, 1.0),
                    "is_charging": random.choice([True, False])
                }
            }
        ],
        "timestamp": timestamp,
        "device_id": "simulator_001"
    }

def main():
    """Main simulation loop"""
    print("🛡️  AUTIGUARD Mobile Data Simulator Starting...")
    print(f"📡 Sending data to: {BACKEND_URL}")
    print("🎯 Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Generate realistic sensor data
            data = generate_realistic_sensor_data()
            
            try:
                # Send POST request to backend
                response = requests.post(BACKEND_URL, json=data, timeout=3)
                
                if response.status_code == 200:
                    accel_mag = math.sqrt(data['payload'][0]['values']['x']**2 + 
                                        data['payload'][0]['values']['y']**2 + 
                                        data['payload'][0]['values']['z']**2)
                    sound_db = data['payload'][1]['values']['db']
                    steps = data['payload'][2]['values']['steps']
                    print(f"✅ Data sent: Accel={accel_mag:.2f} | Steps={steps} | Sound={sound_db:.1f}dB")
                else:
                    print(f"❌ Error: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Connection error: {e}")
            
            # Wait 2 seconds before next data point
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n🛑 Simulator stopped by user")
    except Exception as e:
        print(f"❌ Simulator error: {e}")

if __name__ == "__main__":
    main()