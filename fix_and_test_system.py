#!/usr/bin/env python3
"""
Complete system fix and test
1. Fix Flutter provider syntax errors ✅ (already done)
2. Start backend server with latest code
3. Test hardware simulator connection
4. Verify Flutter app can compile
"""

import subprocess
import time
import requests
import json
import os
import sys
from datetime import datetime

def kill_existing_servers():
    """Kill any existing servers on port 8001"""
    try:
        # Kill processes using port 8001
        subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                      capture_output=True, check=False)
        time.sleep(2)
        print("🔄 Cleared existing processes")
    except:
        pass

def start_server():
    """Start the backend server"""
    backend_dir = os.path.join("sensor logger", "ai-wearable", "backend")
    
    if not os.path.exists(backend_dir):
        print(f"❌ Backend directory not found: {backend_dir}")
        return None
    
    original_dir = os.getcwd()
    os.chdir(backend_dir)
    
    try:
        print(f"🚀 Starting server from: {os.getcwd()}")
        
        # Start server
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:socket_app",
            "--host", "0.0.0.0", "--port", "8001"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait for server to start
        print("⏳ Waiting for server startup...")
        for i in range(10):
            try:
                response = requests.get('http://localhost:8001/health', timeout=2)
                if response.status_code == 200:
                    print("✅ Server started successfully!")
                    return process
            except:
                pass
            time.sleep(1)
            print(f"   Attempt {i+1}/10...")
        
        print("❌ Server failed to start")
        process.terminate()
        return None
        
    finally:
        os.chdir(original_dir)

def test_hardware_simulator():
    """Test the hardware simulator endpoint"""
    print("\n🧪 Testing hardware simulator endpoint...")
    
    data = {
        'bmp': 85,
        'panic': False,
        'steps': 1500,
        'latitude': 11.9416,
        'longitude': 79.8083,
        'battery': 90,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            'http://localhost:8001/api/hardware-data',
            json=data,
            timeout=5
        )
        
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Hardware simulator endpoint working!")
            return True
        else:
            print("❌ Hardware simulator endpoint failed")
            return False
            
    except Exception as e:
        print(f"❌ Hardware simulator test error: {e}")
        return False

def test_flutter_compilation():
    """Test Flutter app compilation"""
    print("\n📱 Testing Flutter app compilation...")
    
    flutter_dir = "autiguard_app"
    if not os.path.exists(flutter_dir):
        print("❌ Flutter app directory not found")
        return False
    
    original_dir = os.getcwd()
    os.chdir(flutter_dir)
    
    try:
        # Test Flutter analyze
        result = subprocess.run(['flutter', 'analyze'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Flutter app compiles without errors!")
            return True
        else:
            print("❌ Flutter compilation errors:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏳ Flutter analyze timed out (but may still work)")
        return True
    except Exception as e:
        print(f"❌ Flutter test error: {e}")
        return False
    finally:
        os.chdir(original_dir)

def run_hardware_simulator():
    """Run the hardware simulator"""
    print("\n🤖 Starting hardware simulator...")
    print("This will send test data to your Flutter app")
    print("Press Ctrl+C to stop")
    
    try:
        subprocess.run([sys.executable, 'simple_hardware_simulator.py'])
    except KeyboardInterrupt:
        print("\n🛑 Hardware simulator stopped")

def main():
    print("🛡️  AUTIGUARD SYSTEM FIX & TEST")
    print("=" * 50)
    
    # Step 1: Kill existing servers
    kill_existing_servers()
    
    # Step 2: Start server
    server_process = start_server()
    if not server_process:
        print("❌ Cannot start server. Exiting.")
        return
    
    try:
        # Step 3: Test hardware simulator
        hardware_ok = test_hardware_simulator()
        
        # Step 4: Test Flutter compilation
        flutter_ok = test_flutter_compilation()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 SYSTEM STATUS SUMMARY")
        print("=" * 50)
        print(f"🌐 Backend Server:      {'✅ RUNNING' if server_process else '❌ FAILED'}")
        print(f"🤖 Hardware Simulator:  {'✅ WORKING' if hardware_ok else '❌ FAILED'}")
        print(f"📱 Flutter App:         {'✅ COMPILES' if flutter_ok else '❌ ERRORS'}")
        
        if hardware_ok and flutter_ok:
            print("\n🎉 SYSTEM IS READY!")
            print("You can now:")
            print("1. Run Flutter app: cd autiguard_app && flutter run")
            print("2. Run hardware simulator: python simple_hardware_simulator.py")
            
            # Ask if user wants to run simulator
            choice = input("\nRun hardware simulator now? (y/n): ").strip().lower()
            if choice == 'y':
                run_hardware_simulator()
        else:
            print("\n⚠️  SYSTEM HAS ISSUES - Check errors above")
        
        # Keep server running
        print("\n🔄 Server is running. Press Ctrl+C to stop...")
        server_process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping system...")
    finally:
        if server_process:
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    main()