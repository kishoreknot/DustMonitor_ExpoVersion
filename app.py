import os, sys, threading, webview
from fastapi import (FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends)
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
#This was used for lifespan management. Need to uncomment if needed again
from contextlib import asynccontextmanager
import asyncio

#Deployment
import uvicorn

from fastapi.staticfiles import StaticFiles


from device_communicator import (send_and_receive, 
                                 decode_response, 
                                 load_config, 
                                 get_serial_connection, 
                                 serial_connection,
                                 device_status)

#Database imports
from database import DeviceReading, get_db, Base, engine
from sqlalchemy.orm import Session
from sqlalchemy import desc

class SensorDataModel(BaseModel):
    period_in_seconds: float = Field(..., ge=2, description="Period in seconds for data reading")
    network_address: int = Field(..., description="Network address of the device")

class NetworkAddressModel(BaseModel):
    address: int = Field(..., ge=0, le=65535, description="Network address to set for the device")

class SmoothingTimeModel(BaseModel):
    smoothtime_in_seconds: int = Field(..., ge=1, description="Smoothing time in seconds")
    network_address: int = Field(..., description="Network address of the device")

class RangeModel(BaseModel):
    max_range_value: int = Field(..., ge=1, description="Maximum Range value")
    network_address: int = Field(..., description="Network address of the device")

class AlarmModel(BaseModel):
    threshold_value: float = Field(..., description="Threshold value for the alarm")
    network_address: int = Field(..., description="Network address of the device")

class CalibrationAModel(BaseModel):
    calibration_value: float = Field(..., description="Calibration value A")
    network_address: int = Field(..., description="Network address of the device")
    calibration_type: str = Field(..., description="Type of calibration: A or B")
    
class CorrectValueModel(BaseModel):
    correction_value: int = Field(..., description="Correction value for calibration")
    network_address: int = Field(..., description="Network address of the device")

class deviceCalibrationModel(BaseModel):
    calibration_type: str = Field(..., description="Calibration type")
    network_address: int = Field(..., description="Network address of the device")
    
# BASE = os.path.dirname(__file__)
# This logic finds the 'base path' whether running as a script or a compiled .exe
if getattr(sys, 'frozen', False):
    # If compiled, the base path is the executable's folder
    BASE = os.path.dirname(sys.executable)
else:
    # If running as a script, the base path is the current file's folder
    BASE = os.path.dirname(os.path.abspath(__file__))

FRONTEND_DIR = os.path.join(BASE, "frontend")

#Used this to create the connection at startup, but now moving to button based connection
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     get_serial_connection()
#     yield
#     if serial_connection and serial_connection.is_open:
#         serial_connection.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up: Checking database connection...")
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: Clean up if necessary
    print("Shutting down...")

# app = FastAPI()

app = FastAPI(lifespan= lifespan)

from fastapi import Response




@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content="", media_type="image/x-icon")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
@app.get("/admin")
async def index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# @app.get("/admin")
# async def read_admin():
#     # This serves the file while keeping the URL clean
#     return FileResponse('frontend/admin.html')

def run_fastapi():
    uvicorn.run(app, host="127.0.0.1", port=8000)

connection = None

# Connect Device
@app.post("/api/connect-device" )
async def connect_device():
    global connection 
    connection = get_serial_connection()
    if connection:
        print("Connected.....")
        return {"status": "Connected", "port": device_status["port"]}
    else:
        print("Not connected....")
        return {"status": "NotConnected", "error": device_status["error"]}

@app.post("/api/close-serial-port")
async def close_serial_port():
    close_serial_port(connection)

