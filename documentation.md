<div style="font-size: 10pt; line-height: 1.2; color: #333;">

## Real-Time Production Line Sensor Dashboard
#### *Technical Specification for Industrial Monitoring Systems*

**Developer:** *Rawan Sleem*  
**Contact:** [rawan.sleem2000@gmail.com](mailto:rawan.sleem2000@gmail.com) | [linkedin.com/in/rawansleem](https://www.linkedin.com/in/rawansleem/)  
**Date:** *December 2025*   
**Version:** *1.0.0*

</div>

---

### Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture Overview](#2-system-architecture-overview)
   - 2.1 [High-Level Architecture](#21-high-level-architecture)
   - 2.2 [Component Interaction Diagram](#22-component-interaction-diagram)
   - 2.3 [Technology Stack](#23-technology-stack)
3. [Theoretical Foundations](#3-theoretical-foundations)
   - 3.1 [Multithreading Concepts](#31-multithreading-concepts)
   - 3.2 [Network Communication Protocols](#32-network-communication-protocols)
   - 3.3 [Real-Time Data Processing](#33-real-time-data-processing)
   - 3.4 [Observer Pattern & Signal-Slot Mechanism](#34-observer-pattern--signal-slot-mechanism)
4. [Core Functionality Implementation](#4-core-functionality-implementation)
   - 4.1 [Sensor Monitoring System](#41-sensor-monitoring-system)
   - 4.2 [Multithreading Architecture](#42-multithreading-architecture)
   - 4.3 [Real-Time GUI Responsiveness](#43-real-time-gui-responsiveness)
   - 4.4 [Alarm System](#44-alarm-system)
5. [Code Structure & Architecture](#5-code-structure--architecture)
   - 5.1 [Project File Organization](#51-project-file-organization)
   - 5.2 [Module Descriptions](#52-module-descriptions)
   - 5.3 [Class Hierarchy](#53-class-hierarchy)
   - 5.4 [Design Patterns](#54-design-patterns)
6. [Thread Safety & Synchronization](#6-thread-safety--synchronization)
   - 6.1 [Thread Safety Principles](#61-thread-safety-principles)
   - 6.2 [Signal-Slot Thread Communication](#62-signal-slot-thread-communication)
   - 6.3 [Race Condition Prevention](#63-race-condition-prevention)
   - 6.4 [Resource Management](#64-resource-management)
7. [Network Communication Layer](#7-network-communication-layer)
   - 7.1 [TCP Socket Implementation](#71-tcp-socket-implementation)
   - 7.2 [WebSocket Alternative](#72-websocket-alternative)
   - 7.3 [Protocol Specification](#73-protocol-specification)
   - 7.4 [Error Handling & Recovery](#74-error-handling--recovery)
8. [GUI Design & User Experience](#8-gui-design--user-experience)
   - 8.1 [UI Architecture](#81-ui-architecture)
   - 8.2 [Responsive Design](#82-responsive-design)
   - 8.3 [Visual Feedback Systems](#83-visual-feedback-systems)
   - 8.4 [User Interaction Flow](#84-user-interaction-flow)
9. [Simulator Design](#9-simulator-design)
   - 9.1 [Simulator Architecture](#91-simulator-architecture)
   - 9.2 [Data Generation Algorithm](#92-data-generation-algorithm)
   - 9.3 [Protocol Compliance](#93-protocol-compliance)
10. [Bonus Features](#10-bonus-features)
    - 10.1 [Offline Data Replay](#101-offline-data-replay)
    - 10.2 [Session Export System](#102-session-export-system)
    - 10.3 [Desktop Notifications](#103-desktop-notifications)
    - 10.4 [Maintenance Access Control](#104-maintenance-access-control)
11. [Testing Strategy](#11-testing-strategy)
    - 11.1 [Unit Testing](#111-unit-testing)
12. [Deployment & Usage](#13-deployment--usage)
    - 13.1 [Installation Guide](#131-installation-guide)
    - 13.2 [Configuration](#132-configuration)
    - 13.3 [Running the Application](#133-running-the-application)
13. [Conclusion](#15-conclusion)
14. [Appendices](#16-appendices)

---


#### 1. Executive Summary

The **Real-Time Production Line Sensor Dashboard** is a comprehensive industrial monitoring solution designed to provide real-time visualization and analysis of multiple sensor data streams in a production environment. The system demonstrates advanced software engineering principles including multithreading, network communication, and responsive GUI design.

##### Key Features:
- **6+ Concurrent Sensor Monitoring**: Temperature, Pressure, Vibration, Speed, Optical, and Humidity,,,
- **Real-Time Data Visualization**: Live graphs with 20-second sliding windows
- **Multi-Protocol Support**: TCP sockets and WebSocket implementations
- **Intelligent Alarm System**: Automatic threshold detection with desktop notifications
- **Offline Data Analysis**: Replay capability for historical data
- **Thread-Safe Architecture**: Proper synchronization and signal-slot communication

---





#### 2. System Architecture Overview

##### 2.1 High-Level Architecture

The system follows a **multi-tier architecture** 

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Dashboard (Main GUI Thread)                  │   │
│  │  - Monitoring Tab                                     │   │
│  │  - Maintenance Console                                │   │
│  │  - Status Indicators                                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ▲ ▼ (Qt Signals)
┌─────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Worker Threads (Separate Threads)            │   │
│  │  - SensorWorker (TCP)                                 │   │
│  │  - WebSocketWorker (WS)                               │   │
│  │  - OfflineReplayWorker (File I/O)                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ▲ ▼ (Socket/File I/O)
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Simulator (Separate Process)                 │   │
│  │  - TCP Server                                         │   │
│  │  - WebSocket Server                                   │   │
│  │  - Data Generation Engine                             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

##### 2.2 Component Interaction Diagram

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│              │         │              │         │              │
│  Simulator   │◄────────│ SensorWorker │◄────────│  Dashboard   │
│   (Server)   │  TCP    │   (Thread)   │ Signal  │   (Main)     │
│              │────────►│              │────────►│              │
└──────────────┘  JSON   └──────────────┘  Slot   └──────────────┘
                                                           │
                                                           │
                                                           ▼
                                                   ┌──────────────┐
                                                   │  PyQtGraph   │
                                                   │  (Plotting)  │
                                                   └──────────────┘
```

##### 2.3 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **GUI Framework** | PyQt6 | Modern, cross-platform GUI development |
| **Plotting Engine** | PyQtGraph | High-performance real-time plotting |
| **Network Protocol** | TCP Sockets | Reliable data streaming |
| **Alternative Protocol** | WebSockets | Bidirectional communication |
| **Threading** | QThread | Thread management and synchronization |
| **Data Format** | JSON | Lightweight data interchange |
| **Notifications** | Plyer | Cross-platform desktop notifications |
| **Configuration** | JSON | External configuration management |
| **Testing** | unittest | Unit and integration testing |

---

#### 3. Theoretical Foundations

###### 3.1 Multithreading

In real-time monitoring systems, **blocking operations** (like network I/O) can freeze the GUI, making the application unresponsive. Multithreading solves this by:

1. **Separating I/O from UI**: Network operations run on worker threads
2. **Maintaining Responsiveness**: GUI thread remains free for user interactions
3. **Parallel Processing**: Multiple sensors can be processed concurrently

for a multithreaded architecture, a separate sensor worker is responsible for handling data reception form the server (simulator)

###### 3.1.2 Thread Lifecycle

```python
# Thread Creation
worker = SensorWorker()

# Thread Initialization
worker.data_received.connect(self.update_dashboard)

# Thread Execution
worker.start()  # OS allocates resources, calls run()

# Thread Termination
worker.stop()   # Set flag to False
worker.wait()   # Wait for thread to finish
```

**Key Principle**: The `run()` method executes in a separate secondary thread, while signals are delivered to the main thread.



##### 3.2 Network Communication Protocols

###### 3.2.1 TCP Socket Architecture

**TCP (Transmission Control Protocol)** provides:
- **Reliable delivery**: Guaranteed packet order
- **Connection-oriented**: Persistent connection
- **Error checking**: Built-in data integrity

**Implementation Flow**:
```python
# Server Side (Simulator)
server_socket.bind((host, port))
server_socket.listen(1)
conn, addr = server_socket.accept()  # Blocks until connection
conn.sendall(data)

# Client Side (Worker)
client.connect((host, port))  # Blocks until connected
data = client.recv(4096)      # Blocks until data arrives
```

###### 3.2.2 WebSocket Protocol *(optional)*

WebSockets provide:
- **Full-duplex communication**: Bidirectional data flow
- **Lower overhead**: After handshake, minimal protocol overhead
- **Native support**: Built into modern systems

```python
# Async/await pattern for non-blocking I/O
async with websockets.connect(url) as ws:
    message = await ws.recv()
```

##### 3.3 Real-Time Data Processing

###### 3.3.1 Sliding Window Algorithm

For 20-second real-time graphs:

```python
while self.plot_times[name] and self.plot_times[name][0] < curr_time - 20:
    self.plot_times[name].pop(0)
    self.plot_data[name].pop(0)
```


###### 3.3.2 Data Flow Pipeline

```
Raw Socket Data → JSON Parse → Validation → UI Update → Graph Render
     (Worker)       (Worker)    (Worker)     (Main)      (Main)
```

##### 3.4 Observer Pattern & Signal-Slot Mechanism

###### 3.4.1 Qt's Signal-Slot Architecture

**Signals** are event emitters, **Slots** are event handlers.

```python
# Signal Declaration (in Worker)
data_received = pyqtSignal(list)

# Signal Emission (in Worker Thread)
self.data_received.emit(sensor_list)

# Slot Connection (in Main Thread)
worker.data_received.connect(self.update_dashboard)

# Slot Execution (in Main Thread)
def update_dashboard(self, sensor_list):
    # Process data safely in GUI thread
```

**Thread Safety Guarantee**: Qt automatically queues signals across threads, ensuring thread-safe communication.

---

#### 4. Core Functionality Implementation

##### 4.1 Sensor Monitoring System

###### 4.1.1 Six Sensor Configuration

The system monitors these industrial parameters:

| Sensor | Range | Unit | Variation | Purpose |
|--------|-------|------|-----------|---------|
| **Temperature** | 50-70 | °C | ±8 | Thermal monitoring |
| **Pressure** | 65-85 | PSI | ±8 | Hydraulic systems |
| **Vibration** | 20-35 | Hz | ±8 | Mechanical health |
| **Speed** | 40-60 | RPM | ±8 | Motor velocity |
| **Optical** | 20-40 | Lux | ±8 | Vision systems |
| **Humidity** | 30-50 | %RH | ±8 | Environmental control |

###### 4.1.2 Data Structure

```python
{
    "name": "Temperature",
    "value": 65.34,
    "timestamp": "14:23:45",
    "status": "OK" | "HIGH ALARM" | "LOW ALARM"
}
```

###### 4.1.3 Update Frequency

- **Sampling Rate**: 2 Hz (every 0.5 seconds)
- **Rationale**: Balances responsiveness with system load
- **Network Throughput**: ~1.2 KB/s for 6 sensors

##### 4.2 Multithreading Architecture

###### 4.2.1 Thread Hierarchy

```
Main Thread (GUI)
├── SensorWorker Thread (TCP Client)
│   ├── Socket I/O Operations
│   ├── JSON Parsing
│   └── Signal Emission
│
├── OfflineReplayWorker/Live SensorWorker Thread (File I/O)
│   ├── JSON File Reading
│   └── Signal Emission
│
└── WebSocketWorker Thread (WS Client)
    ├── Async Event Loop
    ├── WebSocket Connection
    └── Signal Emission
```

###### 4.2.2 Worker Thread Implementation

**Critical Design Elements**:

```python
class SensorWorker(QThread):
    def __init__(self):
        super().__init__()
        self._run_flag = True  # Thread control flag
        self.client = None     # Socket handle
    
    def run(self):
        # Executed in separate thread
        while self._run_flag:
            data = self.client.recv(4096)
            self.data_received.emit(parse(data))
    
    def stop(self):
        # Called from main thread
        self._run_flag = False
```

**Key Principles**:
1. **No Direct GUI Access**: Workers only emit signals
2. **Graceful Shutdown**: `stop()` sets flag, `wait()` ensures cleanup
3. **Exception Isolation**: Errors in worker don't crash GUI

###### 4.2.3 Thread Synchronization

```python
# Stopping a thread safely
if hasattr(self, 'worker') and self.worker.isRunning():
    self.worker.stop()       # Set internal flag
    self.worker.wait()       # Wait for run() to finish
```

**Race Condition Prevention**: The `wait()` call blocks the main thread until the worker thread's `run()` method completes, preventing premature resource cleanup.

##### 4.3 Real-Time GUI Responsiveness

###### 4.3.1 Event Loop Architecture

PyQt6 uses an **event-driven architecture**:

```python
app = QApplication(sys.argv)
window = Dashboard()
window.show()
sys.exit(app.exec())  # Enter event loop
```

The event loop:
1. Waits for events (mouse clicks, timer ticks, signals)
2. Dispatches events to handlers
3. Renders GUI updates
4. Returns to step 1

###### 4.3.2 Non-Blocking Updates

**Problem**: Processing 6 sensor updates + 6 graph redraws every 0.5s

**Solution**: Batch processing in single event

```python
def update_dashboard(self, sensor_list):
    # All 6 sensors processed in one signal emission
    for sensor in sensor_list:
        # Update table
        # Update graph
        # Check alarms
```

**Performance**: Single event dispatch vs. 6 separate signals = 6x reduction in context switches

##### 4.4 Alarm System

###### 4.4.1 Threshold Detection Algorithm

```python
def check_alarm(value, low, high):
    if value < low:
        return "LOW ALARM"
    elif value > high:
        return "HIGH ALARM"
    else:
        return "OK"
```

###### 4.4.2 Alarm State Management

```python
self.active_alarms = set()  # Track currently alarming sensors

if "ALARM" in status:
    if name not in self.active_alarms:
        self.active_alarms.add(name)
        self.trigger_desktop_alert(name, val, status)
else:
    if name in self.active_alarms:
        self.active_alarms.remove(name)  # Clear alarm
```

**Rationale**: Using a `set` ensures:
- O(1) lookup time
- No duplicate alarms
- Easy state tracking

###### 4.4.3 Notification Rate Limiting

```python
self.last_alert_time = {}  # Sensor name → timestamp

def trigger_desktop_alert(self, name, val, status):
    current_time = time.time()
    cooldown = 60  # seconds
    
    last_sent = self.last_alert_time.get(name, 0)
    
    if current_time - last_sent < cooldown:
        return  # Too soon, skip notification
    
    notification.notify(...)
    self.last_alert_time[name] = current_time
```

**Purpose**: Prevents notification spam during sustained alarm conditions.

---

#### 5. Code Structure & Architecture

##### 5.1 Project File Organization

```
project_root/
├── main.py                  # Entry point, Dashboard class
├── sensor_worker.py         # Worker thread implementations
├── simulator.py             # Data source simulator
├── sensors_config.json      # Configuration file
├── test_simulator.py        # Unit tests
├── requirements.txt         # Dependencies
├── icon.png                 # Application icon
├── logo.png                 # Splash screen logo
└── docs/
    └── documentation.md     # This file
```

##### 5.2 Module Descriptions

###### 5.2.1 main.py (Dashboard Module)

**Responsibilities**:
- GUI initialization and layout
- Tab management (Monitoring, Maintenance)
- Signal-slot connections
- Data visualization
- User interaction handling

**Key Classes**:
- `Dashboard(QMainWindow)`: Main application window


###### 5.2.2 sensor_worker.py (Worker Module)

**Responsibilities**:
- Network communication
- Thread lifecycle management
- Data reception and parsing
- Signal emission

**Key Classes**:
- `SensorWorker(QThread)`: TCP socket client
- `WebSocketWorker(QThread)`: WebSocket client
- `OfflineReplayWorker(QThread)`: File-based replay (offline mode)


###### 5.2.3 simulator.py (Simulator Module)

**Responsibilities**:
- Configuration loading
- Data generation
- Network server implementation
- Protocol compliance

**Key Functions**:
- `load_config()`: JSON configuration parser
- `generate_payload()`: Sensor data generator
- `run_tcp_simulator()`: TCP server loop
- `run_websocket_simulator()`: WS server with async


##### 5.3 Class Hierarchy

```
QMainWindow
    └── Dashboard
            ├── QTabWidget (tabs)
            ├── QTableWidget (sensor table)
            ├── QTableWidget (alarm table)
            ├── pg.PlotWidget × 6 (graphs)
            ├── QTextEdit (log display)
            └── QPushButton × 4 (controls)

QThread
    ├── SensorWorker
    │       └── socket.socket (TCP client)
    ├── WebSocketWorker
    │       └── websockets.connect (WS client)
    └── OfflineReplayWorker
            └── json.load (file parser)
```

##### 5.4 Design Patterns

###### 5.4.1 Observer Pattern (Signal-Slot)

**Intent**: Define a one-to-many dependency between objects

**Implementation**:
```python
# Subject (Observable)
class SensorWorker(QThread):
    data_received = pyqtSignal(list)  # Observable event
    
# Observer
class Dashboard(QMainWindow):
    def __init__(self):
        worker.data_received.connect(self.update_dashboard)
    
    def update_dashboard(self, data):  # Observer callback
        # React to data changes
```

###### 5.4.2 Strategy Pattern (Worker Selection)

**Intent**: Define a family of algorithms, encapsulate each one (differenet worker implementations)

**Implementation**:
```python
self.btn_load_offline.clicked.connect(self.load_offline_data)

```
---

#### 6. Thread Safety & Synchronization

##### 6.1 Thread Safety Principles

###### 6.1.1 What is Thread Safety?

Code is considerred thread-safe if it functions correctly during simultaneous execution by multiple threads.


###### 6.1.2 Approach

**Zero Shared Mutable State**:
- Workers maintain independent state
- GUI state only modified by main thread
- Communication via immutable messages (signals)

##### 6.2 Signal-Slot Thread Communication

###### 6.2.1 How Qt Ensures Thread Safety

When a signal is emitted from a worker thread:

```python
# Worker Thread
self.data_received.emit(sensor_list)
```

Qt performs:
1. **Serialization**: Package signal data
2. **Queue Insertion**: Add to main thread's event queue
3. **Event Dispatch**: Main thread processes queue
4. **Slot Execution**: Handler runs in main thread

**Result**: No locks needed, Qt handles synchronization automatically.


##### 6.3 Race Condition Prevention

###### 6.3.1 Potential Race Condition

```python
# BAD: Direct GUI access from worker
def run(self):
    while self._run_flag:
        data = self.client.recv(4096)
        self.table.setItem(0, 0, data)  # ❌ CRASH!
```

**Problem**: PyQt widgets are **not** thread-safe.

#### 6.3.2 Correct Implementation

```python
# GOOD: Signal emission from worker
def run(self):
    while self._run_flag:
        data = self.client.recv(4096)
        self.data_received.emit(data)  # ✅ Safe

# Slot in main thread
def update_dashboard(self, data):
    self.table.setItem(0, 0, data)  # ✅ GUI thread only
```

##### 6.4 Resource Management

###### 6.4.1 Socket Cleanup

```python
def run(self):
    try:
        self.client = socket.socket(...)
        self.client.connect((host, port))
        # ... operation ...
    finally:
        if self.client:
            self.client.close()  # Always cleanup
        self._run_flag = False
```

###### 6.4.2 Application Shutdown

```python
def closeEvent(self, event):
    if hasattr(self, 'worker') and self.worker.isRunning():
        self.worker.stop()
        self.worker.wait()  # Block until thread exits
    event.accept()
```

**Why `wait()`?**: Prevents zombie threads and ensures clean shutdown.

---

#### 7. Network Communication Layer

##### 7.1 TCP Socket Implementation

###### 7.1.1 Server (Simulator)
*without using config file for demonistration*
```python
def run_tcp_simulator():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 5555))
    server.listen(1)  # Accept 1 connection
    
    while True:
        conn, addr = server.accept()  # Blocks here
        while True:
            payload = generate_payload(...)
            conn.sendall(json.dumps(payload).encode() + b'\n')
            time.sleep(0.5)
```

**Key Points**:
- `SO_REUSEADDR`: Allows immediate port reuse after restart
- `listen(1)`: Backlog of 1 pending connection
- `accept()`: Blocks until client connects

###### 7.1.2 Client (Worker)

```python
def run(self):
    self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.client.settimeout(5.0)  # 5-second timeout
    self.client.connect(('127.0.0.1', 5555))
    
    while self._run_flag:
        try:
            raw_data = self.client.recv(4096)  # Blocks up to 5s
            if not raw_data:
                break  # Connection closed
            
            lines = raw_data.strip().split('\n')
            for line in lines:
                sensor_list = json.loads(line)
                self.data_received.emit(sensor_list)
        
        except socket.timeout:
            continue  # Normal, check _run_flag
```

**Key Points**:
- `settimeout(5.0)`: Prevents infinite blocking
- `recv(4096)`: Read up to 4KB at once
- Newline-delimited JSON for frame separation

#### 7.1.3 TCP Handshake

```
Client                          Server
  |                               |
  |-------- SYN ----------------->|
  |<------- SYN-ACK --------------|
  |-------- ACK ----------------->|
  |                               |
  |====== Connected ==============|
  |                               |
  |<------ JSON Data -------------|
  |<------ JSON Data -------------|
```

### 7.2 WebSocket Alternative

#### 7.2.1 Async Server

```python
async def sensor_data(websocket):
    while True:
        payload = generate_payload(...)
        await websocket.send(json.dumps(payload))
        await asyncio.sleep(0.5)

async def main():
    async with websockets.serve(sensor_data, "localhost", 8080):
        await asyncio.Future()  # Run forever
```

#### 7.2.2 Async Client

```python
def run(self):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(self.listen())

async def listen(self):
    async with websockets.connect(self.url) as ws:
        while self._run_flag:
            message = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(message)
            self.data_received.emit(data)
```

##### 7.3 Protocol Specification

###### 7.3.1 Data Format

```json
[
  {
    "name": "Temperature",
    "value": 65.34,
    "timestamp": "14:23:45",
    "status": "OK"
  },
  {
    "name": "Pressure",
    "value": 82.17,
    "timestamp": "14:23:45",
    "status": "HIGH ALARM"
  }
]
```

###### 7.3.2 Frame Delimiter

**TCP**: Newline-terminated JSON (`\n`)  
**WebSocket**: Message boundaries built into protocol

###### 7.3.3 Status Values

| Value | Meaning | Trigger Condition |
|-------|---------|-------------------|
| `"OK"` | Normal operation | `low ≤ value ≤ high` |
| `"LOW ALARM"` | Below threshold | `value < low` |
| `"HIGH ALARM"` | Above threshold | `value > high` |

##### 7.4 Error Handling & Recovery

###### 7.4.1 Connection Failures

```python
try:
    self.client.connect((host, port))
except ConnectionRefusedError:
    self.log_message.emit("Simulator not running")
except Exception as e:
    self.log_message.emit(f"Error: {e}")
```

###### 7.4.2 Data Corruption

```python
try:
    sensor_list = json.loads(line)
    self.data_received.emit(sensor_list)
except json.JSONDecodeError:
    self.log_message.emit("Malformed data received")
    continue  # Skip this packet
```

###### 7.4.3 Automatic Reconnection

**Current**: Manual reconnection (user clicks "Connect")  

---

#### 8. GUI Design & User Experience

##### 8.1 UI Architecture

######


##### 8.2 Responsive Design 
![Monitoring UI](imgs/monitoring_ui.png)



##### 8.3 Visual Feedback Systems

##### 8.4 User Interaction Flow
