#### Real-Time Production Line Sensor Dashboard

A desktop-based real-time monitoring dashboard built with PyQt6 that visualizes industrial sensor data streamed over TCP. The system supports live monitoring, alarm detection, offline replay, and session export with a modern, production-grade UI.

##### Project Structure

```
Real-Time-Production-Line-Sensor-Dashboard/
│
├── app.py                 # Main PyQt6 dashboard application
├── sensor_worker.py       # Worker threads (Live TCP + Offline Replay)
├── simulator.py           # TCP / WebSocket sensor data simulator
├── test_logic.py          # Basic unit tests
├── sensors_config.json    # Sensor definitions and connection config
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── icon.png               # Application icon
├── logo.png               # Splash screen logo
└── venv/                  # (Optional) Virtual environment
```

###### Prerequisites

- Python 3.9+
- Windows / Linux / macOS
- Internet connection not required in case of local TCP simulation

##### Setup Steps

##### 1. Clone Repository
```bash
git clone https://github.com/yourusername/sensor-dashboard.git
```
##### 2. Create & Activate Virtual Environment (Recommended)

```bash
python -m venv venv
```

**Windows**
```bash
venv\Scripts\activate
```

**Linux / macOS**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

**Main libraries used:**
- PyQt6
- pyqtgraph
- plyer
- websockets (optional – WebSocket simulator)

##### Running Instructions

###### Step 1: Start the Sensor Simulator

The simulator acts as an industrial data source and must be running before the dashboard connects.

```bash
python simulator.py
```

**Expected output:**
```
Industrial TCP Simulator Online at 127.0.0.1:5555...
```
for websocket online streaming:
**Expected output:**
```
Industrial WebSocket Simulator Online at ws://localhost:8080...
```

###### Step 2: Launch the Dashboard Application

Open a new terminal and run:

```bash
python app.py
```

**You will see:**
- Splash screen
- Monitoring Dashboard
- Sensors in DISCONNECTED state

###### Step 3: Connect to Live Data

1. Click **Connect System**
2. Status changes to **SYSTEM CONNECTED**
3. Sensors update in real time
4. Graphs display rolling 20-second windows

###### Step 4: Maintenance Console Access

1. Open the **Maintenance Console** tab
2. Enter the admin token: `admin123`

**Available features:**
- Restart simulator
- Clear alarm history
- Export session data
- Load offline logs
- Enable desktop notifications

####  Communication Protocol Description

###### Transport Layer

- **Protocol:** TCP Socket
- **Host:** 127.0.0.1
- **Port:** 5555
- **Update Rate:** Configurable (default: 0.5s)

###### Data Format (TCP Payload)

Each TCP message is:
- JSON-encoded
- Newline (`\n`) terminated
- Contains a list of sensor objects

**Example Payload:**
```json
[
  {
    "name": "Temperature",
    "value": 72.5,
    "timestamp": "14:22:05",
    "status": "HIGH ALARM"
  },
  {
    "name": "Pressure",
    "value": 78.1,
    "timestamp": "14:22:05",
    "status": "OK"
  }
]
```

###### Sensor Object Fields

| Field     | Type   | Description               |
|-----------|--------|---------------------------|
| name      | string | Sensor identifier         |
| value     | float  | Current sensor reading    |
| timestamp | string | Time in HH:MM:SS          |
| status    | string | OK, LOW ALARM, HIGH ALARM |

###### Alarm Logic

- `value < low` → **LOW ALARM**
- `value > high` → **HIGH ALARM**

**Alarm triggers:**
- Red UI highlight
- Alarm log entry
- Optional desktop notification

##### Sensor Configuration (sensors_config.json)

 - The configuration schema is scalable where the user is able to add/edit any data entry and the UI will update accordingly

```json
{
    "connection": {
        "host": "127.0.0.1",
        "tcp_port": 5555,
        "ws_port": 8080,
        "update_interval": 0.5   
    },

    "sensors": {
        "Temperature": {"low": 50.0, "high": 70.0, "variation": 8.0},
        "Pressure":    {"low": 65.0, "high": 85.0, "variation": 8.0},
        "Vibration":   {"low": 20.0, "high": 35.0, "variation": 8.0},
        "Speed":       {"low": 40.0, "high": 60.0, "variation": 8.0},
        "Optical":     {"low": 20.0, "high": 40.0, "variation": 8.0},
        "Humidity":    {"low": 30.0, "high": 50.0, "variation": 8.0}
    }
}

```

#### Offline Replay & Export

##### Export Current Session

- Saves all received packets to JSON
- Timestamped archive
- Accessible from Maintenance Console

