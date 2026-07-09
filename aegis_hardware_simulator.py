#!/usr/bin/env python3
"""
AEGIS ESP32 Hardware Simulator
Simulates ESP32 wearable device with BPM, panic button, GPS, and fall detection
Sends data via serial port emulation to the Autiguard backend
"""

import serial
import time
import random
import threading
import json
from datetime import datetime
import math

class AegisHardwareSimulator:
    def __init__(self, port='COM3', baud_rate=115200):
        self.port = port
        self.baud_rate = baud_rate
        self.serial_conn = None
        self.running = False
        
        # Simulated sensor data
        self.bpm = 75  # Normal resting heart rate
        self.panic_pressed = False
        self.steps = 0
        self.latitude = 11.9416  # Pondicherry coordinates
        self.longitude = 79.8083
        self.battery_level = 85
        
        # Simulation parameters
        self.bpm_variation = 5  # BPM can vary ±5
        self.step_increment = 0
        self.panic_cooldown = 0
        
        # Emergency scenarios
        self.scenarios = {
            'normal': {'bpm_range': (70, 85), 'panic_chance': 0.001},
            'exercise': {'bpm_range': (120, 160), 'panic_chance': 0.001},
            'stress': {'bpm_range': (90, 110), 'panic_chance': 0.01},
            'emergency': {'bpm_range': (140, 180), 'panic_chance': 0.1},
            'medical': {'bpm_range': (45, 200), 'panic_chance': 0.05}
        }
        self.current_scenario = 'normal'
        
    def connect_serial(self):
        """Initialize serial connection (simulated)"""
        try:
            print(f"🔌 AEGIS Hardware Simulator starting on {self.port}")
            print(f"📡 Baud Rate: {self.baud_rate}")
            print(f"💓 Initial BPM: {self.bpm}")
            print(f"📍 GPS: {self.latitude}, {self.longitude}")
            print("=" * 50)
            return True
        except Exception as e:
            print(f"❌ Serial connection failed: {e}")
            return False
    
    def generate_realistic_bpm(self):
        """Generate realistic heart rate based on current scenario"""
        scenario = self.scenarios[self.current_scenario]
        base_bpm = random.randint(*scenario['bpm_range'])
        
        # Add natural variation (breathing, movement)
        variation = random.uniform(-self.bpm_variation, self.bpm_variation)
        
        # Add time-based variation (circadian rhythm simulation)
        time_factor = math.sin(time.time() / 3600) * 3  # Slight daily variation
        
        self.bpm = max(40, min(200, int(base_bpm + variation + time_factor)))
        return self.bpm
    
    def simulate_movement(self):
        """Simulate step counting and GPS movement"""
        # Step simulation
        if random.random() < 0.3:  # 30% chance of step per cycle
            self.step_increment += random.randint(1, 3)
            self.steps += self.step_increment
        
        # GPS drift simulation (small movements)
        if random.random() < 0.1:  # 10% chance of GPS update
            self.latitude += random.uniform(-0.0001, 0.0001)
            self.longitude += random.uniform(-0.0001, 0.0001)
    
    def check_panic_button(self):
        """Simulate panic button press based on scenario"""
        scenario = self.scenarios[self.current_scenario]
        
        if self.panic_cooldown > 0:
            self.panic_cooldown -= 1
            return False
        
        if random.random() < scenario['panic_chance']:
            self.panic_pressed = True
            self.panic_cooldown = 50  # 5 second cooldown (50 * 100ms)
            print(f"🚨 PANIC BUTTON PRESSED! Scenario: {self.current_scenario}")
            return True
        
        self.panic_pressed = False
        return False
    
    def simulate_battery_drain(self):
        """Simulate battery level changes"""
        if random.random() < 0.01:  # 1% chance per cycle
            self.battery_level = max(0, self.battery_level - 1)
    
    def format_serial_data(self):
        """Format data in ESP32 serial format"""
        # Format: BPM:75,PANIC:0,STEPS:1240,LAT:11.9416,LNG:79.8083,BAT:85
        panic_val = 1 if self.panic_pressed else 0
        
        data = (f"BPM:{self.bpm},"
                f"PANIC:{panic_val},"
                f"STEPS:{self.steps},"
                f"LAT:{self.latitude:.6f},"
                f"LNG:{self.longitude:.6f},"
                f"BAT:{self.battery_level}")
        
        return data
    
    def send_data_to_backend(self):
        """Send data directly to backend via HTTP (since serial is simulated)"""
        try:
            import requests
            
            data = {
                'bpm': self.bpm,
                'panic': self.panic_pressed,
                'steps': self.steps,
                'latitude': self.latitude,
                'longitude': self.longitude,
                'battery': self.battery_level,
                'timestamp': datetime.now().isoformat()
            }
            
            # Send to backend
            response = requests.post(
                'http://10.123.50.141:8001/api/hardware-data',
                json=data,
                timeout=2
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"⚠️ Backend response: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Backend communication error: {e}")
            return False
    
    def print_status(self):
        """Print current hardware status"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        serial_data = self.format_serial_data()
        
        print(f"[{timestamp}] 📡 {serial_data} | Scenario: {self.current_scenario}")
        
        # Special alerts
        if self.panic_pressed:
            print(f"[{timestamp}] 🚨 PANIC ALERT ACTIVE!")
        
        if self.battery_level < 20:
            print(f"[{timestamp}] 🔋 LOW BATTERY: {self.battery_level}%")
    
    def change_scenario(self, scenario):
        """Change simulation scenario"""
        if scenario in self.scenarios:
            self.current_scenario = scenario
            print(f"🎭 Scenario changed to: {scenario.upper()}")
            return True
        return False
    
    def run_simulation(self):
        """Main simulation loop"""
        self.running = True
        cycle_count = 0
        
        while self.running:
            try:
                # Generate sensor data
                self.generate_realistic_bpm()
                self.simulate_movement()
                self.check_panic_button()
                self.simulate_battery_drain()
                
                # Send data to backend
                self.send_data_to_backend()
                
                # Print status every 10 cycles (1 second)
                if cycle_count % 10 == 0:
                    self.print_status()
                
                # Auto scenario changes for demo
                if cycle_count % 300 == 0 and cycle_count > 0:  # Every 30 seconds
                    scenarios = list(self.scenarios.keys())
                    new_scenario = random.choice(scenarios)
                    self.change_scenario(new_scenario)
                
                cycle_count += 1
                time.sleep(0.1)  # 100ms cycle (10 Hz)
                
            except KeyboardInterrupt:
                print("\n🛑 Simulation stopped by user")
                break
            except Exception as e:
                print(f"❌ Simulation error: {e}")
                time.sleep(1)
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.running = False
        print("🛑 AEGIS Hardware Simulator stopped")

def interactive_mode():
    """Interactive mode for manual control"""
    simulator = AegisHardwareSimulator()
    
    if not simulator.connect_serial():
        return
    
    # Start simulation in background thread
    sim_thread = threading.Thread(target=simulator.run_simulation)
    sim_thread.daemon = True
    sim_thread.start()
    
    print("\n🎮 INTERACTIVE MODE COMMANDS:")
    print("1 - Normal scenario")
    print("2 - Exercise scenario") 
    print("3 - Stress scenario")
    print("4 - Emergency scenario")
    print("5 - Medical scenario")
    print("p - Trigger panic button")
    print("b - Set low battery")
    print("q - Quit")
    print("=" * 50)
    
    while True:
        try:
            cmd = input("Enter command: ").strip().lower()
            
            if cmd == '1':
                simulator.change_scenario('normal')
            elif cmd == '2':
                simulator.change_scenario('exercise')
            elif cmd == '3':
                simulator.change_scenario('stress')
            elif cmd == '4':
                simulator.change_scenario('emergency')
            elif cmd == '5':
                simulator.change_scenario('medical')
            elif cmd == 'p':
                simulator.panic_pressed = True
                simulator.panic_cooldown = 50
                print("🚨 Manual panic button triggered!")
            elif cmd == 'b':
                simulator.battery_level = 15
                print("🔋 Battery set to low (15%)")
            elif cmd == 'q':
                break
            else:
                print("❌ Invalid command")
                
        except KeyboardInterrupt:
            break
    
    simulator.stop_simulation()

if __name__ == "__main__":
    print("🛡️ AEGIS ESP32 Hardware Simulator v2.0")
    print("🎯 Simulating wearable device for Autiguard system")
    print()
    
    mode = input("Choose mode:\n1. Auto simulation\n2. Interactive mode\nEnter choice (1/2): ").strip()
    
    if mode == '2':
        interactive_mode()
    else:
        # Auto mode
        simulator = AegisHardwareSimulator()
        if simulator.connect_serial():
            try:
                simulator.run_simulation()
            except KeyboardInterrupt:
                simulator.stop_simulation()