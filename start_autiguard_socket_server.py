#!/usr/bin/env python3
"""
AUTIGUARD SOCKET.IO SERVER STARTUP
Start the Autiguard backend with proper Socket.IO configuration.
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    
    print("🔄 Checking dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'python-socketio',
        'twilio',
        'python-dotenv',
        'pyserial'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}: Installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}: Missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages)
        return True
    
    print("✅ All dependencies satisfied")
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    
    env_path = Path("sensor logger/ai-wearable/backend/.env")
    
    if not env_path.exists():
        print("❌ .env file not found!")
        print("📝 Please create .env file in sensor logger/ai-wearable/backend/")
        return False
    
    print("✅ .env file found")
    
    # Check for required variables
    required_vars = [
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN',
        'TWILIO_WHATSAPP_FROM',
        'TWILIO_WHATSAPP_TO',
        'TWILIO_TEMPLATE_SID'
    ]
    
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    missing_vars = []
    for var in required_vars:
        if f"{var}=" not in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
        print("📝 Please add them to your .env file")
    else:
        print("✅ All required environment variables present")
    
    return True

def start_server():
    """Start the Autiguard server with proper configuration"""
    
    print("🚀 Starting Autiguard Socket.IO Server...")
    
    # Change to backend directory
    backend_dir = Path("sensor logger/ai-wearable/backend")
    
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return False
    
    os.chdir(backend_dir)
    
    # Start server with uvicorn
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'main:socket_app',  # Use socket_app instead of app
        '--host', '0.0.0.0',
        '--port', '8000',
        '--reload',  # Enable auto-reload for development
        '--log-level', 'info'
    ]
    
    print(f"🔄 Running command: {' '.join(cmd)}")
    print("🌐 Server will be available at: http://localhost:8000")
    print("🔌 Socket.IO endpoint: ws://localhost:8000/socket.io/")
    print("📊 API docs: http://localhost:8000/docs")
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        return False
    
    return True

def test_server_health():
    """Test if server is running and healthy"""
    
    print("🔄 Testing server health...")
    
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            response = requests.get('http://localhost:8000/health', timeout=2)
            if response.status_code == 200:
                print("✅ Server is healthy and responding")
                return True
        except:
            pass
        
        print(f"⏳ Waiting for server... ({attempt + 1}/{max_attempts})")
        time.sleep(1)
    
    print("❌ Server health check failed")
    return False

def main():
    """Main startup function"""
    
    print("🛡️ AUTIGUARD SOCKET.IO SERVER STARTUP")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check .env file
    if not check_env_file():
        return False
    
    # Start server
    if not start_server():
        return False
    
    return True

if __name__ == "__main__":
    main()