# Read Sensor Data
@app.post("/api/read-data")
async def read_data(data: SensorDataModel, db: Session = Depends(get_db)):
    # print('data.period_in_seconds --> ', data.period_in_seconds)
    data_frequency = int(data.period_in_seconds * 10)
    network_address_high = (data.network_address >> 8) & 0xFF
    network_address_low = data.network_address & 0xFF

    # print('data_frequency (int) --> ', data_frequency)
    # print('hex data_frequency --> ', hex(data_frequency))


    cmd_list = [0xFA, network_address_high, network_address_low, 0xC9, data_frequency, 0x00]
    # print("Checksum", sum(cmd_list) % 0x100)
    checksum = (sum(cmd_list) % 0x100)
    # print("checksum--------->", checksum)
    cmd_list.append(checksum)
    cmd = ' '.join(f"{byte:02x}" for byte in cmd_list)

    print('*****************calling send_and_receive with cmd:', cmd)
    try:
        resp_hex = send_and_receive(cmd)
        parsed = decode_response(resp_hex)
        result_data = {"raw": resp_hex, "parsed": parsed}
        print(result_data)
        #Code to Store the Parse Json to DB
        if result_data.get("parsed"):
            parsed_info = result_data["parsed"]
            new_reading = DeviceReading(
                network_address = parsed_info.get("network_address"),
                dust_concentration = parsed_info.get("dust_concentration"),
                pcb_temp = parsed_info.get("dust_concentration"),
                current_loop = parsed_info.get("dust_concentration"),
                laser_diode_signal = parsed_info.get("ld"),
                photo_diode_signal = parsed_info.get("pd")
            )

            db.add(new_reading)
            db.commit()
            db.close()

        return result_data 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/get-reading-history")
async def get_reading_history(db: Session = Depends(get_db)):
    readings = db.query(DeviceReading)\
        .order_by(desc(DeviceReading.timestamp))\
        .limit(50)\
        .all()
    
    readings.reverse()

    return {
        "history": [
            {
                "timestamp": r.timestamp.strftime("%H:%M:%S"), # Format for chart labels
                "dust": r.dust_concentration,
                "temp": r.pcb_temp,
                "current": r.current_loop
            } for r in readings
        ]
    }



@app.websocket("/ws/sensor")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    continuous_task = None
    try:
        while True:
            # Receive configuration from frontend
            data = await websocket.receive_json()
            is_continuous = data.get("continuous", False)
            network_address = data.get("network_address", 0)
            period = data.get("period_in_seconds", 2)

            # Cancel any existing continuous task
            if continuous_task:
                continuous_task.cancel()
                continuous_task = None

            # Determine bytes 5 and 6 logic
            if is_continuous:
                # Assuming period * 10 for continuous mode as per your logic
                freq_byte = int(period * 10)
                # Ensure it stays within single byte range if that's device spec
                byte5, byte6 = freq_byte & 0xFF, 0x00
            else:
                # Value > 250 for bytes 5 and 6 signals single-shot
                byte5, byte6 = 0xFF, 0xFF 

            # Construct Command
            net_h, net_l = (network_address >> 8) & 0xFF, network_address & 0xFF
            cmd_list = [0xFA, net_h, net_l, 0xC9, byte5, byte6]
            cmd_list.append(sum(cmd_list) % 0x100)
            cmd = ' '.join(f"{byte:02x}" for byte in cmd_list)

            if is_continuous:
                # For continuous mode, create a task that keeps sending
                async def send_continuous_data():
                    try:
                        while True:
                            try:
                                resp_hex = send_and_receive(cmd)
                                parsed = decode_response(resp_hex)
                                await websocket.send_json({"raw": resp_hex, "parsed": parsed})
                            except Exception as e:
                                await websocket.send_json({"error": str(e)})
                            await asyncio.sleep(period)
                    except asyncio.CancelledError:
                        pass
                
                continuous_task = asyncio.create_task(send_continuous_data())
            else:
                # For single-shot, just send once
                try:
                    resp_hex = send_and_receive(cmd)
                    parsed = decode_response(resp_hex)
                    await websocket.send_json({"raw": resp_hex, "parsed": parsed})
                except Exception as e:
                    await websocket.send_json({"error": str(e)})
                # Close the websocket after single-shot response
                await websocket.close()
                break  # Exit the loop after closing
                    
    except WebSocketDisconnect:
        if continuous_task:
            continuous_task.cancel()
        print("Client disconnected")    

# Read System Info
@app.get("/api/read-system-info")
async def read_system_info():
    cmd = "fa ff ff 98 00 00 90"

    resp_hex = send_and_receive(cmd)
    parsed = decode_response(resp_hex)
    result_data = {"raw": resp_hex, "parsed": parsed}
    print(result_data)
    return result_data

