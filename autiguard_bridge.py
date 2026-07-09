#!/usr/bin/env python3
"""
AUTIGUARD Bridge - Clean Dynamic Setup
No hardcoded values, environment-based configuration
"""

import sqlite3
import sys
import os
from flask import Flask, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration from environment
LAPTOP_IP = os.getenv('LAPTOP_IP', '10.123.50.141')
SENSOR_LOGGER_PORT = os.getenv('SENSOR_LOGGER_PORT', '8000')
BRIDGE_PORT = int(os.getenv('BRIDGE_PORT', '5000'))
HARDWARE_DB_PATH = os.getenv('HARDWARE_DB_PATH', r'E:\Athidh\Autiguard\esp32-cloud-server-main\wearable.db')
SENSOR_LOGGER_PATH = os.getenv('SENSOR_LOGGER_PATH', r'E:\Athidh\sensor logger\ai-wearable\backend')

# Add sensor logger backend to path
sys.path.append(SENSOR_LOGGER_PATH)

try:
    from controller.state import global_state
    SENSOR_LOGGER_AVAILABLE = True
    print(f"✅ Sensor Logger imported from: {SENSOR_LOGGER_PATH}")
except ImportError as e:
    print(f"⚠️  Sensor Logger not available: {e}")
    SENSOR_LOGGER_AVAILABLE = False

app = Flask(__name__)
CORS(app)

def get_hardware_data():
    """Get latest data from ESP32 hardware database"""
    try:
        if not os.path.exists(HARDWARE_DB_PATH):
            return {
                'bpm': 0,
                'lat': 0.0,
                'lng': 0.0,
                'panic': False,
                'fall': False,
                'sound': False,
                'food': False,
                'water': False,
                'restroom': False,
                'timestamp': datetime.now().isoformat(),
                'source': 'no_hardware'
            }
        
        conn = sqlite3.connect(HARDWARE_DB_PATH)
        c = conn.cursor()
        c.execute('SELECT * FROM sensor_data ORDER BY id DESC LIMIT 1')
        row = c.fetchone()
        conn.close()
        
        if row:
            return {
                'bpm': int(row[4]) if len(row) > 4 else 0,
                'lat': float(row[2]) if len(row) > 2 else 0.0,
                'lng': float(row[3]) if len(row) > 3 else 0.0,
                'panic': bool(row[5]) if len(row) > 5 else False,
                'fall': bool(row[6]) if len(row) > 6 else False,
                'sound': bool(row[7]) if len(row) > 7 else False,
                'food': bool(row[8]) if len(row) > 8 else False,
                'water': bool(row[9]) if len(row) > 9 else False,
                'restroom': bool(row[10]) if len(row) > 10 else False,
                'timestamp': row[1] if len(row) > 1 else datetime.now().isoformat(),
                'source': 'hardware'
            }
        else:
            return {
                'bpm': 0,
                'lat': 0.0,
                'lng': 0.0,
                'panic': False,
                'fall': False,
                'sound': False,
                'food': False,
                'water': False,
                'restroom': False,
                'timestamp': datetime.now().isoformat(),
                'source': 'no_data'
            }
            
    except Exception as e:
        print(f"❌ Hardware error: {e}")
        return {
            'bpm': 0,
            'lat': 0.0,
            'lng': 0.0,
            'panic': False,
            'fall': False,
            'sound': False,
            'food': False,
            'water': False,
            'restroom': False,
            'timestamp': datetime.now().isoformat(),
            'source': 'error'
        }

def get_sensor_logger_data():
    """Get latest data from Sensor Logger (mobile app via HTTP)"""
    try:
        if SENSOR_LOGGER_AVAILABLE:
            state_data = global_state.get_current()
            
            location = state_data.get('location', {}) or {}
            
            return {
                'steps': state_data.get('steps', 0),
                'activity': state_data.get('activity', 'Unknown'),
                'sound_db': state_data.get('sound_db', 0),
                'lat': float(location.get('lat', 0.0)),
                'lng': float(location.get('lon', 0.0)),
                'alert': state_data.get('alert'),
                'is_emergency': state_data.get('is_emergency', False),
                'timestamp': datetime.now().isoformat(),
                'source': 'sensor_logger'
            }
        else:
            return {
                'steps': 0,
                'activity': 'Unknown',
                'sound_db': 0,
                'lat': 0.0,
                'lng': 0.0,
                'alert': None,
                'is_emergency': False,
                'timestamp': datetime.now().isoformat(),
                'source': 'no_sensor_logger'
            }
            
    except Exception as e:
        print(f"❌ Sensor Logger error: {e}")
        return {
            'steps': 0,
            'activity': 'Unknown',
            'sound_db': 0,
            'lat': 0.0,
            'lng': 0.0,
            'alert': None,
            'is_emergency': False,
            'timestamp': datetime.now().isoformat(),
            'source': 'error'
        }

