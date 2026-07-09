/*
 * AEGIS.SYS ESP32 Serial Streamer
 * Arduino Nano ESP32 - High-Speed Telemetry Bridge
 * COM3 @ 115200 baud - Zero Latency Demo
 */

// Pin Definitions
#define BPM_SENSOR_PIN A0      // Analog pin for BPM sensor (simulated)
#define PANIC_BUTTON_PIN 2     // Digital pin for panic button
#define LED_STATUS_PIN 13      // Built-in LED for status indication

// Simulation Variables
unsigned long lastUpdate = 0;
unsigned long stepCounter = 1240;  // Starting step count
int baseBPM = 75;                  // Base heart rate
bool panicState = false;
unsigned long panicPressTime = 0;

// Sensor smoothing
float bpmSmoothed = 75.0;
const float BPM_ALPHA = 0.3;  // Smoothing factor

void setup() {
  // Initialize Serial Communication
  Serial.begin(115200);
  
  // Configure Pins
  pinMode(PANIC_BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_STATUS_PIN, OUTPUT);
  
  // Initialize random seed
  randomSeed(analogRead(A1));
  
  // Startup sequence
  digitalWrite(LED_STATUS_PIN, HIGH);
  delay(500);
  digitalWrite(LED_STATUS_PIN, LOW);
  
  Serial.println("AEGIS.SYS ESP32 INITIALIZED");
  Serial.println("SERIAL BRIDGE ACTIVE ON COM3");
  Serial.println("FORMAT: BPM:XX,PANIC:X,STEPS:XXXX");
  
  delay(1000);
}

void loop() {
  unsigned long currentTime = millis();
  
  // Update every 100ms for high-frequency telemetry
  if (currentTime - lastUpdate >= 100) {
    lastUpdate = currentTime;
    
    // Read and process sensors
    readBPMSensor();
    readPanicButton();
    updateStepSimulator();
    
    // Transmit telemetry data
    transmitTelemetry();
    
    // Status LED heartbeat
    updateStatusLED();
  }
}

void readBPMSensor() {
  // Simulate realistic BPM sensor reading
  int rawBPM = analogRead(BPM_SENSOR_PIN);
  
  // Convert analog reading to BPM (simulate sensor behavior)
  float simulatedBPM = baseBPM + sin(millis() / 1000.0) * 5 + random(-3, 4);
  
  // Add panic state influence
  if (panicState) {
    simulatedBPM += 20 + random(0, 15);  // Elevated heart rate during panic
  }
  
  // Clamp to realistic range
  simulatedBPM = constrain(simulatedBPM, 60, 180);
  
  // Apply smoothing filter
  bpmSmoothed = (BPM_ALPHA * simulatedBPM) + ((1.0 - BPM_ALPHA) * bpmSmoothed);
}

void readPanicButton() {
  bool buttonPressed = !digitalRead(PANIC_BUTTON_PIN);  // Active LOW
  
  if (buttonPressed && !panicState) {
    // Panic button pressed - activate emergency state
    panicState = true;
    panicPressTime = millis();
    Serial.println("EMERGENCY: PANIC BUTTON ACTIVATED");
  } else if (panicState && (millis() - panicPressTime > 5000)) {
    // Auto-reset panic state after 5 seconds (for demo)
    panicState = false;
    Serial.println("EMERGENCY: PANIC STATE RESET");
  }
}

void updateStepSimulator() {
  // Simulate step counting based on activity level
  static unsigned long lastStepTime = 0;
  
  if (millis() - lastStepTime > random(800, 2000)) {  // Variable step interval
    stepCounter++;
    lastStepTime = millis();
    
    // Occasional step bursts (simulating walking/running)
    if (random(0, 100) < 10) {  // 10% chance of burst
      stepCounter += random(1, 5);
    }
  }
}

void transmitTelemetry() {
  // Format: BPM:XX,PANIC:X,STEPS:XXXX
  Serial.print("BPM:");
  Serial.print((int)bpmSmoothed);
  Serial.print(",PANIC:");
  Serial.print(panicState ? 1 : 0);
  Serial.print(",STEPS:");
  Serial.println(stepCounter);
}

void updateStatusLED() {
  // Heartbeat pattern on status LED
  static unsigned long ledTime = 0;
  static bool ledState = false;
  
  if (millis() - ledTime > (panicState ? 200 : 1000)) {  // Faster blink during panic
    ledState = !ledState;
    digitalWrite(LED_STATUS_PIN, ledState);
    ledTime = millis();
  }
}

// Additional utility functions for enhanced demo

void printSystemInfo() {
  Serial.println("=== AEGIS.SYS SYSTEM INFO ===");
  Serial.print("Uptime: ");
  Serial.print(millis() / 1000);
  Serial.println(" seconds");
  Serial.print("Current BPM: ");
  Serial.println((int)bpmSmoothed);
  Serial.print("Step Count: ");
  Serial.println(stepCounter);
  Serial.print("Panic State: ");
  Serial.println(panicState ? "ACTIVE" : "NORMAL");
  Serial.println("=============================");
}

// Handle serial commands (optional for debugging)
void serialEvent() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "INFO") {
      printSystemInfo();
    } else if (command == "RESET") {
      stepCounter = 0;
      panicState = false;
      Serial.println("SYSTEM RESET COMPLETE");
    } else if (command.startsWith("BPM:")) {
      int newBPM = command.substring(4).toInt();
      if (newBPM >= 60 && newBPM <= 180) {
        baseBPM = newBPM;
        Serial.print("BASE BPM SET TO: ");
        Serial.println(baseBPM);
      }
    }
  }
}