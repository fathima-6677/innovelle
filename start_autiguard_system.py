#!/usr/bin/env python3
"""
Autiguard Complete System Startup
Starts backend + ESP32 simulator + provides Flutter connection info
"""

import subprocess
import time
import os
import sys
import threading
import requests
from datetime import datetime

def print_banner():
    """Print system startup banner"""
    print("=" * 70)
    print("🛡️  AUTIGUARD COMPLETE SYSTEM STARTUP")
    print("=" * 70)
    print("📅 Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🔋 Hardware Status: BATTERY DEAD (Using Simulation)")
    print("⚡ Action Required: Charge ESP32 hardware")
    print("🎯 System Mode: Full Pipeline Simulation")
    print("-" * 70)

def check_backend_health():
    """Check if backend is responding"""
    try:
        response = requests.get("http://localhost:8000/", timeout=3)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Health: {data.get('service', 'Unknown')}")
            print(f"📊 API Version: {data.get('version', 'Unknown')}")
            return True
    except:
        pass
    return False

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting FastAPI Backend...")
    
    backend_dir = "sensor logger/ai-wearable/backend"
    if not os.path.exists(backend_dir):
        print(f"❌ Backend directory not found: {backend_dir}")
        return None
    
    try:
        # Start backend process
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for backend to start
        print("⏳ Waiting for backend to initialize...")
        for i in range(10):
            time.sleep(1)
            if check_backend_health():
                print("✅ Backend started successfully!")
                return process
            print(f"   Attempt {i+1}/10...")
        
        print("❌ Backend failed to start within 10 seconds")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_esp32_simulator():
    """Start ESP32 hardware simulator"""
    print("🤖 Starting ESP32 Hardware Simulator...")
    
    try:
        process = subprocess.Popen(
            [sys.executable, "esp32_hardware_simulator.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("✅ ESP32 Simulator started!")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start ESP32 simulator: {e}")
        return None

def print_flutter_instructions():
    """Print Flutter app connection instructions"""
    print("\n" + "=" * 70)
    print("📱 FLUTTER APP CONNECTION INSTRUCTIONS")
    print("=" * 70)
    print("1. Open your Flutter project in VS Code/Android Studio")
    print("2. Connect your Android device or start emulator")
    print("3. Run the Flutter app:")
    print("   cd autiguard_app")
    print("   flutter run")
    print()
    print("🔗 Backend Endpoints:")
    print("   • Main API: http://localhost:8000/api/telemetry")
    print("   • ESP32 Data: http://localhost:8000/api/sensor-data")
    print("   • Status: http://localhost:8000/")
    print()
    print("📊 Expected Behavior:")
    print("   • Hardware Tab: Shows ESP32 WiFi connection")
    print("   • Mobile Tab: Shows sensor logger data")
    print("   • Fall Detection: Triggers every ~50 seconds")
    print("   • Panic Button: Triggers every ~100 seconds")
    print("   • Heart Rate: 70-85 BPM with natural variation")
    print()
    print("🔋 Hardware Status:")
    print("   • ESP32: SIMULATED (Battery charging)")
    print("   • Connection: WiFi (192.168.137.29)")
    print("   • Fall Threshold: 11.0 m/s² (Hyper-Sensitive)")
    print("   • Latch Duration: 15 seconds")

def monitor_system(backend_process, simulator_process):
    """Monitor system processes"""
    print("\n" + "=" * 70)
    print("🖥️  SYSTEM MONITORING")
    print("=" * 70)
    print("Press Ctrl+C to stop all processes")
    print("-" * 70)
    
    try:
        while True:
            # Check backend health
            if backend_process and backend_process.poll() is not None:
                print("❌ Backend process died!")
                break
            
            # Check simulator health
            if simulator_process and simulator_process.poll() is not None:
                print("❌ ESP32 Simulator process died!")
                break
            
            # Health check every 30 seconds
            time.sleep(30)
            if check_backend_health():
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] ✅ System Health: All processes running")
            else:
                print("⚠️ Backend health check failed")
            
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
    
    # Cleanup processes
    print("🧹 Cleaning up processes...")
    if backend_process:
        backend_process.terminate()
        print("✅ Backend process terminated")
    
    if simulator_process:
        simulator_process.terminate()
        print("✅ ESP32 Simulator terminated")
    
    print("🏁 System shutdown complete")

def main():
    """Main system startup"""
    print_banner()
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Cannot continue without backend")
        return
    
    # Start ESP32 simulator
    simulator_process = start_esp32_simulator()
    if not simulator_process:
        print("❌ Cannot continue without ESP32 simulator")
        backend_process.terminate()
        return
    
    # Print Flutter instructions
    print_flutter_instructions()
    
    # Monitor system
    monitor_system(backend_process, simulator_process)

if __name__ == "__main__":
    main()