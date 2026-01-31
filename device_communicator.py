import json, os, sys, logging, struct, serial, threading
import serial.tools.list_ports
from database import engine



#Gloabal Variable
serial_connection = None
device_status = {"connected": False, "error": None, "port": None}
serial_lock = threading.Lock()

if getattr(sys, 'frozen', False):
    # If compiled, the base path is the executable's folder
    BASE = os.path.dirname(sys.executable)
else:
    # If running as a script, the base path is the current file's folder
    BASE = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(BASE, "config.json")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
    
# def search_serial_ports():
#     """Search for available serial ports."""
#     ports = serial.tools.list_ports.comports()
#     return [port.device for port in ports]

def get_serial_connection():
    """Establish and return a serial connection based on config.
    """
    global serial_connection
    if serial_connection is None or not serial_connection.is_open:
        #print("Creating fresh connection...")
        try:
            ports = serial.tools.list_ports.comports()
            if len(ports) == 0:
                #print("K1..")
                device_status = {"connected": False, "error": "No serial ports found", "port": None}
                return None
            elif len(ports) == 1:
                #print("K2..")
                port = ports[0].device
                # #print(f"Using the only available port: {port}")
                # #print("Manufacturer:", ports[0].manufacturer)
                # #print("Description:", ports[0].description)
                # #print("HWID:", ports[0].hwid)
                # #print("VID:", ports[0].vid)
                # #print("PID:", ports[0].pid)
                # #print("Serial Number:", ports[0].serial_number)
                # #print("Location:", ports[0].location)
                # #print("Product:", ports[0].product)
                # #print("Interface:", ports[0].interface)
                # #print("---------------------------------------------------")
            
            cfg = load_config()
            # port = cfg.get("serial", {}).get("port", "COM6")
            baud = cfg.get("serial", {}).get("baudrate", 9600)
            parity = cfg.get("serial", {}).get("parity", serial.PARITY_NONE)
            bytesize = cfg.get("serial", {}).get("bytesize", 8)
            #print("port:", port)
            serial_connection = serial.Serial(port=port, baudrate=baud, parity=parity, bytesize= bytesize, timeout=1)
            command_hex = "fa ff ff 98 00 00 90"
            cmd_bytes = bytes.fromhex(command_hex.replace(" ", ""))
            btye_write = serial_connection.write(cmd_bytes)
            #print('byte_write', btye_write)
            first_byte = serial_connection.read(1)
            #print('first_byte', first_byte)
            if first_byte == b'\xFA':
                #print("First bit received..")
                device_status = {"connected": True, "error": None, "port": port}
                return serial_connection
            else:
                #print("No First bit received..")
                serial_connection = None
                device_status = {"connected": False, "error": "Device Not Connected", "port": None}
                return None
        except Exception as e:
            device_status = {"connected": False, "error": str(e), "port": None}
            #print('K4..', device_status)
            return None
    
    return serial_connection 

def close_serial_port():
    if serial_connection:
        serial_connection.close()
        return {"Status": "Closed"}
    return {"Status": "Closed"}

def send_and_receive(command_hex: str) -> str:
    """Send a hex command (string) to device and return hex response string.
    """
    #print("command_hex:", command_hex)
    # Convert hex string to bytes
    try:
        cmd_bytes = bytes.fromhex(command_hex.replace(" ", ""))
        #print('cmd_bytes --> ', cmd_bytes)
        if len(cmd_bytes) < 7:
            raise Exception("Command too short")
        if len(cmd_bytes) > 7:
            raise Exception("Command too long")
        if len(cmd_bytes) != 7:
            raise Exception("Command should be 7 bytes")
        if cmd_bytes[0] != 0xFA:
            raise Exception("Invalid start byte in command")
        
    except Exception as e:
        return f"Error: invalid command hex - {str(e)}"

    # Can be removed If centralized serial connection logic works.
    # cfg = load_config()
    # port = cfg.get("serial", {}).get("port", "COM6")
    # baud = cfg.get("serial", {}).get("baudrate", 9600)
    # parity = cfg.get("serial", {}).get("parity", "N")
    # bytesize = cfg.get("serial", {}).get("bytesize", 8)
    
    with serial_lock:
        ser = get_serial_connection()
        if ser is not None:
            ser.reset_input_buffer()
            ser.reset_output_buffer()
        else:
            return {"error":"No connection Established"}
        try:
            # #print("ser.port:", ser.port)
            # #print("ser.baudrate:", ser.baudrate)
            # #print("ser.parity:", ser.parity)
            # #print("ser.bytesize:", ser.bytesize)
            # #print("ser.timeout:", ser.timeout)
            # #print("Sending command...")

            # #print("First byte even before reading:",ser.read(1))  

            bytes_sent = ser.write(cmd_bytes)
            #print("bytes_sent:", bytes_sent)
            if bytes_sent != len(cmd_bytes): 
                logging.warning("Sent %d bytes, expected %d", bytes_sent, len(cmd_bytes))   
            
            resp = ser.read(1) # read first byte to check the start byte
            #print("resp first byte:", resp)
            if not resp: 
                #print("No response from device")
                raise Exception("No response from device")
            if resp != b'\xFA':
                #print("Invalid start byte in response")
                raise Exception("Invalid start byte")
            
            second_byte = ser.read(1) # Read 2nd byte, indicates number of bytes contained in this packet
            #print("second_byte:", second_byte)
            if not second_byte:
                raise Exception("Incomplete response from device. Second byte missing in response.")
            resp += second_byte
            packet_length = int.from_bytes(second_byte, "big") # More reliable but below one is faster
            # packet_length = second_byte[0]
            #print("packet_length:", packet_length)
            resp += ser.read(packet_length - 2) # read the rest of the packet
            #print("*************resp.hex()************\n", resp.hex())
            return resp.hex()
        except Exception as e:
                    #need to remove this later
            import traceback
            error_details = traceback.format_exc()
            #print(f"DEBUG LOG:\n{error_details}")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = exc_tb.tb_frame.f_code.co_filename
            line_no = exc_tb.tb_lineno
            #print(f"Error: {exc_type.__name__} in {fname} at line {line_no}: {str(e)}")
            raise Exception(f"Serial communication error: {str(e)}")