@app.route('/api/hardware')
def hardware_endpoint():
    """ESP32 hardware data"""
    return jsonify(get_hardware_data())

@app.route('/api/mobile')
def mobile_endpoint():
    """Sensor Logger mobile data"""
    return jsonify(get_sensor_logger_data())

@app.route('/api/fusion')
def fusion_endpoint():
    """Combined data with distance calculation"""
    hardware = get_hardware_data()
    mobile = get_sensor_logger_data()
    
    # Calculate distance
    from math import radians, cos, sin, asin, sqrt
    
    def haversine(lon1, lat1, lon2, lat2):
        if lat1 == 0 or lat2 == 0:
            return 0
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return c * 6371000  # Earth radius in meters
    
    distance = haversine(
        hardware.get('lng', 0), hardware.get('lat', 0),
        mobile.get('lng', 0), mobile.get('lat', 0)
    )
    
    return jsonify({
        'hardware': hardware,
        'mobile': mobile,
        'distance_meters': round(distance, 2),
        'leash_broken': distance > 50,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status')
def status_endpoint():
    """System status"""
    # Check if sensor logger backend is running
    sensor_logger_running = False
    try:
        response = requests.get(f'http://{LAPTOP_IP}:{SENSOR_LOGGER_PORT}/docs', timeout=1)
        sensor_logger_running = response.status_code == 200
    except:
        pass
    
    return jsonify({
        'laptop_ip': LAPTOP_IP,
        'sensor_logger_port': SENSOR_LOGGER_PORT,
        'bridge_port': BRIDGE_PORT,
        'hardware_db_exists': os.path.exists(HARDWARE_DB_PATH),
        'sensor_logger_imported': SENSOR_LOGGER_AVAILABLE,
        'sensor_logger_backend_running': sensor_logger_running,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/')
def index():
    """Status page"""
    hardware_status = "✅ Found" if os.path.exists(HARDWARE_DB_PATH) else "❌ Not Found"
    sensor_import = "✅ Imported" if SENSOR_LOGGER_AVAILABLE else "❌ Failed"
    
    # Check sensor logger backend
    sensor_backend = "❌ Not Running"
    try:
        response = requests.get(f'http://{LAPTOP_IP}:{SENSOR_LOGGER_PORT}/docs', timeout=1)
        if response.status_code == 200:
            sensor_backend = "✅ Running"
    except:
        pass
    
    return f'''
    <h1>🛡️ AUTIGUARD Bridge</h1>
    <h2>Configuration</h2>
    <ul>
        <li><strong>Laptop IP:</strong> {LAPTOP_IP}</li>
        <li><strong>Sensor Logger Port:</strong> {SENSOR_LOGGER_PORT}</li>
        <li><strong>Bridge Port:</strong> {BRIDGE_PORT}</li>
    </ul>
    
    <h2>Backend Status</h2>
    <ul>
        <li><strong>Hardware DB:</strong> {hardware_status}</li>
        <li><strong>Sensor Logger Import:</strong> {sensor_import}</li>
        <li><strong>Sensor Logger Backend:</strong> {sensor_backend}</li>
    </ul>
    
    <h2>API Endpoints</h2>
    <ul>
        <li><a href="/api/hardware">Hardware Data</a></li>
        <li><a href="/api/mobile">Mobile Data</a></li>
        <li><a href="/api/fusion">Fusion Data</a></li>
        <li><a href="/api/status">Status</a></li>
    </ul>
    
    <h2>Setup</h2>
    <ol>
        <li>Start Sensor Logger: <code>cd "{SENSOR_LOGGER_PATH}" && python main.py</code></li>
        <li>Configure app to POST to: <code>{LAPTOP_IP}:{SENSOR_LOGGER_PORT}/data</code></li>
        <li>Start ESP32 backend (optional)</li>
        <li>Start Flutter app</li>
    </ol>
    '''

if __name__ == '__main__':
    print("🛡️  AUTIGUARD Bridge Starting...")
    print(f"💻 Laptop IP: {LAPTOP_IP}")
    print(f"📱 Sensor Logger: {LAPTOP_IP}:{SENSOR_LOGGER_PORT}")
    print(f"🔗 Bridge: http://localhost:{BRIDGE_PORT}")
    print(f"📊 Hardware DB: {HARDWARE_DB_PATH}")
    print(f"📱 Sensor Logger Path: {SENSOR_LOGGER_PATH}")
    
    app.run(host='0.0.0.0', port=BRIDGE_PORT, debug=True)