##### Offline Replay

- Load exported JSON
- Replay data using the same UI pipeline
- System switches to **REPLAY MODE**

#### Optional WebSocket Support

The simulator includes a WebSocket server:
```
ws://localhost:8080
```

**To enable it:**
1. Uncomment WebSocket section in `simulator.py` entry point.
```python
if __name__ == "__main__":
    # You can choose which one to run by uncommenting:
    
    # OPTION A: Run TCP (Default for the current dashboard)
    try:
        run_tcp_simulator()
    except KeyboardInterrupt:
        print("\nTCP Simulator shut down.")

    # OPTION B: Run WebSocket (NOTE ---> update your dashboard worker WebSocketWorker accordingly)
    # try:
    #     asyncio.run(run_websocket_simulator())
    # except KeyboardInterrupt:
    #     print("\nWS Simulator shut down.")
```
2. Uncomment websocketworker instance in `app.py` `handle_connection()` method.
```python
self.worker = SensorWorker()       # TCP sensor Socket Worker initiation if connect system clicked
# self.worker = WebSocketWorker()  # WebSocket Worker initiation if connect system clicked
```



###### Verification

```bash
# Test simulator
python -m unittest .\tests\simulator_test.py

# Test sensor worker
python -m unittest .\tests\worker_test.py

```
#### Key Features Summary

- Real-time sensor monitoring
- Industrial TCP simulation
- Alarm detection & logging
- Sliding-window analytics
- Offline replay
- Session export
- Admin-protected maintenance console

#### API Documentation 

##### Class Overview

##### `Dashboard(QMainWindow)`

The main application class that provides a real-time monitoring interface for industrial sensor data.

**Inherits**: `QMainWindow` (PyQt6)

**Purpose**: Manages the complete dashboard UI, handles sensor data visualization, monitoring, and maintenance operations.

---

##### Dashboard Class

###### Constructor

```python
def __init__(self)
```

**Description**: Initializes the dashboard application with all necessary components.

**Initializes**:
- Window properties (title, size, icon)
- Session timing and authentication
- Sensor configuration from `sensors_config.json`
- Data storage structures for plotting
- Event filtering for user activity monitoring "session timeouts for maintenance console access"

**Instance Variables**:
| Variable | Type | Description |
|----------|------|-------------|
| `start_time` | float | Application start timestamp |
| `maintenance_unlocked` | bool | Maintenance console access state |
| `timeout_seconds` | int | Session timeout duration (600s) |
| `sensor_config` | dict | Sensor definitions from sensors_config file |
| `plot_data` | dict | Historical sensor values for graphs |
| `plot_times` | dict | Timestamps for plot data points |
| `name_to_row` | dict | Maps sensor names to table rows |
| `session_timer` | QTimer | Auto-lock timer for maintenance |
| `active_alarms` | set | Currently active alarm sensors |
| `session_archive` | list | Buffer for session export |

---

#### Public Methods

##### UI Initialization

##### `init_ui()`
```python
def init_ui(self) -> None
```

**Description**: Constructs the main user interface with tabs and styling.

**Creates**:
- Tab widget with Monitoring and Maintenance views
- Global status indicator in status bar
- Application-wide stylesheet

---

##### `setup_monitoring_ui()`
```python
def setup_monitoring_ui(self) -> None
```

**Description**: Builds the main monitoring dashboard interface.

**Components Created**:
1. **Header Bar**
   - Connection status LED indicator
   - Connect/Disconnect toggle button to connect and disconnect from simulator 

2. **Live Sensors Table** 
   - 4 columns: Sensor, Reading, Time, Status
   - Auto-stretch columns
   - Read-only cells

3. **Alarm Logs Table** 
   - 4 columns: Time, Sensor, Val, Type
   - Chronological alarm history

4. **Real-Time Analytics Visualizer**
   - 5+ dynamic line graphs (one per sensor)
   - 20-second sliding window


---

##### `setup_maintenance_ui()`
```python
def setup_maintenance_ui(self) -> None
```

**Description**: Constructs the maintenance console interface.


**Left Sidebar Components**:
1. **System Control Group**
   - Restart Simulator button
   - Clear Alarm History button

2. **Preferences Group**
   - Desktop Alerts checkbox

3. **Data Archive Group**
   - Open Offline Log button
   - Export Current Session button

**Right Panel**:
- Live System Logs (text console)
- Clear Logs button

---

##### Connection Management

##### `handle_connection()`
```python
def handle_connection(self) -> None
```

**Description**: Manages live sensor connection lifecycle.

