#!/usr/bin/env python3
"""
AUTIGUARD SOCKET.IO SERVER STARTUP SCRIPT
Fixes Python version conflicts and starts the server properly
"""

import os
import sys
import subprocess
import time

def main():
    print("🚀 AUTIGUARD SOCKET.IO SERVER STARTUP")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = os.path.join("sensor logger", "ai-wearable", "backend")
    if not os.path.exists(backend_dir):
        print("❌ Backend directory not found!")
        return
    
    os.chdir(backend_dir)
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check Python version
    python_version = sys.version
    print(f"🐍 Python version: {python_version}")
    
    # Try to import serial to verify it works
    try:
        import serial
        print("✅ Serial module imported successfully")
    except ImportError as e:
        print(f"❌ Serial import failed: {e}")
        print("Installing pyserial...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyserial==3.5"])
    
    # Start the server using python directly instead of uvicorn command
    print("\n🌐 Starting FastAPI server with Socket.IO...")
    print("Server will be available at: http://localhost:8000")
    print("Socket.IO endpoint: http://localhost:8000/socket.io/")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Import and run the app directly
        from main import app
        import uvicorn
        
        # Run with uvicorn programmatically
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            reload=False
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        print("\nTrying alternative startup method...")
        
        # Alternative: Run as module
        try:
            subprocess.run([
                sys.executable, "-m", "uvicorn", 
                "main:app", 
                "--host", "0.0.0.0", 
                "--port", "8000",
                "--reload"
            ])
        except Exception as e2:
            print(f"❌ Alternative startup failed: {e2}")

if __name__ == "__main__":
    main()