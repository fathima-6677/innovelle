#!/usr/bin/env python3
"""
AEGIS.SYS Serial Bridge Setup Script
Installs dependencies and tests COM3 connection
"""

import subprocess
import sys
import os

def install_requirements():
    """Install Python dependencies"""
    print("🔧 Installing Python dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", 
            "sensor logger/ai-wearable/backend/requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def test_serial_connection():
    """Test COM3 serial connection"""
    print("🔌 Testing COM3 serial connection...")
    try:
        import serial
        
        # Try to open COM3
        ser = serial.Serial('COM3', 115200, timeout=1)
        print("✅ COM3 connection successful")
        ser.close()
        return True
        
    except ImportError:
        print("❌ pyserial not installed")
        return False
    except serial.SerialException as e:
        print(f"❌ COM3 connection failed: {e}")
        print("💡 Make sure ESP32 is connected to COM3")
        return False

def main():
    print("🛡️  AEGIS.SYS SERIAL BRIDGE SETUP")
    print("=" * 40)
    
    # Install dependencies
    if not install_requirements():
        return False
    
    # Test serial connection
    if not test_serial_connection():
        print("\n⚠️  Serial connection test failed")
        print("📋 Setup checklist:")
        print("   1. Connect Arduino Nano ESP32 to USB")
        print("   2. Upload aegis_esp32_serial_streamer.ino")
        print("   3. Verify device appears on COM3")
        print("   4. Run this script again")
        return False
    
    print("\n🎉 AEGIS Serial Bridge setup complete!")
    print("🚀 Ready to start backend server")
    print("\nNext steps:")
    print("1. cd 'sensor logger/ai-wearable/backend'")
    print("2. python main.py")
    print("3. Open Flutter app")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)