def decode_response(hexstr: str) -> dict:
    """Decode Bytes response into sensor fields.
    Returns a dict with interpreted values.
    """
    # #print("***************hexstr*****************", hexstr)
    try:
        b = bytes.fromhex(hexstr)
        # #print("***************bytes*****************", b)
        if len(b) >= 2 and b[0] != 0xFA:
            return {"error": "invalid start byte in Response"}
        if len(b) >= 2 and b[-1] != 0xF5:
            return {"error": "invalid end byte in Response"}
    except Exception:
        return {"error": "invalid hex"}
    decoded_resp = {}
    cmdId = b[4]
    # #print("****************cmdId****************", cmdId)
    if cmdId == 0xC9:
        #print("My News---->",engine.url.host) #KIDEL
        if len(b) < 39:
            #print(f"!!! CRITICAL: Received short packet ({len(b)} bytes). Skipping decode.")
            return {"error": "incomplete response for command C9"}
        
        calculated_checksum = sum(b[:-2]) % 0x100
        if calculated_checksum != b[-2]:
            #print("****************calculated_checksum****************", calculated_checksum, b[-1])
            #print("!!! CRITICAL: Checksum mismatch. Data is corrupted.")
            return {"error": "Checksum failed"}
        
        decoded_resp["network_address"] = int.from_bytes(b[2:4], "big")
        decoded_resp["ld"] = int.from_bytes(b[5:7], "big")
        decoded_resp["pd"] = int.from_bytes(b[7:9], "big")
        decoded_resp["pcb_temperature"] = round(25 - (int.from_bytes(b[19:21], "big") - 1065) * 1025 / 4096, 2)
        decoded_resp["dust_concentration"] = round(struct.unpack(">f", b[25:29])[0], 2)
        decoded_resp["current_loop"] = int.from_bytes(b[33:35], "big") / 100
        #print("***********************decode_response:************************ \n", decoded_resp)
    elif cmdId == 0x98:
        decoded_resp["network_address_info"] = int.from_bytes(b[2:4], "big")
        decoded_resp["calibration_factor"] = round(struct.unpack(">f", b[5:9])[0], 3)
        #print("calibration_factor:", decoded_resp["calibration_factor"])
        if decoded_resp["calibration_factor"] > 10:
            decoded_resp["calibration_a"] = 10.0
        elif decoded_resp["calibration_factor"] < 10:
            decoded_resp["calibration_a"] = decoded_resp["calibration_factor"]
        #print("calibration_a:", decoded_resp["calibration_a"])
        decoded_resp["range"] = int.from_bytes(b[9:11], "big")
        decoded_resp["calibration_b"] = round(struct.unpack(">f", b[11:15])[0], 3)
        decoded_resp["smoothing_time_sec"] = struct.unpack(">f", b[41:45])[0] #int.from_bytes(b[41:45], "big")
        decoded_resp["temp_auth_days"] = int.from_bytes(b[49:51], "big")
        decoded_resp["TimeUserHours"] = int.from_bytes(b[51:53], "big")
        decoded_resp["MSN"] = int.from_bytes(b[55:57], "big")
        decoded_resp["alarm_threshold"] = int.from_bytes(b[59:61], "big")
        
    elif cmdId == 0x97:
        decoded_resp["set_network_address_ack"] = "Success"
        decoded_resp["new_network_address"] = int.from_bytes(b[2:4], "big")
        
    elif cmdId == 0x8C:
        decoded_resp["set_smoothing_time_ack"] = "Success"
        decoded_resp["new_smoothing_time_sec"] = struct.unpack(">f", b[5:9])[0]
        
    elif cmdId == 0x9D:
        decoded_resp["set_range_ack"] = "Success"
        decoded_resp["new_range"] = int.from_bytes(b[5:7], "big")
        
    elif cmdId == 0x9A:
        decoded_resp["set_alarm_ack"] = "Success"
        decoded_resp["new_alarm_threshold"] = int.from_bytes(b[5:7], "big")
        
    elif cmdId == 0xCF:
        decoded_resp["set_calibration_a_ack"] = "Success"
        decoded_resp["new_calibration_a"] = struct.unpack(">f", b[5:9])[0]
    elif cmdId == 0xD0:
        decoded_resp["set_calibration_b_ack"] = "Success"
        decoded_resp["new_calibration_b"] = struct.unpack(">f", b[5:9])[0]
    elif cmdId == 0x9E:
        decoded_resp["set_correction_value_ack"] = "Success"
        decoded_resp["new_correction_value"] = round(struct.unpack(">f", b[5:9])[0], 3)
    elif cmdId == 0xA5:
        decoded_resp["set_cancel_correction_ack"] = "Success"
        decoded_resp["cancel_correction_value"] = 1.0
    elif cmdId == 0xD1:
        decoded_resp["set_zero_calibration_ack"] = "Success"
    elif cmdId == 0xD2:
        decoded_resp["cancel_zero_calibration_ack"] = "Success"
    elif cmdId == 0xD3:
        decoded_resp["set_range_calibration_ack"] = "Success"
    #print("***********************decode_response:************************\n", decoded_resp)
    return decoded_resp
