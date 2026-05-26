# DustMonitor_ExpoVersion

A comprehensive real-time dust concentration monitoring system that interfaces with IoT hardware devices through serial communication. The application provides a web-based dashboard for device control, configuration, and historical data visualization.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Installation & Setup](#installation--setup)
6. [Configuration](#configuration)
7. [Core Components](#core-components)
8. [API Endpoints](#api-endpoints)
9. [Frontend Architecture](#frontend-architecture)
10. [Device Communication Protocol](#device-communication-protocol)
11. [Database Schema](#database-schema)
12. [Running the Application](#running-the-application)
13. [Troubleshooting](#troubleshooting)

---

## Project Overview

**DustMonitor_ExpoVersion** is an IoT dust monitoring solution that:

- **Connects to hardware devices** via serial/USB communication to read dust concentration, temperature, and other sensor data
- **Provides a real-time web dashboard** for viewing live sensor readings
- **Allows device configuration** including alarm thresholds, calibration parameters, and network addresses
- **Stores historical data** in a database for trend analysis and reporting
- **Features WebSocket support** for continuous data streaming
- **Supports dark mode** for improved user experience
- **Implements database migrations** using Alembic for version control

### Key Use Cases

- Environmental monitoring in industrial facilities
- Air quality tracking in controlled environments
- Real-time dust concentration alerts
- Historical data analysis and trend reporting
- Device configuration and calibration management

---

## Architecture

### High-Level Flow

```
┌─────────────────────┐
│   Hardware Device   │ (Serial/USB)
│  (Dust Sensor)      │
└──────────┬──────────┘
           │ (Hex Protocol)
           ↓
┌─────────────────────────────────────────────┐
│         Browser (Web Client)                │
│  - Real-time Dashboard (HTML/CSS/JS)        │
│  - Device Connection & Control              │
│  - Data Visualization (Chart.js)            │
│  - Configuration UI                         │
└────────────┬────────────────────────────────┘
             │ (HTTP/WebSocket)
             ↓
┌─────────────────────────────────────────────┐
│      FastAPI Server (Python)                │
│  - Serial Communication Handler             │
│  - Hex Protocol Decoder/Encoder             │
│  - REST API Endpoints                       │
│  - WebSocket Server                         │
│  - Business Logic                           │
└────────────┬────────────────────────────────┘
             │ (SQLAlchemy ORM)
             ↓
┌─────────────────────────────────────────────┐
│    Database (PostgreSQL/SQLite)             │
│  - Device Readings Table                    │
│  - Historical Data Storage                  │
└─────────────────────────────────────────────┘
```

### Communication Flow

1. **Device → Server**: Hardware sends hex-encoded sensor data via serial port
2. **Server → Frontend**: Decoded data sent via HTTP/WebSocket
3. **Frontend → User**: Real-time visualization and status updates
4. **User → Server**: Configuration commands sent via REST API
5. **Server → Device**: Hex-encoded commands sent via serial port

---

## Technology Stack

### Backend
- **Framework**: FastAPI 0.100.0 (async web framework)
- **Server**: Uvicorn 0.22.0 (ASGI application server)
- **Database ORM**: SQLAlchemy (SQL database abstraction)
- **Database Migrations**: Alembic (schema version control)
- **Serial Communication**: PySerial 3.5 (hardware interface)
- **Data Validation**: Pydantic 1.10.12
- **Timezone**: Pytz (IST timezone for India)
- **Database**: PostgreSQL (primary) / SQLite (fallback)

### Frontend
- **Markup**: HTML5
- **Styling**: Tailwind CSS 4.1.18 (utility-first CSS framework)
- **Charting**: Chart.js (data visualization)
- **Scripting**: Vanilla JavaScript (no frameworks)
- **API Client**: Fetch API (HTTP requests)
- **Real-time**: WebSocket (bidirectional communication)

### Deployment
- **Container Ready**: Can be packaged as executable (PyInstaller)
- **Cross-Platform**: Windows, macOS, Linux support
- **Database**: Local AppData or project directory storage

---

## Project Structure

```
DustMonitor_ExpoVersion/
├── frontend/                          # Web interface
│   ├── index.html                    # Main dashboard
│   ├── home.html                     # Home page (alternative)
│   ├── admin.html                    # Configuration management page
│   ├── css/
│   │   ├── input.css                 # Tailwind input directives
│   │   └── output.css                # Compiled Tailwind CSS
│   └── js/
│       ├── api.js                    # Serial communication & API calls
│       ├── ui.js                     # UI updates & visualization
│       ├── websocket.js              # WebSocket client
│       └── vendor/
│           └── charts.min.js         # Chart.js library
│
├── alembic/                          # Database migrations
│   ├── versions/
│   │   └── a55c16e84ca6_init.py     # Initial migration schema
│   ├── env.py                        # Migration environment config
│   ├── script.py.mako                # Migration template
│   └── alembic.ini                   # Alembic configuration
│
├── app.py                            # FastAPI application entry point
├── database.py                       # Database connection & models
├── device_communicator.py            # Hardware protocol handler
├── config.json                       # Device configuration
├── requirements.txt                  # Python dependencies
├── package.json                      # Node.js dependencies (Tailwind)
├── tailwind.config.js                # Tailwind CSS configuration
├── README.md                         # This file
└── .gitignore                        # Git ignore rules
```

---

## Installation & Setup

### Prerequisites

- **Python**: 3.8+ (3.10+ recommended)
- **Node.js**: 16+ (for Tailwind CSS compilation)
- **Database**: PostgreSQL or SQLite
- **USB Port**: For serial device communication
- **OS**: Windows, macOS, or Linux

### Step 1: Clone Repository

```bash
git clone https://github.com/kishoreknot/DustMonitor_ExpoVersion.git
cd DustMonitor_ExpoVersion
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Database

```bash
# Initialize database tables
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"

# Run Alembic migrations (if needed)
alembic upgrade head
```

### Step 5: Install Frontend Dependencies

```bash
npm install
```

### Step 6: Compile Tailwind CSS

```bash
npx tailwindcss -i ./frontend/css/input.css -o ./frontend/css/output.css --watch
```

### Step 7: Configure Application

Edit `config.json`:

```json
{
  "network_address": 16,
  "full_scale": 1000,
  "alarm_threshold": 800,
  "calibration": {
    "offset": 0,
    "scale": 1.0
  },
  "serial": {
    "baudrate": 9600,
    "parity": "N",
    "bytesize": 8
  }
}
```

### Step 8: Run Application

```bash
python app.py
```

The application will start at `http://127.0.0.1:8000`

---

## Configuration

### Environment Variables

The application can be configured via environment variables:

```bash
# Database URL (defaults to local SQLite)
export DATABASE_URL="postgresql://user:password@localhost/dustmonitor"

# Server configuration
export SERVER_HOST="127.0.0.1"
export SERVER_PORT=8000
```

### Database Configuration

**In `database.py`:**

- **Development**: SQLite database stored in `DustMonitorUM/dustmonitor.db`
- **Production**: PostgreSQL connection string from environment or hardcoded (line 11)
- **Auto-creation**: Database tables created automatically on first run

### Device Configuration

**In `config.json`:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `network_address` | 16 | Unique ID for device on serial network |
| `full_scale` | 1000 | Maximum dust concentration value |
| `alarm_threshold` | 800 | Dust level triggering alarm |
| `calibration.offset` | 0 | Calibration offset value |
| `calibration.scale` | 1.0 | Calibration scale factor |
| `serial.baudrate` | 9600 | Serial port baud rate |
| `serial.parity` | "N" | Parity bit (None) |
| `serial.bytesize` | 8 | Data bits per byte |

---

## Core Components

### 1. **app.py** - FastAPI Application Server

**Purpose**: Main application server and REST API endpoint handler

**Key Classes/Functions**:

- `SensorDataModel`: Pydantic model for sensor data validation
- `RawHexModel`: Validates raw hex command format
- `DataStoreModel`: Database storage schema
- `decode_info()`: POST endpoint for decoding device responses
- `store_reading()`: POST endpoint for saving sensor readings
- `get_reading_history()`: GET endpoint for historical data retrieval
- Lifespan context manager for app startup/shutdown

**Port**: 127.0.0.1:8000

**Static Files**: Served from `frontend/` directory

### 2. **database.py** - Database Layer

**Purpose**: Database connection, ORM models, and session management

**Key Components**:

```python
class DeviceReading(Base):
    __tablename__ = "readings"
    # Columns:
    id: int (Primary Key)
    timestamp: DateTime (UTC)
    network_address: int
    dust_concentration: float (mg/m³)
    pcb_temp: float (°C)
    current_loop: float (mA)
    laser_diode_signal: int (LD)
    photo_diode_signal: int (PD)
    alarm_threshold: int
    alarm_raised: bool
```

**Database Path Logic**:

- **Frozen Executable**: Uses `C:\Users\Username\AppData\Local\DustMonitorUM\dustmonitor.db`
- **Development**: Uses project directory `./DustMonitorUM/dustmonitor.db`
- **PostgreSQL**: Uses connection string from `DATABASE_URL` env var

**Functions**:

- `get_db_path()`: Determines SQLite database location
- `get_encoded_url()`: Encodes PostgreSQL connection string with proper password encoding
- `get_db()`: Dependency injection for database session

### 3. **device_communicator.py** - Hardware Protocol Handler

**Purpose**: Decodes hex protocol responses from the dust sensor device

**Key Functions**:

#### `decode_response(hexstr: str) -> dict`

Interprets raw hex data based on command ID:

**Command 0xC9** (Sensor Reading Data):

```
Bytes:  0      1      2-3         4      5-6    7-8    ...  25-28         33-34   -2     -1
        0xFA   LEN    NET_ADDR    0xC9   LD     PD     ...  DUST_CONC     LOOP    CKSUM  0xF5
Position: 0     1     2-3        4       5-6    7-8   ... 25-28           33-34  -2     -1
```

**Returns**:
```python
{
    "network_address": int,           # Device address
    "ld": int,                        # Laser diode signal
    "pd": int,                        # Photo diode signal
    "pcb_temperature": float,         # Calculated from raw ADC value
    "dust_concentration": float,      # IEEE 754 32-bit float
    "current_loop": float,            # Current in mA (value/100)
}
```

**Command 0x98** (Device Information):

Returns device configuration:
```python
{
    "network_address_info": int,
    "calibration_factor": float,
    "calibration_a": float,           # Coefficient correction
    "range": int,                     # Full scale range
    "calibration_b": float,           # Offset
    "smoothing_time_sec": float,
    "alarm_threshold": int,
    "TimeUserHours": int,             # Device uptime
}
```

**Command Acknowledgments**: 0x97, 0x8C, 0x9D, 0x9A, 0xCF, 0xD0, 0x9E, 0xA5, 0xD1, 0xD2, 0xD3

**Error Handling**:
- Validates start byte (0xFA) and end byte (0xF5)
- Verifies checksum: `sum(bytes[:-2]) % 256`
- Returns `{"error": "message"}` on failure

### 4. **frontend/js/api.js** - Serial Communication Bridge

**Purpose**: Browser-side serial port handling and API communication

**Key Functions**:

#### `connectDevice()`

Establishes serial port connection and device identification:

1. Requests user to select serial port via `navigator.serial.requestPort()`
2. Opens port with baudrate 9600, 8 data bits, 1 stop bit, no parity
3. Sends initialization command: `fa ff ff 98 00 00 90`
4. Decodes response and updates UI with device info
5. Stores device network address globally

**Hex Command Structure**:

```
[0xFA] [NetAddrH] [NetAddrL] [CmdID] [Data...] [Checksum]
  1B       1B         1B        1B      ...       1B
```

#### `writeAndRead(hexCmd)`

Sends hex command to device and reads response with timeout:

1. Converts hex string to bytes: `hexToBytes("fa 00 10 c9 ff 00")`
2. Writes to serial port
3. Waits 100ms for device to process
4. Reads response in loop until complete packet received
5. Validates packet length using second byte
6. Returns hex string of response

**Packet Validation**:
```javascript
// Packet structure: [0xFA] [LENGTH] [...data...] [...] [0xF5]
if (responseBuffer[0] === 0xFA) {
    expectedLength = responseBuffer[1];  // Second byte = total length
    if (responseBuffer.length >= expectedLength) {
        // Complete packet received
    }
}
```

#### `readData(period_in_seconds)`

Continuous sensor data reading with interval:

- If `period_in_seconds = 0`: Single read
- If `period_in_seconds > 0`: Continuous polling loop
- Constructs read command using device network address
- Calls `store_reading` API endpoint
- Updates UI with new data

#### `updateSystemSetting(type, inputId)`

Sends configuration commands to device:

| Type | Command ID | Purpose |
|------|-----------|---------|
| `smoothing-time` | 0x8C | Set smoothing filter time |
| `range` | 0x9D | Set measurement range |
| `alarm` | 0x9A | Set alarm threshold |
| `network-address` | 0x97 | Change device network address |
| `calibration-a` | 0xCF | Set coefficient correction |
| `calibration-b` | 0xD0 | Set offset correction |
| `correction-value` | 0x9E | Apply temporary correction |
| `cancel-correction-value` | 0xA5 | Reset correction |

**Float Encoding** (for calibration values):

```javascript
// Converts JS float to 2-byte integer (multiply by 1000)
// Example: 1.5 → 1500 → [0x05, 0xDC]
value = value * 1000;
cmdList.push((value >> 8) & 0xFF);  // High byte
cmdList.push(value & 0xFF);         // Low byte
```

### 5. **frontend/js/ui.js** - User Interface Updates

**Purpose**: DOM manipulation, real-time data display, and user feedback

**Key Functions**:

#### `updateReading(parsed)`

Updates sensor value displays on dashboard:

```javascript
// Updates HTML elements with parsed sensor data
document.querySelector("#dustConcentrationValue").textContent = 
    parsed.dust_concentration ?? "--";
document.querySelector("#pcbTempValue").textContent = 
    parsed.pcb_temperature ?? "--";
// ... more updates
```

#### `initChart()`

Initializes Chart.js for real-time dust concentration graph:

```javascript
dustChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],  // Timestamps
        datasets: [{
            label: 'Dust Concentration (mg/m³)',
            data: [],
            borderColor: '#3b82f6',      // Blue when normal
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            fill: true,
            tension: 0.4,
            pointRadius: 2
        }]
    }
});
```

#### `addChartData(value)`

Adds single data point to chart (keeps last 20 points):

```javascript
dustChart.data.labels.push(formatted_timestamp);
dustChart.data.datasets[0].data.push(value);

if (dustChart.data.labels.length > 20) {
    dustChart.data.labels.shift();
    dustChart.data.datasets[0].data.shift();
}
dustChart.update('none');
```

#### `updateDustAlert()`

Changes card colors based on alarm threshold:

- **Normal** (concentration < threshold): Green gradient + normal colors
- **Alarm** (concentration > threshold): Red gradient + pulse animation

```javascript
const isAlarm = concentration > threshold;
card.classList.toggle('from-orange-500', isAlarm);
card.classList.toggle('from-emerald-400', !isAlarm);
```

#### `showToast(message, type)`

Displays notification messages with animations:

```javascript
// Toast slides in from right, stays for 1s, then fades out
// Type: 'success' (green) or 'error' (red)
```

### 6. **frontend/js/websocket.js** - Real-time Data Streaming

**Purpose**: WebSocket client for continuous sensor data streaming

**Functions**:

#### `startSensorStream(config, onData)`

Establishes WebSocket connection to server:

```javascript
socket = new WebSocket(`ws://${location.host}/ws/sensor`);

socket.onopen = () => {
    socket.send(JSON.stringify({
        continuous: true,
        period_in_seconds: 5,
        network_address: 16
    }));
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onData(data);  // Process received data
};
```

---

## API Endpoints

### REST Endpoints

#### `GET /`
- **Description**: Serve main dashboard HTML
- **Response**: HTML page

#### `GET /admin`
- **Description**: Serve configuration management page
- **Response**: HTML page

#### `GET /favicon.ico`
- **Description**: Serve application icon
- **Response**: PNG image

#### `POST /api/decode-info`
- **Description**: Decode raw hex response from device
- **Request Body**:
```json
{
    "raw_hex": "fa 12 00 10 98 ..."
}
```
- **Response**:
```json
{
    "parsed": {
        "network_address_info": 16,
        "alarm_threshold": 800,
        "calibration_a": 1.5,
        "range": 1000,
        ...
    }
}
```

#### `POST /api/store-reading`
- **Description**: Save sensor reading to database
- **Request Body**:
```json
{
    "raw_hex": "fa 12 00 10 c9 ...",
    "alarm_threshold": 800
}
```
- **Response**:
```json
{
    "parsed": {
        "dust_concentration": 450.25,
        "pcb_temperature": 28.5,
        "current_loop": 12.5,
        "ld": 2500,
        "pd": 3000
    }
}
```

#### `GET /api/get-reading-history`
- **Description**: Retrieve historical sensor readings
- **Query Parameters**:
  - `limit` (optional): Number of records to return (default: 100)
  - `offset` (optional): Pagination offset
- **Response**:
```json
{
    "history": [
        {
            "timestamp": "2026-05-26T10:30:45",
            "dust_concentration": 450.25,
            "pcb_temperature": 28.5,
            "network_address": 16
        },
        ...
    ]
}
```

### WebSocket Endpoint

#### `WS /ws/sensor`
- **Description**: Real-time sensor data streaming
- **Message Format** (Client → Server):
```json
{
    "continuous": true,
    "period_in_seconds": 5,
    "network_address": 16
}
```
- **Message Format** (Server → Client):
```json
{
    "timestamp": "2026-05-26T10:30:45",
    "dust_concentration": 450.25,
    "pcb_temperature": 28.5,
    "alarm_raised": false
}
```

---

## Frontend Architecture

### Page Structure

#### **index.html** - Main Dashboard

**Header Section**:
- Logo display
- Application title (DUSTMONITOR)
- Dark mode toggle button
- Control Center link to admin panel

**Device Readings Section**:
- Connect Device button (shows connection status)
- Stream Data toggle
- Polling interval selector (2-60 seconds)
- Read Sensor Data button
- Stop button

**Metrics Cards** (6 columns on desktop, 2 on mobile):
1. Network Address
2. Dust Concentration (mg/m³)
3. PCB Temperature (°C)
4. Current Loop (mA)
5. Laser Diode (LD) signal
6. Photo Diode (PD) signal

**Chart Section**:
- Real-time line chart of dust concentration over time
- Responsive height (300px)

#### **admin.html** - Configuration Management

**Device Configuration Section**:
- Smoothing Time input + Set button
- Range input + Set button
- Alarm Threshold input + Set button
- Network Address input + Set button

**Calibration Section**:
- Calibration A input + Set button
- Calibration B input + Set button
- Manual Zero Calibration button
- Cancel Zero Calibration button
- Range Calibration button

**Correction Section**:
- Tabbed interface (Coefficient vs. Direct Correction)
- Correction Value input
- Cancel Correction button

### Styling System

**Tailwind CSS v4.1.18**:
- Utility-first approach
- Built-in dark mode support
- Responsive grid system
- Pre-compiled to `frontend/css/output.css`

**Color Scheme**:
- **Primary**: Blue (#3b82f6)
- **Success**: Emerald/Green (#10b981)
- **Alert**: Orange/Red (#f97316 / #ef4444)
- **Neutral**: Slate (#64748b)

**Responsive Breakpoints**:
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

### JavaScript Module Structure

```
frontend/js/
├── api.js          - Serial + HTTP communication
├── ui.js           - DOM updates & visualization
├── websocket.js    - Real-time streaming
└── vendor/
    └── charts.min.js - Chart.js library
```

**Module Communication**:
```javascript
// api.js exports
export { connectDevice, readData, updateSystemSetting }

// ui.js exports
export { updateReading, showToast, initChart, addChartData }

// Global event handlers in HTML
onclick="connectDevice()"
onclick="updateSystemSetting('alarm', 'sys-alarm')"
```

---

## Device Communication Protocol

### Hex Command Format

All commands follow a 7-byte structure:

```
Byte 0    | Byte 1-2       | Byte 3   | Byte 4-5    | Byte 6
----------|----------------|----------|-------------|--------
0xFA      | Network Addr   | Command  | Data        | Checksum
(Start)   | (Big Endian)   | ID       | (Parameter) | (Sum % 256)
```

### Example Commands

**1. Device Identification (0x98)**
```
Command:  fa ff ff 98 00 00 90
Decoded:  [0xFA] [0xFFFF] [0x98] [0x0000] [0x90]
Purpose:  Request device information
```

**2. Read Sensor Data (0xC9)**
```
Command:  fa 00 10 c9 ff 00 [checksum]
Decoded:  [0xFA] [0x0010] [0xC9] [0xFF00] [checksum]
Purpose:  Read dust concentration (freq=0xFF)
Network:  Address 0x0010 (16 decimal)
```

**3. Set Alarm Threshold (0x9A)**
```
Command:  fa 00 10 9a 03 20 [checksum]
Decoded:  [0xFA] [0x0010] [0x9A] [0x0320] [checksum]
Purpose:  Set alarm to 800 mg/m³ (0x0320 = 800)
```

### Response Format

Device responses have variable length based on command:

```
Byte 0    | Byte 1       | Byte 2-...   | Byte -2      | Byte -1
----------|--------------|--------------|--------------|----------
0xFA      | Total Length | Payload      | Checksum     | 0xF5
(Start)   | (Bytes)      | (Data)       | (Sum % 256)  | (End)
```

### Example Response - Device Info (0x98)

```
Raw Response (61 bytes):
fa 3d 00 10 98 00 01 3a 40 00 00 3a 40 00 e8
00 41 95 00 00 41 98 80 00 00 00 00 00 00 00
80 00 00 00 00 00 00 00 00 00 00 41 c8 00 00
70 08 00 00 00 00 03 20 bb f5

Decoded Structure:
Byte 0:    0xFA (start)
Byte 1:    0x3D (61 bytes total)
Byte 2-3:  0x0010 (network address = 16)
Byte 4:    0x98 (command type)
Byte 5-8:  Calibration factor (IEEE 754 float) = 1.875
Byte 9-10: Range = 1000
Byte 11-14: Calibration B (IEEE 754 float) = 3.0
...
Byte 59-60: 0x0320 (alarm threshold = 800)
Byte 61-62: Checksum + End marker (0xF5)
```

### Checksum Calculation

```javascript
const checksum = bytes.slice(0, -2).reduce((sum, b) => sum + b, 0) % 0x100;
```

Validation:
```javascript
if (calculated_checksum !== received_checksum) {
    return { error: "Checksum failed" };
}
```

---

## Database Schema

### DeviceReading Table

**Purpose**: Store time-series sensor data for historical analysis

**Columns**:

| Column Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTOINCREMENT | Unique record identifier |
| timestamp | DateTime (UTC) | NOT NULL, Server Default | When reading was recorded |
| network_address | Integer | NOT NULL | Device address (1-65535) |
| dust_concentration | Float | NOT NULL | Dust in mg/m³ |
| pcb_temp | Float | NOT NULL | PCB temperature in °C |
| current_loop | Float | NOT NULL | Current loop in mA |
| laser_diode_signal | Integer | NOT NULL | LD raw signal |
| photo_diode_signal | Integer | NOT NULL | PD raw signal |
| alarm_threshold | Integer | NOT NULL | Alarm level at time of reading |
| alarm_raised | Boolean | DEFAULT FALSE | Whether alarm condition existed |

**Indexes**:
- Primary: `id`
- Foreign: `network_address`
- Time-series: `timestamp` (for range queries)

**Sample Query**:

```sql
-- Get last 100 readings for device
SELECT * FROM readings 
WHERE network_address = 16 
ORDER BY timestamp DESC 
LIMIT 100;

-- Get readings above threshold
SELECT * FROM readings 
WHERE dust_concentration > alarm_threshold 
AND timestamp > NOW() - INTERVAL '24 hours';

-- Average dust concentration per hour
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    AVG(dust_concentration) as avg_dust,
    MAX(dust_concentration) as max_dust
FROM readings
WHERE network_address = 16
GROUP BY DATE_TRUNC('hour', timestamp)
ORDER BY hour DESC;
```

### Migration Strategy

**Location**: `alembic/versions/`

**File**: `a55c16e84ca6_init.py`

Currently contains placeholder for initial schema creation.

**To Add New Migrations**:

```bash
# Generate migration
alembic revision --autogenerate -m "Add new column"

# Edit the generated file to add operations

# Apply migration
alembic upgrade head
```

---

## Running the Application

### Development Mode

```bash
# Terminal 1: Watch Tailwind CSS
npx tailwindcss -i ./frontend/css/input.css -o ./frontend/css/output.css --watch

# Terminal 2: Start FastAPI server
python app.py
```

Navigate to `http://127.0.0.1:8000`

### Production Mode

```bash
# Compile Tailwind CSS once
npx tailwindcss -i ./frontend/css/input.css -o ./frontend/css/output.css

# Start Uvicorn with production settings
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment (Optional)

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Troubleshooting

### Issue: Serial Port Connection Fails

**Symptoms**: "No serial ports found" or device not detected

**Solutions**:

1. **Check Physical Connection**:
   - Verify USB cable is connected
   - Try different USB port
   - Check device is powered on

2. **Check Driver Installation**:
   ```bash
   # Windows: Device Manager
   # macOS: System Information → USB
   # Linux: lsusb
   ```

3. **Check Permissions** (Linux):
   ```bash
   sudo usermod -a -G dialout $USER
   # Then log out and log back in
   ```

4. **Check Baudrate**:
   - Default: 9600 baud
   - Verify device supports same rate in `config.json`

5. **Debug Serial Port**:
   ```bash
   python -c "import serial; print(serial.tools.list_ports.comports())"
   ```

### Issue: Checksum Mismatch

**Symptoms**: "Checksum failed" in console, decoding fails

**Solutions**:

1. **Verify Data Integrity**:
   - Check serial cable for damage
   - Reduce baud rate to 9600
   - Add delay between commands

2. **Check Device Response**:
   - Enable debug logging in `device_communicator.py`
   - Print raw bytes: `print(resp.hex())`
   - Verify start byte (0xFA) and end byte (0xF5)

### Issue: Database Connection Error

**Symptoms**: "Connection refused" or "Database locked"

**Solutions**:

1. **SQLite Issues**:
   ```bash
   # Check file permissions
   ls -la ~/AppData/Local/DustMonitorUM/

   # Delete and recreate
   rm ~/AppData/Local/DustMonitorUM/dustmonitor.db
   python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
   ```

2. **PostgreSQL Issues**:
   ```bash
   # Check connection string
   echo $DATABASE_URL

   # Test connection
   psql "postgresql://user:pass@localhost/dustmonitor"

   # Verify PostgreSQL is running
   # Windows: Services panel
   # macOS: brew services list
   # Linux: systemctl status postgresql
   ```

### Issue: Tailwind CSS Not Applied

**Symptoms**: Styling looks broken, basic layout only

**Solutions**:

1. **Recompile CSS**:
   ```bash
   npx tailwindcss -i ./frontend/css/input.css -o ./frontend/css/output.css
   ```

2. **Clear Browser Cache**:
   - Ctrl+Shift+Delete → Clear browsing data
   - Close and reopen browser

3. **Check Config Path**:
   ```javascript
   // Verify in HTML
   <link href="/static/css/output.css" rel="stylesheet">
   ```

### Issue: Real-time Chart Not Updating

**Symptoms**: Chart.js renders but no data points appear

**Solutions**:

1. **Check WebSocket Connection**:
   - Open browser DevTools → Network → WS
   - Verify connection to `/ws/sensor`

2. **Verify Data Flow**:
   ```javascript
   // In browser console
   console.log(window.dustChart);  // Should not be null
   console.log(window.dustChart.data.labels);  // Should have timestamps
   ```

3. **Check Memory Limit**:
   - Chart keeps 20 points max to prevent lag
   - If chart freezes, reduce update frequency

### Issue: Device Commands Not Executing

**Symptoms**: "Set" button unresponsive, no acknowledgment

**Solutions**:

1. **Verify Device Connected**:
   - Check connection status dot is green
   - Try "Read Sensor Data" first

2. **Check Command Format**:
   ```javascript
   // In api.js, verify generateHexCommand output
   console.log("generateHexCommand hexCmd", hexCmd);
   ```

3. **Validate Checksum**:
   ```python
   # In device_communicator.py
   calculated = sum(bytes[:-2]) % 0x100
   print(f"Calculated: {hex(calculated)}, Received: {hex(bytes[-2])}")
   ```

4. **Reset Device**:
   - Power cycle device
   - Reconnect in browser

### Issue: High CPU Usage

**Symptoms**: Server process consuming excessive CPU

**Solutions**:

1. **Reduce Update Frequency**:
   - Change polling interval from 2s to 5s+
   - Disable continuous streaming when not needed

2. **Optimize Database Queries**:
   - Add indexes to frequently queried columns
   - Use pagination for historical data

3. **Profile Application**:
   ```bash
   pip install py-spy
   py-spy record -o profile.svg -- python app.py
   ```

---

## Development Workflow

### Adding New API Endpoint

1. **Define Pydantic Model** in `app.py`:
```python
class NewCommandModel(BaseModel):
    value: int = Field(..., description="Command value")
    network_address: int = Field(..., description="Device address")
```

2. **Create Endpoint**:
```python
@app.post("/api/new-command")
async def new_command(data: NewCommandModel, db: Session = Depends(get_db)):
    # Implementation
    return {"status": "success"}
```

3. **Add Frontend Handler** in `api.js`:
```javascript
export async function executeNewCommand(value) {
    const response = await fetch(`${API_BASE}/api/new-command`, {
        method: "POST",
        body: JSON.stringify({ value, network_address })
    });
    return await response.json();
}
```

### Adding New Device Command

1. **Define Command ID** in protocol documentation
2. **Add Hex Encoder** in `api.js`:
```javascript
case 'new-command':
    hexCmd = generateHexCommand(currentNetAddr, 0xXX, value);
    break;
```

3. **Add Decoder** in `device_communicator.py`:
```python
elif cmdId == 0xXX:
    decoded_resp["new_field"] = parse_value(b[5:9])
```

### Creating Database Migration

```bash
# 1. Modify DeviceReading model in database.py
# 2. Generate migration
alembic revision --autogenerate -m "Add new_column"

# 3. Review generated file
# 4. Apply migration
alembic upgrade head
```

---

## Performance Optimization

### Frontend

- **Lazy Load Charts**: Initialize Chart.js only when needed
- **Debounce Updates**: Limit UI updates to 100ms intervals
- **CSS Optimization**: Tailwind output.css is pre-compiled (~200KB)

### Backend

- **Connection Pooling**: SQLAlchemy manages database connections
- **Async Handlers**: FastAPI processes requests concurrently
- **Data Compression**: JSON responses are auto-compressed by Uvicorn

### Database

- **Retention Policy**: Consider archiving old readings (> 90 days)
- **Batch Inserts**: Group multiple readings in single transaction
- **Query Optimization**: Use indexes on timestamp and network_address

---

## Security Considerations

### Current Implementation

- **No Authentication**: Public access by default
- **No HTTPS**: HTTP only in development
- **No Input Validation**: Limited server-side validation

### Production Recommendations

1. **Enable HTTPS**:
   ```python
   uvicorn app:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem
   ```

2. **Add Authentication**:
   ```python
   from fastapi.security import HTTPBearer
   security = HTTPBearer()
   
   @app.get("/api/protected")
   async def protected(credentials: HTTPAuthCredentials = Depends(security)):
       # Validate token
       pass
   ```

3. **Input Sanitization**:
   - Validate all hex strings format
   - Range check numeric inputs
   - Whitelist allowed command IDs

4. **Rate Limiting**:
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   
   @app.post("/api/command")
   @limiter.limit("10/minute")
   async def limited_command(...):
       pass
   ```

---

## License

This project is part of GreenEnv monitoring systems.

---

## Support & Contact

For issues, feature requests, or contributions:
- **GitHub Issues**: https://github.com/kishoreknot/DustMonitor_ExpoVersion/issues
- **Repository**: https://github.com/kishoreknot/DustMonitor_ExpoVersion

---

## Changelog

### Version 1.0.0
- Initial release with serial device communication
- Web-based real-time dashboard
- Device configuration management
- Historical data storage and retrieval
- Dark mode support
- Responsive design

---

**Last Updated**: 2026-05-26
**Maintainer**: @kishoreknot
