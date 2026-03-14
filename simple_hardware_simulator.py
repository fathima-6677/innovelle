#!/usr/bin/env python3
"""
Simple ESP32 Hardware Simulator
Sends BPM, panic, and GPS data directly to your Flutter app via the backend
"""

import requests
import time
import random
import threading
from datetime import datetime

class SimpleHardwareSimulator:
    def __init__(self):
        self.backend_url = "http://10.123.50.141:8001"
        self.running = False
        
        # Hardware data
        self.bpm = 75
        self.panic = False
        self.steps = 0
        self.latitude = 13.0827  # Bangalore
        self.longitude = 80.2707
        self.battery = 85
        
    def generate_realistic_data(self):
        """Generate realistic sensor data"""
        # BPM variation (70-85 normal, can spike for emergencies)
        self.bpm = random.randint(70, 85) + random.randint(-5, 5)
        
        # Panic button (1% chance)
        if random.random() < 0.01:
            self.panic = True
            self.bpm = random.randint(120, 160)  # Elevated BPM during panic
            print(f"🚨 PANIC TRIGGERED! BPM: {self.bpm}")
        else:
            self.panic = False
            
        # Steps increment
        if random.random() < 0.3:
            self.steps += random.randint(1, 3)
            
        # GPS drift
        if random.random() < 0.1:
            self.latitude += random.uniform(-0.0001, 0.0001)
            self.longitude += random.uniform(-0.0001, 0.0001)
            
        # Battery drain
        if random.random() < 0.005:
            self.battery = max(0, self.battery - 1)
    
    def send_to_backend(self):
        """Send data to your existing backend"""
        try:
            # Format data for your backend
            data = {
                'bpm': self.bpm,
                'panic': self.panic,
                'steps': self.steps,
                'latitude': self.latitude,
                'longitude': self.longitude,
                'battery': self.battery,
                'timestamp': datetime.now().isoformat()
            }
            
            # Send to hardware data endpoint
            response = requests.post(
                f'{self.backend_url}/api/hardware-data',
                json=data,
                timeout=2
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Backend error: {e}")
            return False
    
    def print_status(self):
        """Print current status"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        panic_status = "🚨 PANIC" if self.panic else "✅ OK"
        print(f"[{timestamp}] BPM:{self.bpm} | {panic_status} | Steps:{self.steps} | Battery:{self.battery}%")
    
    def run(self):
        """Main simulation loop"""
        print("🤖 Simple Hardware Simulator Started")
        print(f"📡 Sending data to: {self.backend_url}")
        print("🎮 Press Ctrl+C to stop")
        print("-" * 50)
        
        self.running = True
        cycle = 0
        
        while self.running:
            try:
                # Generate new data
                self.generate_realistic_data()
                
                # Send to backend
                success = self.send_to_backend()
                
                # Print status every 10 cycles (1 second)
                if cycle % 10 == 0:
                    status = "✅" if success else "❌"
                    print(f"{status} [{datetime.now().strftime('%H:%M:%S')}] BPM:{self.bpm} | Panic:{self.panic} | Steps:{self.steps}")
                
                cycle += 1
                time.sleep(0.1)  # 100ms = 10 Hz
                
            except KeyboardInterrupt:
                print("\n🛑 Simulator stopped")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(1)
        
        self.running = False

def interactive_mode():
    """Interactive mode with manual controls"""
    sim = SimpleHardwareSimulator()
    
    # Start simulation in background
    sim_thread = threading.Thread(target=sim.run)
    sim_thread.daemon = True
    sim_thread.start()
    
    print("\n🎮 INTERACTIVE CONTROLS:")
    print("p - Trigger panic button")
    print("h - High BPM (exercise)")
    print("l - Low battery")
    print("r - Reset to normal")
    print("q - Quit")
    print("-" * 30)
    
    while sim.running:
        try:
            cmd = input("Command: ").strip().lower()
            
            if cmd == 'p':
                sim.panic = True
                sim.bpm = random.randint(140, 180)
                print("🚨 Panic button triggered!")
                
            elif cmd == 'h':
                sim.bpm = random.randint(120, 160)
                print(f"🏃 High BPM set: {sim.bpm}")
                
            elif cmd == 'l':
                sim.battery = 15
                print("🔋 Low battery set")
                
            elif cmd == 'r':
                sim.panic = False
                sim.bpm = random.randint(70, 85)
                sim.battery = 85
                print("✅ Reset to normal")
                
            elif cmd == 'q':
                sim.running = False
                break
                
        except KeyboardInterrupt:
            sim.running = False
            break

if __name__ == "__main__":
    print("🤖 Simple ESP32 Hardware Simulator")
    print("Sends data directly to your Flutter app via backend")
    print()
    
    mode = input("Choose mode:\n1. Auto simulation\n2. Interactive mode\nChoice (1/2): ").strip()
    
    if mode == '2':
        interactive_mode()
    else:
        sim = SimpleHardwareSimulator()
        sim.run()