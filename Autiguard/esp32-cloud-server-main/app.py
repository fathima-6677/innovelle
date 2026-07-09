from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('wearable.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sensor_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT, lat REAL, lng REAL, bmp INTEGER,
                  panic BOOLEAN, fall BOOLEAN, sound BOOLEAN,
                  food BOOLEAN, water BOOLEAN, restroom BOOLEAN)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/api/data', methods=['POST'])
def receive_data():
    try:
        data = request.json
        conn = sqlite3.connect('wearable.db')
        c = conn.cursor()
        c.execute('''INSERT INTO sensor_data (timestamp, lat, lng, bmp, panic, fall, sound, food, water, restroom)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.get('lat',0.0), data.get('lng',0.0), data.get('bmp',0),
                   data.get('panic',False), data.get('fall',False), data.get('sound',False), data.get('food',False), data.get('water',False), data.get('restroom',False)))
        conn.commit(); conn.close()
        return jsonify({"status": "success"}), 200
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/latest')
def get_latest():
    conn = sqlite3.connect('wearable.db')
    c = conn.cursor()
    c.execute('SELECT * FROM sensor_data ORDER BY id DESC LIMIT 1')
    row = c.fetchone()
    conn.close()
    if row:
        return jsonify({"timestamp": row[1], "lat": row[2], "lng": row[3], "bmp": row[4], "panic": bool(row[5]), "fall": bool(row[6]), "sound": bool(row[7]), "food": bool(row[8]), "water": bool(row[9]), "restroom": bool(row[10])})
    return jsonify({"error": "No data"})

@app.route('/')
def index():
    return jsonify({"status": "ESP32 Backend API", "endpoints": ["/api/data", "/api/latest"]})

if __name__ == '__main__': app.run(host='0.0.0.0', port=5001)