# Set Network Address
@app.post("/api/set-network-address")
async def set_network_address(data: NetworkAddressModel):
    cmd_list = [0xFA, 0xFF, 0xFF, 0x97]
    byte_5 = (data.address >> 8) & 0xFF
    byte_6 = data.address & 0xFF
    cmd_list.append(byte_5)
    cmd_list.append(byte_6)
    checksum = (sum(cmd_list) % 0x100)
    cmd_list.append(checksum)
    cmd = ' '.join(f"{byte:02x}" for byte in cmd_list)

    try:
        print('*****************calling send_and_receive with cmd:', cmd)
        resp_hex = send_and_receive(cmd)
        parsed = decode_response(resp_hex)
        result_data = {"raw": resp_hex, "parsed": parsed}
        print(result_data)
        return result_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Set Smoothing Time
@app.post("/api/set-smoothing-time")
async def set_smoothing_time(data: SmoothingTimeModel):
    network_address_high = (data.network_address >> 8) & 0xFF
    network_address_low = data.network_address & 0xFF
    cmd_list = [0xFA, network_address_high, network_address_low, 0x8C]

    smoothing_time = data.smoothtime_in_seconds
    
    byte_5 = (smoothing_time >> 8) & 0xFF
    byte_6 = smoothing_time & 0xFF
    cmd_list.append(byte_5)
    cmd_list.append(byte_6)

    checksum = (sum(cmd_list) % 0x100)
    cmd_list.append(checksum)

    cmd = ' '.join(f"{byte:02x}" for byte in cmd_list)

    try:
        print('*****************calling send_and_receive with cmd:', cmd)
        resp_hex = send_and_receive(cmd)
        parsed = decode_response(resp_hex)
        result_data = {"raw": resp_hex, "parsed": parsed}
        print(result_data)
        return result_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Set Range
@app.post("/api/set-range")
async def set_range(data: RangeModel):
    network_address_high = (data.network_address >> 8) & 0xFF
    network_address_low = data.network_address & 0xFF
    cmd_list = [0xFA, network_address_high, network_address_low, 0x9D]

    range_value = data.max_range_value

    byte_5 = (range_value >> 8) & 0xFF
    byte_6 = range_value & 0xFF
    cmd_list.append(byte_5)
    cmd_list.append(byte_6)

    checksum = (sum(cmd_list) % 0x100)
    cmd_list.append(checksum)

    cmd = ' '.join(f"{byte:02x}" for byte in cmd_list)

    try:
        print('*****************calling send_and_receive with cmd --> ', cmd)
        resp_hex = send_and_receive(cmd)
        parsed = decode_response(resp_hex)
        result_data = {"raw": resp_hex, "parsed": parsed}
        print(result_data)
        return result_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/set-alarm")
async def set_alarm(data: AlarmModel):
    network_address_high = (data.network_address >> 8) & 0xFF
    network_address_low = data.network_address & 0xFF
    cmd_list = [0xFA, network_address_high, network_address_low, 0x9A]

    threshold_value = int(data.threshold_value)  # Assuming the device expects the value multiplied by 100

    byte_5 = (threshold_value >> 8) & 0xFF
    byte_6 = threshold_value & 0xFF
    cmd_list.append(byte_5)
    cmd_list.append(byte_6)

    checksum = (sum(cmd_list) % 0x100)
    cmd_list.append(checksum)

    cmd = ' '.join(f"{byte:02x}" for byte in cmd_list)

    try:
        print('*****************calling send_and_receive with cmd --> ', cmd)
        resp_hex = send_and_receive(cmd)
        parsed = decode_response(resp_hex)
        result_data = {"raw": resp_hex, "parsed": parsed}
        print(result_data)
        return result_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Set Data Calibration A