**Behavior**:
- **If Connect Clicked**:
  - Creates new `SensorWorker` thread
  - Connects signals to dashboard slots
  - Updates UI to "CONNECTED" state (green)
  - Starts worker secondary thread

- **If Disconnect Clicked**:
  - Stops active worker thread
  - Updates UI to "DISCONNECTED" state (red)
  - Releases resources

**Thread Safety**: Uses `worker.wait()` to ensure clean thread termination.

---

#### Data Processing

##### `update_dashboard(sensor_list)`
```python
def update_dashboard(self, sensor_list: List[Dict]) -> None
```

**Description**: Core update loop that processes incoming sensor data.

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `sensor_list` | List[Dict] | Array of sensor objects from TCP stream |

**Processing Steps**:
1. Archives data for export (if live mode)
2. Updates live sensor table with new readings
3. Applies alarm logic
4. Triggers desktop notifications for new alarms (if notifications preference enabled)
5. Updates individual graphs with sliding window

**Alarm Detection**:
```python
if "ALARM" in status:
    # Add to alarm history
    # Trigger notification if new
else:
    # Remove from active alarms
```

**Graph Update**:
- Appends new data point
- Removes points older than 20 seconds (to keep 20-second rolling)

---

##### `add_to_alarm_history(ts, name, val, status)`
```python
def add_to_alarm_history(self, ts: str, name: str, val: float, status: str) -> None
```

**Description**: Logs an alarm event to the alarm history table.

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `ts` | str | Timestamp in HH:MM:SS format |
| `name` | str | Sensor identifier |
| `val` | float | Sensor reading at alarm time |
| `status` | str | Alarm type (LOW ALARM/HIGH ALARM) |

**Behavior**: Inserts new row at top of alarm table.

---

#### Maintenance Operations

##### `clear_system_alarms()`
```python
def clear_system_alarms(self) -> None
```

**Description**: Clears all entries from the alarm history table.

**Use Case**: Manual cleanup after resolving issues.

**Logs**: "USER ACTION: Alarm history cleared."

---

##### `restart_simulation()`
```python
def restart_simulation(self) -> None
```

**Description**: Performs complete system reset.

**Reset Operations**:
1. Stops active worker thread
2. Clears all plot data buffers
3. Resets live sensor table (values + backgrounds)
4. Clears all graphs
5. Clears alarm history and active alarms set
6. Resets notification preference
7. Resets global status indicator
8. Clears session archive
9. Locks maintenance tab
9. Re-establishes connection if was connected

**Thread Safety**: Uses `worker.wait()` before reinitializing.

---

##### `load_offline_data()`
```python
def load_offline_data(self) -> None
```

**Description**: Loads and replays previously exported sensor data.

**Process**:
1. Stops live worker if running
2. Resets UI to clean statemask
3. Opens file dialog (JSON/CSV support)
4. Switches status to "REPLAY MODE" 
5. Creates `OfflineReplayWorker` instance
6. Connects signals and starts replay

**UI Changes**:
- Status text: "SYSTEM REPLAY MODE"
- Connect button: Unchecked back to default

---

##### `export_session_to_json()`
```python
def export_session_to_json(self) -> None
```

**Description**: Exports current session data to JSON file.

**Data Structure**:
```json
[
  {
    "timestamp_unix": 1735574525.123,
    "sensors": [
      {
        "name": "Temperature",
        "value": 72.5,
        "timestamp": "14:22:05",
        "status": "HIGH ALARM"
      }
    ]
  }
]
```

**Validation**: Checks if `session_archive` has data before proceeding.

**Default Filename**: `Session_<unix_timestamp>.json`

---

#### Notification System

##### `trigger_desktop_alert(name, val, status)`
```python
def trigger_desktop_alert(self, name: str, val: float, status: str) -> None
```

**Description**: Sends desktop notification for new alarms.

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | str | Sensor name triggering alarm |
| `val` | float | Current sensor value |
| `status` | str | Alarm type |

**Requirements**:
- User must enable "Desktop Alerts" in preferences
- Sensor must not be in `active_alarms` set (prevents spam)

**Notification Format**:
- **Title**: `⚠️ {status}`
- **Message**: `{name} is at {val:.2f}`
- **Timeout**: 2 seconds

**Library**: Uses `plyer.notification`

---

#### Authentication & Security

##### `check_tab_access(index)`
```python
def check_tab_access(self, index: int) -> None
```

**Description**: Guards maintenance console access with password.

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `index` | int | Tab index being switched to |

