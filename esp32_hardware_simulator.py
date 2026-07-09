#!/usr/bin/env python3
"""
ESP32 Hardware Simulator - Complete Pipeline
Simulates ESP32 at 192.168.137.29 sending continuous sensor data
Includes realistic BPM, accelerometer, and panic button simulation
"""

import requests
import json
import time
import math
import random
from datetime import datetime
import threading

# ESP32 Configuration
ESP32_IP = "192.168.137.29"
BACKEND_URL = "http://localhost:8000/api/sensor-data"
UPDATE_INTERVAL = 1.0  # Send data every 1 second (realistic ESP32 rate)

class ESP32Simulator:
    def __init__(self):
        self.running = False
        self.packet_count = 0
        self.last_fall_time = 0
        self.last_panic_time = 0
        
        # Realistic sensor ranges
        self.base_bpm = random.randint(70, 85)  # Resting heart rate
        self.bpm_variation = 0
        
        print("🛡️ ESP32 HARDWARE SIMULATOR INITIALIZED")
        print(f"📡 Simulated ESP32 IP: {ESP32_IP}")
        print(f"🔗 Backend Endpoint: {BACKEND_URL}")
        print(f"⏱️ Update Interval: {UPDATE_INTERVAL}s")
        print(f"💓 Base Heart Rate: {self.base_bpm} BPM")
        print("-" * 60)
    
    def generate_realistic_bpm(self):
        """Generate realistic heart rate with natural variation"""
        # Natural heart rate variation (±5 BPM)
        variation = random.uniform(-5, 5)
        
        # Slight trend over time (simulates activity/rest cycles)
        time_factor = math.sin(time.time() / 60) * 3  # 1-minute cycle
        
        bmp = int(self.base_bpm + variation + time_factor)
        return max(60, min(100, bmp))  # Clamp to realistic range
    
    def generate_accelerometer_data(self):
        """Generate realistic accelerometer data with occasional falls"""
        current_time = time.time()
        
        # 2% chance of simulating a fall (every ~50 seconds on average)
        if (random.random() < 0.02 and 
            current_time - self.last_fall_time > 30):  # Min 30s between falls
            
            # Simulate fall: high magnitude impact
            magnitude = random.uniform(12.0, 25.0)
            angle = random.uniform(0, 2 * math.pi)
            
            accel_x = magnitude * math.cos(angle)
            accel_y = magnitude * math.sin(angle)
            accel_z = random.uniform(-3.0, 3.0)
            
            self.last_fall_time = current_time
            print(f"🚨 SIMULATING FALL: Magnitude {magnitude:.2f} m/s²")
            
            return accel_x, accel_y, accel_z, magnitude
        
        # Normal movement: around gravity (9.8 m/s²) with small variations
        base_accel = 9.8
        noise_x = random.uniform(-0.8, 0.8)
        noise_y = random.uniform(-0.8, 0.8)
        noise_z = random.uniform(-0.8, 0.8)
        
        accel_x = base_accel + noise_x
        accel_y = noise_y
        accel_z = noise_z
        
        magnitude = math.sqrt(accel_x**2 + accel_y**2 + accel_z**2)
        
        return accel_x, accel_y, accel_z, magnitude
    
    def generate_panic_button(self):
        """Generate panic button state with occasional presses"""
        current_time = time.time()
        
        # 1% chance of panic button press (every ~100 seconds on average)
        if (random.random() < 0.01 and 
            current_time - self.last_panic_time > 60):  # Min 60s between panics
            
            self.last_panic_time = current_time
            print(f"🚨 SIMULATING PANIC BUTTON PRESS")
            return 1
        
        return 0
    
    def create_sensor_packet(self):
        """Create complete ESP32 sensor data packet"""
        accel_x, accel_y, accel_z, magnitude = self.generate_accelerometer_data()
        bmp = self.generate_realistic_bpm()
        button_state = self.generate_panic_button()
        
        return {
            "accel_x": round(accel_x, 2),
            "accel_y": round(accel_y, 2),
            "accel_z": round(accel_z, 2),
            "bmp": bmp,
            "button_state": button_state,
            "client_ip": ESP32_IP,
            "timestamp": datetime.now().isoformat(),
            "battery_level": random.randint(85, 100),  # Simulate good battery
            "signal_strength": random.randint(-45, -30)  # Good WiFi signal
        }
    
    def send_data_packet(self, packet):
        """Send sensor data to backend"""
        try:
            response = requests.post(BACKEND_URL, json=packet, timeout=3)
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                print(f"❌ Backend Error: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Error: {e}")
            return None
    
    def run_simulation(self):
        """Main simulation loop"""
        print("🚀 ESP32 SIMULATION STARTED")
        print("📊 Monitoring: BPM | Accelerometer | Panic Button")
        print("🎯 Fall Threshold: 11.0 m/s² (Hyper-Sensitive)")
        print("⏱️ Latch Duration: 15 seconds (Network Compensation)")
        print("=" * 60)
        
        self.running = True
        
        try:
            while self.running:
                self.packet_count += 1
                
                # Generate and send sensor data
                packet = self.create_sensor_packet()
                result = self.send_data_packet(packet)
                
                if result:
                    # Display packet status
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    magnitude = math.sqrt(
                        packet['accel_x']**2 + 
                        packet['accel_y']**2 + 
                        packet['accel_z']**2
                    )
                    
                    # Status indicators
                    fall_status = "🚨 FALL" if result.get('fall_detected') else "✅ NORMAL"
                    panic_status = "🚨 PANIC" if result.get('panic_detected') else ""
                    
                    print(f"[{timestamp}] #{self.packet_count:04d} | "
                          f"BPM:{packet['bmp']:3d} | "
                          f"MAG:{magnitude:5.2f} | "
                          f"BTN:{packet['button_state']} | "
                          f"{fall_status} {panic_status}")
                    
                    # Show backend alerts
                    if result.get('fall_detected') or result.get('panic_detected'):
                        print(f"    🛡️ Backend: {result.get('message')}")
                        
                else:
                    print(f"❌ Packet #{self.packet_count} failed to send")
                    print("💡 Check if backend is running on localhost:8000")
                    break
                
                # Wait for next update
                time.sleep(UPDATE_INTERVAL)
                
        except KeyboardInterrupt:
            print(f"\n🛑 ESP32 Simulation Stopped by User")
        except Exception as e:
            print(f"\n❌ Simulation Error: {e}")
        finally:
            self.running = False
            print(f"📊 Total packets sent: {self.packet_count}")
            print("🔋 Simulation complete - Ready for real hardware")

def main():
    """Main entry point"""
    simulator = ESP32Simulator()
    
    print("🔋 HARDWARE BATTERY DEAD - USING SIMULATION")
    print("⚡ Charge your ESP32 while this runs")
    print("🔄 Press Ctrl+C to stop simulation")
    print()
    
    # Start simulation
    simulator.run_simulation()

if __name__ == "__main__":
    main()