@app.post("/api/set-data-calibration")
async def set_data_calibration(data: CalibrationAModel):
    network_address_high = (data.network_address >> 8) & 0xFF
    network_address_low = data.network_address & 0xFF
    if data.calibration_type == "A":
        cmd_list = [0xFA, network_address_high, network_address_low, 0xCF]
        calibration_value = int(data.calibration_value * 1000)  # Assuming the device expects the value multiplied by 1000
    elif data.calibration_type == "B":
        cmd_list = [0xFA, network_address_high, network_address_low, 0xD0]
        calibration_value = int(data.calibration_value * 10)  # Assuming the device expects the value multiplied by 10

    
    print("calibration_value --> ", calibration_value)

    byte_5 = (calibration_value >> 8) & 0xFF
    byte_6 = calibration_value & 0xFF
    cmd_list.append(byte_5)
    cmd_list.append(byte_6)

    checksum = (sum(cmd_list) % 0x100)
    cmd_list.append(checksum)

    cmd = ' '.join(f"{byte:02x}" for byte in cmd_list)

    try:
        print('*****************calling send_and_receive with cmd:', cmd)
        resp_hex = send_and_receive(cmd)
        parsed = decode_response(resp_hex)
        result_data = {"raw": resp_hex, "parsed": parsed}
        print(result_data)
        return result_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
     
@app.post("/api/set-correction-value")
async def set_correction_value(data: CorrectValueModel):
    network_address_high = (data.network_address >> 8) & 0xFF
    network_address_low = data.network_address & 0xFF
    cmd_list = [0xFA, network_address_high, network_address_low, 0x9E]

    correction_value = data.correction_value
    byte_5 = (correction_value >> 8) & 0xFF
    byte_6 = correction_value & 0xFF
    cmd_list.append(byte_5)
    cmd_list.append(byte_6)

    checksum = (sum(cmd_list) % 0x100)
    cmd_list.append(checksum)

    cmd = ' '.join(f"{byte:02x}" for byte in cmd_list)

    try:
        print('*****************calling send_and_receive with cmd:', cmd)
        resp_hex = send_and_receive(cmd)
        parsed = decode_response(resp_hex)
        result_data = {"raw": resp_hex, "parsed": parsed}
        print(result_data)
        return result_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/set-cancel-correction-value")
async def set_cancel_correction_value(data: CorrectValueModel):
    network_address_high = (data.network_address >> 8) & 0xFF
    network_address_low = data.network_address & 0xFF
    cmd_list = [0xFA, network_address_high, network_address_low, 0xA5]

    correction_value = 0  # Setting correction value to 0 to cancel
    byte_5 = (correction_value >> 8) & 0xFF
    byte_6 = correction_value & 0xFF
    cmd_list.append(byte_5)
    cmd_list.append(byte_6)

    checksum = (sum(cmd_list) % 0x100)
    cmd_list.append(checksum)

    cmd = ' '.join(f"{byte:02x}" for byte in cmd_list)

    try:
        print('*****************calling send_and_receive with cmd:', cmd)
        resp_hex = send_and_receive(cmd)
        parsed = decode_response(resp_hex)
        result_data = {"raw": resp_hex, "parsed": parsed}
        print(result_data)
        return result_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/set-calibration-setup")
async def set_calibration_setup(data: deviceCalibrationModel):
    network_address_high = (data.network_address >> 8) & 0xFF
    network_address_low = data.network_address & 0xFF
    if data.calibration_type == "manual-zero-calibration":
        cmd_list = [0xFA, network_address_high, network_address_low, 0xD1]
    elif data.calibration_type == "cancel-zero-calibration":
        cmd_list = [0xFA, network_address_high, network_address_low, 0xD2]
    elif data.calibration_type == "range-calibration":
        cmd_list = [0xFA, network_address_high, network_address_low, 0xD3]
    
    calibration_value = 0  # No additional value needed for these commands

    byte_5 = (calibration_value >> 8) & 0xFF
    byte_6 = calibration_value & 0xFF
    cmd_list.append(byte_5)
    cmd_list.append(byte_6)

    checksum = (sum(cmd_list) % 0x100)
    cmd_list.append(checksum)

    cmd = ' '.join(f"{byte:02x}" for byte in cmd_list)

    try:
        print('*********calling send_and_receive with cmd:', cmd)
        resp_hex = send_and_receive(cmd)
        parsed = decode_response(resp_hex)
        result_data = {"raw": resp_hex, "parsed": parsed}
        print(result_data)
        return result_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#Uncomment below to run FastAPI with webview directly from this file
if __name__ == "__main__":
    threading.Thread(target=run_fastapi, daemon=True).start()

    webview.create_window('UserMonitor_v1', 'http://127.0.0.1:8000')
    webview.start()