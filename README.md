# Real-Time Production Line Sensor Dashboard

A desktop-based real-time monitoring dashboard built with PyQt6 that visualizes industrial sensor data streamed over TCP. The system supports live monitoring, alarm detection, offline replay, and session export with a modern, production-grade UI.

## 📁 Project Structure

```
Real-Time-Production-Line-Sensor-Dashboard/
│
├── app.py                 # Main PyQt6 dashboard application
├── sensor_worker.py       # Worker threads (Live TCP + Offline Replay)
├── simulator.py           # TCP / WebSocket sensor data simulator
├── sensors_config.json    # Sensor definitions and connection config
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── icon.png               # Application icon
├── logo.png               # Splash screen logo
└── venv/                  # (Optional) Virtual environment
```

## ⚙️ Setup Steps

### 1. Prerequisites

- Python 3.9+
- Windows / Linux / macOS
- Internet connection not required (local TCP simulation)

### 2. Create & Activate Virtual Environment (Recommended)

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
pip install -r requirements.txt
```

**Main libraries used:**
- PyQt6
- pyqtgraph
- plyer
- websockets (optional – WebSocket simulator)

## ▶️ Running Instructions

### Step 1: Start the Sensor Simulator

The simulator acts as an industrial data source and must be running before the dashboard connects.

```bash
python simulator.py
```

**Expected output:**
```
Industrial TCP Simulator Online at 127.0.0.1:5555...
```

### Step 2: Launch the Dashboard Application

Open a new terminal and run:

```bash
python app.py
```

**You will see:**
- Splash screen
- Monitoring Dashboard
- Sensors in DISCONNECTED state

### Step 3: Connect to Live Data

1. Click **Connect System**
2. Status changes to **SYSTEM CONNECTED**
3. Sensors update in real time
4. Graphs display rolling 20-second windows

### Step 4: Maintenance Console Access

1. Open the **Maintenance Console** tab
2. Enter the admin token: `admin123`

**Available features:**
- Restart simulator
- Clear alarm history
- Export session data
- Load offline logs
- Enable desktop notifications

## 📡 Communication Protocol Description

### 🔌 Transport Layer

- **Protocol:** TCP Socket
- **Host:** 127.0.0.1
- **Port:** 5555
- **Update Rate:** Configurable (default: 0.5s)

### 📦 Data Format (TCP Payload)

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

### 🧾 Sensor Object Fields

| Field     | Type   | Description               |
|-----------|--------|---------------------------|
| name      | string | Sensor identifier         |
| value     | float  | Current sensor reading    |
| timestamp | string | Time in HH:MM:SS          |
| status    | string | OK, LOW ALARM, HIGH ALARM |

### ⚠️ Alarm Logic

- `value < low` → **LOW ALARM**
- `value > high` → **HIGH ALARM**

**Alarm triggers:**
- Red UI highlight
- Alarm log entry
- Optional desktop notification

## 🗂 Sensor Configuration (sensors_config.json)

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
    "Optical":     {"low": 20.0, "high": 40.0, "variation": 8.0}
  }
}
```

## 💾 Offline Replay & Export

### Export Current Session

- Saves all received packets to JSON
- Timestamped archive
- Accessible from Maintenance Console

### Offline Replay

- Load exported JSON
- Replay data using the same UI pipeline
- System switches to **REPLAY MODE**

## 🛠 Optional WebSocket Support

The simulator includes a WebSocket server:
```
ws://localhost:8080
```

**To enable it:**
1. Uncomment WebSocket section in `simulator.py`
2. Implement WebSocket worker in `sensor_worker.py`

## ✅ Key Features Summary

- ✓ Real-time sensor monitoring
- ✓ Industrial TCP simulation
- ✓ Alarm detection & logging
- ✓ Sliding-window analytics
- ✓ Offline replay
- ✓ Session export
- ✓ Admin-protected maintenance console
- ✓ Modern dark UI (production-grade)
