#!/usr/bin/env python3
"""
AEGIS System Launcher
Starts the complete Autiguard system with hardware simulation
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def print_banner():
    """Print system banner"""
    print("=" * 60)
    print("🛡️  AEGIS AUTIGUARD EMERGENCY MONITORING SYSTEM")
    print("=" * 60)
    print("🚀 Complete system launcher with hardware simulation")
    print("📱 Backend + Hardware Simulator + Flutter App")
    print("=" * 60)

def check_requirements():
    """Check if required files exist"""
    required_files = [
        "run_server_direct.py",
        "aegis_hardware_simulator.py", 
        "aegis_simulator_gui.py",
        "autiguard_app"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found")
    return True

def start_backend():
    """Start the backend server"""
    print("\n🌐 Starting Autiguard Backend Server...")
    try:
        backend_process = subprocess.Popen(
            [sys.executable, "run_server_direct.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if process is still running
        if backend_process.poll() is None:
            print("✅ Backend server started successfully")
            return backend_process
        else:
            print("❌ Backend server failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_hardware_simulator():
    """Start the hardware simulator"""
    print("\n🤖 Choose Hardware Simulator Mode:")
    print("1. GUI Mode (Recommended)")
    print("2. Console Mode")
    print("3. Skip Hardware Simulator")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        print("🎮 Starting GUI Hardware Simulator...")
        try:
            sim_process = subprocess.Popen([sys.executable, "aegis_simulator_gui.py"])
            print("✅ GUI Hardware Simulator started")
            return sim_process
        except Exception as e:
            print(f"❌ Error starting GUI simulator: {e}")
            return None
            
    elif choice == "2":
        print("💻 Starting Console Hardware Simulator...")
        try:
            sim_process = subprocess.Popen([sys.executable, "aegis_hardware_simulator.py"])
            print("✅ Console Hardware Simulator started")
            return sim_process
        except Exception as e:
            print(f"❌ Error starting console simulator: {e}")
            return None
    else:
        print("⏭️ Skipping Hardware Simulator")
        return None

def start_flutter_app():
    """Start the Flutter app"""
    print("\n📱 Starting Flutter App...")
    
    if not os.path.exists("autiguard_app"):
        print("❌ Flutter app directory not found")
        return None
    
    try:
        # Change to Flutter app directory and run
        flutter_process = subprocess.Popen(
            ["flutter", "run"],
            cwd="autiguard_app"
        )
        print("✅ Flutter app started")
        return flutter_process
        
    except Exception as e:
        print(f"❌ Error starting Flutter app: {e}")
        print("💡 Make sure Flutter SDK is installed and in PATH")
        return None

def show_system_info():
    """Show system information and URLs"""
    print("\n" + "=" * 60)
    print("🎯 SYSTEM INFORMATION")
    print("=" * 60)
    print("🌐 Backend Server: http://10.123.50.141:8001")
    print("🔌 Socket.IO: http://10.123.50.141:8001/socket.io/")
    print("🏥 Health Check: http://10.123.50.141:8001/health")
    print("📊 API Docs: http://10.123.50.141:8001/docs")
    print("=" * 60)
    print("🚨 EMERGENCY FEATURES:")
    print("   • Fall Detection: 11.0 m/s² threshold")
    print("   • Audio Distress: 85 dB threshold") 
    print("   • WhatsApp Alerts: +918754617636")
    print("   • Real-time Socket.IO streaming")
    print("=" * 60)

def main():
    """Main launcher function"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        input("\nPress Enter to exit...")
        return
    
    processes = []
    
    try:
        # Start backend server
        backend_proc = start_backend()
        if backend_proc:
            processes.append(("Backend", backend_proc))
        else:
            print("❌ Cannot continue without backend server")
            return
        
        # Start hardware simulator
        sim_proc = start_hardware_simulator()
        if sim_proc:
            processes.append(("Hardware Simulator", sim_proc))
        
        # Start Flutter app
        flutter_proc = start_flutter_app()
        if flutter_proc:
            processes.append(("Flutter App", flutter_proc))
        
        # Show system info
        show_system_info()
        
        print("\n🎉 AEGIS System is now running!")
        print("💡 Use the GUI simulator to control hardware data")
        print("📱 Check your Flutter app for real-time updates")
        print("\nPress Ctrl+C to stop all processes...")
        
        # Wait for user interrupt
        try:
            while True:
                time.sleep(1)
                
                # Check if processes are still running
                for name, proc in processes:
                    if proc.poll() is not None:
                        print(f"⚠️ {name} process has stopped")
                        
        except KeyboardInterrupt:
            print("\n🛑 Shutting down AEGIS system...")
            
    except Exception as e:
        print(f"❌ System error: {e}")
        
    finally:
        # Clean up processes
        print("🧹 Cleaning up processes...")
        for name, proc in processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
                print(f"✅ {name} stopped")
            except Exception as e:
                print(f"⚠️ Error stopping {name}: {e}")
        
        print("👋 AEGIS system shutdown complete")

if __name__ == "__main__":
    main()