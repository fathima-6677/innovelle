#!/usr/bin/env python3
"""
AEGIS Hardware Simulator - GUI Version
Interactive GUI for controlling ESP32 wearable simulation
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import requests
from datetime import datetime
import random
import math

class AegisSimulatorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AEGIS ESP32 Hardware Simulator")
        self.root.geometry("600x700")
        self.root.configure(bg='#1a1a1a')
        
        # Simulation state
        self.running = False
        self.sim_thread = None
        
        # Hardware data
        self.bpm = 75
        self.panic_pressed = False
        self.steps = 0
        self.latitude = 11.9416
        self.longitude = 79.8083
        self.battery_level = 85
        self.current_scenario = 'normal'
        
        # Scenarios
        self.scenarios = {
            'normal': {'bpm_range': (70, 85), 'color': '#4CAF50'},
            'exercise': {'bpm_range': (120, 160), 'color': '#FF9800'},
            'stress': {'bpm_range': (90, 110), 'color': '#FFC107'},
            'emergency': {'bpm_range': (140, 180), 'color': '#F44336'},
            'medical': {'bpm_range': (45, 200), 'color': '#9C27B0'}
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the GUI interface"""
        # Title
        title_frame = tk.Frame(self.root, bg='#1a1a1a')
        title_frame.pack(pady=10)
        
        title_label = tk.Label(
            title_frame, 
            text="🛡️ AEGIS ESP32 Hardware Simulator",
            font=('Arial', 16, 'bold'),
            fg='#00ff00',
            bg='#1a1a1a'
        )
        title_label.pack()
        
        # Status display
        self.setup_status_display()
        
        # Control panels
        self.setup_scenario_controls()
        self.setup_manual_controls()
        self.setup_simulation_controls()
        
        # Log display
        self.setup_log_display()
        
    def setup_status_display(self):
        """Setup real-time status display"""
        status_frame = tk.LabelFrame(
            self.root, 
            text="📊 Live Hardware Status",
            font=('Arial', 12, 'bold'),
            fg='#00ff00',
            bg='#2a2a2a'
        )
        status_frame.pack(pady=10, padx=20, fill='x')
        
        # BPM display
        bpm_frame = tk.Frame(status_frame, bg='#2a2a2a')
        bpm_frame.pack(pady=5, fill='x')
        
        tk.Label(bpm_frame, text="💓 BPM:", font=('Arial', 10), fg='white', bg='#2a2a2a').pack(side='left')
        self.bpm_label = tk.Label(bpm_frame, text="75", font=('Arial', 14, 'bold'), fg='#ff4444', bg='#2a2a2a')
        self.bpm_label.pack(side='left', padx=10)
        
        # Panic status
        panic_frame = tk.Frame(status_frame, bg='#2a2a2a')
        panic_frame.pack(pady=5, fill='x')
        
        tk.Label(panic_frame, text="🚨 Panic:", font=('Arial', 10), fg='white', bg='#2a2a2a').pack(side='left')
        self.panic_label = tk.Label(panic_frame, text="INACTIVE", font=('Arial', 12, 'bold'), fg='#44ff44', bg='#2a2a2a')
        self.panic_label.pack(side='left', padx=10)
        
        # Steps and battery
        info_frame = tk.Frame(status_frame, bg='#2a2a2a')
        info_frame.pack(pady=5, fill='x')
        
        tk.Label(info_frame, text="👣 Steps:", font=('Arial', 10), fg='white', bg='#2a2a2a').pack(side='left')
        self.steps_label = tk.Label(info_frame, text="0", font=('Arial', 10), fg='#44ff44', bg='#2a2a2a')
        self.steps_label.pack(side='left', padx=10)
        
        tk.Label(info_frame, text="🔋 Battery:", font=('Arial', 10), fg='white', bg='#2a2a2a').pack(side='left', padx=(20,0))
        self.battery_label = tk.Label(info_frame, text="85%", font=('Arial', 10), fg='#44ff44', bg='#2a2a2a')
        self.battery_label.pack(side='left', padx=10)
        
        # GPS coordinates
        gps_frame = tk.Frame(status_frame, bg='#2a2a2a')
        gps_frame.pack(pady=5, fill='x')
        
        tk.Label(gps_frame, text="📍 GPS:", font=('Arial', 10), fg='white', bg='#2a2a2a').pack(side='left')
        self.gps_label = tk.Label(gps_frame, text="11.9416, 79.8083", font=('Arial', 10), fg='#44ff44', bg='#2a2a2a')
        self.gps_label.pack(side='left', padx=10)
        
    def setup_scenario_controls(self):
        """Setup scenario selection controls"""
        scenario_frame = tk.LabelFrame(
            self.root,
            text="🎭 Simulation Scenarios",
            font=('Arial', 12, 'bold'),
            fg='#00ff00',
            bg='#2a2a2a'
        )
        scenario_frame.pack(pady=10, padx=20, fill='x')
        
        # Scenario buttons
        button_frame = tk.Frame(scenario_frame, bg='#2a2a2a')
        button_frame.pack(pady=10)
        
        for scenario, config in self.scenarios.items():
            btn = tk.Button(
                button_frame,
                text=scenario.upper(),
                command=lambda s=scenario: self.change_scenario(s),
                bg=config['color'],
                fg='white',
                font=('Arial', 10, 'bold'),
                width=10
            )
            btn.pack(side='left', padx=5)
        
        # Current scenario display
        self.scenario_label = tk.Label(
            scenario_frame,
            text=f"Current: {self.current_scenario.upper()}",
            font=('Arial', 12, 'bold'),
            fg='#4CAF50',
            bg='#2a2a2a'
        )
        self.scenario_label.pack(pady=5)
        
    def setup_manual_controls(self):
        """Setup manual control buttons"""
        control_frame = tk.LabelFrame(
            self.root,
            text="🎮 Manual Controls",
            font=('Arial', 12, 'bold'),
            fg='#00ff00',
            bg='#2a2a2a'
        )
        control_frame.pack(pady=10, padx=20, fill='x')
        
        # Button row 1
        btn_row1 = tk.Frame(control_frame, bg='#2a2a2a')
        btn_row1.pack(pady=5)
        
        tk.Button(
            btn_row1,
            text="🚨 PANIC BUTTON",
            command=self.trigger_panic,
            bg='#ff4444',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=15
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_row1,
            text="🔋 LOW BATTERY",
            command=self.set_low_battery,
            bg='#ff8800',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=15
        ).pack(side='left', padx=5)
        
        # Button row 2
        btn_row2 = tk.Frame(control_frame, bg='#2a2a2a')
        btn_row2.pack(pady=5)
        
        tk.Button(
            btn_row2,
            text="📍 RANDOM GPS",
            command=self.randomize_gps,
            bg='#4444ff',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=15
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_row2,
            text="👣 ADD STEPS",
            command=self.add_steps,
            bg='#44ff44',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=15
        ).pack(side='left', padx=5)
        
    def setup_simulation_controls(self):
        """Setup simulation start/stop controls"""
        sim_frame = tk.LabelFrame(
            self.root,
            text="⚙️ Simulation Control",
            font=('Arial', 12, 'bold'),
            fg='#00ff00',
            bg='#2a2a2a'
        )
        sim_frame.pack(pady=10, padx=20, fill='x')
        
        # Control buttons
        control_buttons = tk.Frame(sim_frame, bg='#2a2a2a')
        control_buttons.pack(pady=10)
        
        self.start_btn = tk.Button(
            control_buttons,
            text="▶️ START SIMULATION",
            command=self.start_simulation,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=20
        )
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = tk.Button(
            control_buttons,
            text="⏹️ STOP SIMULATION",
            command=self.stop_simulation,
            bg='#F44336',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=20,
            state='disabled'
        )
        self.stop_btn.pack(side='left', padx=5)
        
        # Status indicator
        self.sim_status_label = tk.Label(
            sim_frame,
            text="Status: STOPPED",
            font=('Arial', 12, 'bold'),
            fg='#ff4444',
            bg='#2a2a2a'
        )
        self.sim_status_label.pack(pady=5)
        
    def setup_log_display(self):
        """Setup log display area"""
        log_frame = tk.LabelFrame(
            self.root,
            text="📝 Activity Log",
            font=('Arial', 12, 'bold'),
            fg='#00ff00',
            bg='#2a2a2a'
        )
        log_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        # Text widget with scrollbar
        text_frame = tk.Frame(log_frame, bg='#2a2a2a')
        text_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.log_text = tk.Text(
            text_frame,
            bg='#1a1a1a',
            fg='#00ff00',
            font=('Consolas', 9),
            wrap='word'
        )
        
        scrollbar = tk.Scrollbar(text_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def log_message(self, message):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert('end', log_entry)
        self.log_text.see('end')
        
        # Limit log size
        if int(self.log_text.index('end-1c').split('.')[0]) > 100:
            self.log_text.delete('1.0', '10.0')
    
    def update_display(self):
        """Update the GUI display with current values"""
        self.bpm_label.config(text=str(self.bpm))
        
        if self.panic_pressed:
            self.panic_label.config(text="ACTIVE", fg='#ff4444')
        else:
            self.panic_label.config(text="INACTIVE", fg='#44ff44')
            
        self.steps_label.config(text=str(self.steps))
        self.battery_label.config(text=f"{self.battery_level}%")
        self.gps_label.config(text=f"{self.latitude:.6f}, {self.longitude:.6f}")
        
        # Update scenario display
        scenario_color = self.scenarios[self.current_scenario]['color']
        self.scenario_label.config(
            text=f"Current: {self.current_scenario.upper()}",
            fg=scenario_color
        )
    
    def change_scenario(self, scenario):
        """Change simulation scenario"""
        self.current_scenario = scenario
        self.log_message(f"🎭 Scenario changed to: {scenario.upper()}")
        self.update_display()
    
    def trigger_panic(self):
        """Manually trigger panic button"""
        self.panic_pressed = True
        self.log_message("🚨 MANUAL PANIC BUTTON TRIGGERED!")
        self.update_display()
        
        # Auto-reset after 3 seconds
        self.root.after(3000, lambda: setattr(self, 'panic_pressed', False))
    
    def set_low_battery(self):
        """Set battery to low level"""
        self.battery_level = 15
        self.log_message("🔋 Battery set to LOW (15%)")
        self.update_display()
    
    def randomize_gps(self):
        """Randomize GPS coordinates"""
        self.latitude += random.uniform(-0.001, 0.001)
        self.longitude += random.uniform(-0.001, 0.001)
        self.log_message(f"📍 GPS randomized: {self.latitude:.6f}, {self.longitude:.6f}")
        self.update_display()
    
    def add_steps(self):
        """Add random steps"""
        added_steps = random.randint(10, 50)
        self.steps += added_steps
        self.log_message(f"👣 Added {added_steps} steps (Total: {self.steps})")
        self.update_display()
    
    def generate_realistic_bpm(self):
        """Generate realistic BPM based on scenario"""
        scenario_config = self.scenarios[self.current_scenario]
        base_bpm = random.randint(*scenario_config['bpm_range'])
        
        # Add natural variation
        variation = random.uniform(-5, 5)
        time_factor = math.sin(time.time() / 3600) * 3
        
        self.bpm = max(40, min(200, int(base_bpm + variation + time_factor)))
    
    def send_data_to_backend(self):
        """Send data to Autiguard backend"""
        try:
            data = {
                'bpm': self.bpm,
                'panic': self.panic_pressed,
                'steps': self.steps,
                'latitude': self.latitude,
                'longitude': self.longitude,
                'battery': self.battery_level,
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(
                'http://10.123.50.141:8001/api/hardware-data',
                json=data,
                timeout=2
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.log_message(f"❌ Backend error: {e}")
            return False
    
    def simulation_loop(self):
        """Main simulation loop"""
        cycle_count = 0
        
        while self.running:
            try:
                # Generate new data
                self.generate_realistic_bpm()
                
                # Simulate movement
                if random.random() < 0.3:
                    self.steps += random.randint(1, 3)
                
                # GPS drift
                if random.random() < 0.1:
                    self.latitude += random.uniform(-0.0001, 0.0001)
                    self.longitude += random.uniform(-0.0001, 0.0001)
                
                # Battery drain
                if random.random() < 0.01:
                    self.battery_level = max(0, self.battery_level - 1)
                
                # Send to backend
                success = self.send_data_to_backend()
                
                # Update GUI (thread-safe)
                self.root.after(0, self.update_display)
                
                # Log every 10 cycles
                if cycle_count % 10 == 0:
                    status = "✅" if success else "❌"
                    self.root.after(0, lambda: self.log_message(
                        f"{status} BPM:{self.bpm} PANIC:{self.panic_pressed} STEPS:{self.steps} BAT:{self.battery_level}%"
                    ))
                
                cycle_count += 1
                time.sleep(0.1)  # 100ms cycle
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"❌ Simulation error: {e}"))
                time.sleep(1)
    
    def start_simulation(self):
        """Start the simulation"""
        if not self.running:
            self.running = True
            self.sim_thread = threading.Thread(target=self.simulation_loop)
            self.sim_thread.daemon = True
            self.sim_thread.start()
            
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.sim_status_label.config(text="Status: RUNNING", fg='#44ff44')
            
            self.log_message("🚀 AEGIS Hardware Simulation STARTED")
    
    def stop_simulation(self):
        """Stop the simulation"""
        if self.running:
            self.running = False
            
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.sim_status_label.config(text="Status: STOPPED", fg='#ff4444')
            
            self.log_message("🛑 AEGIS Hardware Simulation STOPPED")
    
    def run(self):
        """Start the GUI application"""
        self.log_message("🛡️ AEGIS Hardware Simulator GUI Ready")
        self.log_message("📡 Backend: http://10.123.50.141:8001")
        self.update_display()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing"""
        if self.running:
            self.stop_simulation()
        self.root.destroy()

if __name__ == "__main__":
    app = AegisSimulatorGUI()
    app.run()