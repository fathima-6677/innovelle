#!/usr/bin/env python3
"""
Direct server runner to bypass uvicorn import issues
"""

import os
import sys

# Change to backend directory
backend_dir = os.path.join("sensor logger", "ai-wearable", "backend")
if os.path.exists(backend_dir):
    os.chdir(backend_dir)
    sys.path.insert(0, os.getcwd())

print(f"🚀 Starting Autiguard Server from: {os.getcwd()}")
print(f"🐍 Python: {sys.version}")

try:
    # Test imports first
    print("📦 Testing imports...")
    import serial
    print("✅ Serial module OK")
    
    import fastapi
    print("✅ FastAPI OK")
    
    import socketio
    print("✅ Socket.IO OK")
    
    # Import the socket app (not just the main app)
    from main import socket_app as app
    print("✅ Socket app imported")
    
    # Run with uvicorn programmatically
    import uvicorn
    print("\n🌐 Starting server on http://localhost:8001")
    print("🔌 Socket.IO available at http://localhost:8001/socket.io/")
    print("📡 WebSocket endpoint: ws://localhost:8001/ws")
    print("\nPress Ctrl+C to stop")
    print("-" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Installing missing dependencies...")
    
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print("🔄 Retrying...")
    from main import app
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
    
except Exception as e:
    print(f"❌ Server error: {e}")
    import traceback
    traceback.print_exc()