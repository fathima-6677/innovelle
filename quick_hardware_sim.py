#!/usr/bin/env python3
"""
Quick Hardware Simulator - Works with existing system
Sends data via the existing /data endpoint that your system already uses
"""

import requests
import time
import random
from datetime import datetime

def send_hardware_data():
    """Send hardware data via existing endpoint"""
    
    # Generate realistic data
    bpm = random.randint(70, 85) + random.randint(-5, 5)
    panic = random.random() < 0.01  # 1% chance
    steps = random.randint(1000, 5000)
    
    # If panic, increase BPM
    if panic:
        bpm = random.randint(120, 160)
    
    # Data format for existing endpoint
    data = {
        'bpm': bpm,
        'panic': panic,
        'steps': steps,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        # Try the existing /data endpoint
        response = requests.post(
            'http://10.123.50.141:8001/data',
            json=data,
            timeout=2
        )
        
        if response.status_code == 200:
            return True, "✅"
        else:
            return False, f"❌ ({response.status_code})"
            
    except Exception as e:
        return False, f"❌ {str(e)[:20]}"

def main():
    print("🤖 Quick Hardware Simulator")
    print("📡 Sending to existing Flutter system")
    print("🎮 Press Ctrl+C to stop")
    print("-" * 40)
    
    cycle = 0
    
    while True:
        try:
            # Send data
            success, status = send_hardware_data()
            
            # Print status every 10 cycles (1 second)
            if cycle % 10 == 0:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"{status} [{timestamp}] Hardware data sent")
            
            cycle += 1
            time.sleep(0.1)  # 100ms
            
        except KeyboardInterrupt:
            print("\n🛑 Simulator stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()