**Authentication Flow**:
1. User clicks "Maintenance Console" tab
2. If not unlocked, blocks navigation
3. Shows password dialog 
4. Validates token: `"admin123"`
5. On success:
   - Sets `maintenance_unlocked = True`
   - Starts session timer (10 minutes)
   - Allows tab access

**Security**: Password input uses `QLineEdit.EchoMode.Password`

---

##### `lock_maintenance_session()`
```python
def lock_maintenance_session(self) -> None
```

**Description**: Auto-locks maintenance after inactivity timeout.

**Trigger**: QTimer expires after 600 seconds of no user activity.

**Behavior**:
- Resets `maintenance_unlocked` to False
- Forces navigation back to Monitoring tab

---

##### `eventFilter(obj, event)`
```python
def eventFilter(self, obj: QObject, event: QEvent) -> bool
```

**Description**: Global event monitor for user activity detection.

**Monitored Events**:
- `MouseMove`
- `MouseButtonPress`
- `KeyPress`

**Behavior**: Any activity restarts the 10-minute session timer.

**Installation**: Called in `__init__` with `QApplication.instance().installEventFilter(self)`

---

#### Status Management

##### `global_status_update(operational)`
```python
def global_status_update(self, operational: bool) -> None
```

**Description**: Updates the global system status indicator in status bar.

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `operational` | bool | True = healthy, False = ANY alarm active |

**Visual States**:
| State | Circle Color | Text |
|-------|--------------|------|
| Healthy | Green| "GLOBAL STATUS INDICATOR" |
| Alarm | Red | "GLOBAL STATUS INDICATOR" |
| Offline | Grey | "SYSTEM OFFLINE" |

---

##### `update_log(msg)`
```python
def update_log(self, msg: str) -> None
```

**Description**: Appends timestamped message to maintenance console log.

**Format**: `<b>HH:MM:SS</b> > {msg}`

**Use Cases**:
- System events
- User actions
- Worker thread notifications
- Error messages

---

#### Signal/Slot Connections

##### Worker Thread Signals

```python
# SensorWorker signals
worker.data_received.connect(self.update_dashboard)
worker.log_message.connect(self.update_log)

# OfflineReplayWorker signals (same interface)
worker.data_received.connect(self.update_dashboard)
worker.log_message.connect(self.update_log)
```

##### UI Component Signals

```python
# Connection button
btn_toggle.clicked.connect(self.handle_connection)

# Maintenance buttons
btn_restart.clicked.connect(self.restart_simulation)
btn_clear_alarms.clicked.connect(self.clear_system_alarms)
btn_clear_logs.clicked.connect(lambda: self.log_display.clear())

# Data management
btn_load_offline.clicked.connect(self.load_offline_data)
btn_export_data.clicked.connect(self.export_session_to_json)

# Tab navigation
tabs.currentChanged.connect(self.check_tab_access)

# Session timeout
session_timer.timeout.connect(self.lock_maintenance_session)
```

---

#### Data Structures

##### Sensor Data Packet
```python
{
    "name": str,        # Sensor identifier
    "value": float,     # Current reading
    "timestamp": str,   # HH:MM:SS format
    "status": str       # "OK" | "FAULT"
}
```

##### Session Archive Entry
```python
{
    "timestamp_unix": float,           # Unix timestamp
    "sensors": List[SensorDataPacket]  # All sensors at this moment
}
```

##### Sensor Configuration
```python
{
    "connection": {
        "host": str,
        "tcp_port": int,
        "ws_port": int,
        "update_interval": float
    },
    "sensors": {
        "SensorName": {
            "low": float,      # Low threshold
            "high": float,     # High threshold
            "variation": float # Simulated noise range
        }
    }
}
```

##### Typical Workflow

1. **Startup**: Splash screen displays for 2.5s
2. **Monitor Tab**: Dashboard loads in disconnected state
3. **Connect**: User clicks "Connect System"
4. **Live Data**: Sensor values update every 0.5s
5. **Alarm Handling**: Red highlights + optional notifications
6. **Maintenance**: Admin authenticates to access controls
7. **Export**: Session data saved to JSON
8. **Replay**: Load and visualize historical data

---

#### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| PyQt6 | Latest | GUI framework |
| pyqtgraph | Latest | Real-time plotting |
| plyer | Latest | Desktop notifications |
| sensor_worker | Local | Threading for TCP/replay |
| websockets | Latest | websocket streaming|

---

#### Thread Safety Notes

- **Main Thread**: Handles all GUI updates
- **Worker Thread**: Manages TCP socket or file replay
- **Signals**: Used for thread-safe communication
- **Critical Sections**: Always call `worker.wait()` before reinitializing
