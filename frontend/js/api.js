import { showToast, updateDeviceInfo, populateSystemSettings,checkDustLevel } from "./ui.js";

let serialPort = null;
let networkAddress = null;
const API_BASE = ""; 

const hexToBytes = (hex) => {
    // 1. Ensure it's a string and trim whitespace
    const hexString = String(hex).trim();
    
    // 2. Split by one or more spaces
    return new Uint8Array(
        hexString.split(/\s+/).map(h => parseInt(h, 16))
    );
};

const bytesToHex = (bytes) => Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join(' ');

function updateStatusDot(state) {
    const dot = document.getElementById('statusDot');
    const ping = document.getElementById('statusDotPing');
    
    if (state === 'connected') {
        dot.className = "relative inline-flex rounded-full h-3 w-3 bg-green-500";
        ping.className = "absolute inline-flex h-full w-full rounded-full bg-green-400 animate-ping opacity-75";
    } else {
        dot.className = "relative inline-flex rounded-full h-3 w-3 bg-red-500";
        ping.className = "absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75";
    }
}

export async function connectDevice() {
    const btn = document.getElementById('connectBtn');
    const btnText = document.getElementById('btnText');
    const spinner = document.getElementById('loadingSpinner');

    // UI Feedback: Start
    btn.disabled = true;
    spinner.classList.remove('hidden');
    btnText.innerText = "Selecting Port...";
    try {
        // 1. Identify and Open Serial Port
        const port = await navigator.serial.requestPort();
        const openPromise = port.open({ 
            baudRate: 9600, 
            parity: "none",    
            dataBits: 8,       
            stopBits: 1 
        });

        const timeoutPromise = new Promise((_, reject) =>
            setTimeout(() => reject(new Error("Timeout: Device took too long to open")), 2000)
        );

        // Race the open process against the 2s timer
        await Promise.race([openPromise, timeoutPromise]);
        window.serialPort = port;

        btnText.innerText = "Identifying...";
        
        
        // 2. Send the Identification Command (fa ff ff 98 00 00 90)
        const initCmd = "fa ff ff 98 00 00 90";
        const responseHex = await writeAndRead(initCmd);
        
        // 3. Send raw response to Python to get it decoded
        const res = await fetch(`${API_BASE}/api/decode-info`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ raw_hex: responseHex })
        });
        const data = await res.json();

        if (data.parsed) {
            updateStatusDot('connected');
            updateDeviceInfo(data.parsed);
            populateSystemSettings(data);
            btnText.innerText = "Connected";
            btn.classList.add('bg-green-600');
            networkAddress = data.parsed.network_address_info;
            showToast(`Connected! Device Address: ${networkAddress}`, 'success');
            return data
        } else {
            throw new Error("Device did not return valid identification");
        }
    } catch (err) {
        updateStatusDot('error');

        showToast("Connection failed: " + err.message, 'error');
        btn.disabled = false;
        btnText.innerText = "Connect Device";
        throw err;
    }
    finally {
        spinner.classList.add('hidden');
    }
}

async function writeAndRead(hexCmd) {
    console.log("DEBUG: hexCmd type is", typeof hexCmd, "value:", hexCmd);
    if (!window.serialPort || !window.serialPort.writable) {
        throw new Error("Serial port not connected or not writable.");
    }
    console.log("DEBUG: Trace1");
    const writer = window.serialPort.writable.getWriter();
    console.log("DEBUG: Trace2");
    // const bytes = new Uint8Array(hexCmd.split(' ').map(h => parseInt(h, 16)));
    const bytes = hexToBytes(hexCmd);
    console.log("DEBUG: Trace3", bytes);
    await writer.write(bytes);
    console.log("DEBUG: Trace4");
    writer.releaseLock();
    console.log("DEBUG: Trace5");

    // Small delay for hardware response
    await new Promise(r => setTimeout(r, 100));
    console.log("DEBUG: Trace5.1");
    const reader = window.serialPort.readable.getReader();
    let readTimeout;
    console.log("DEBUG: Trace5.2");
    const timeoutPromise = new Promise((_, reject) => {
        readTimeout = setTimeout(() => {
            reader.cancel().catch(() => {});
            reject(new Error("Harware Response Timeout"));
        }, 5000);
    });
   
    try {
        let responseBuffer = new Uint8Array();
        
        // Loop until we have a complete packet or timeout
        while (true) {
            const { value, done } = await Promise.race([
                reader.read(),
                timeoutPromise
            ]);

            if (done) break;
            if (value) {
                // Append new chunk to our buffer
                let newBuffer = new Uint8Array(responseBuffer.length + value.length);
                newBuffer.set(responseBuffer);
                newBuffer.set(value, responseBuffer.length);
                responseBuffer = newBuffer;
                console.log("Debug Trace: 5.3")
            }

            // CHECK: Do we have enough data? 
            // Based on device_communicator.py, packets start with 0xFA
            if (responseBuffer.length >= 2) {
                const expectedLength = responseBuffer[1]; // Second byte is length
                if (responseBuffer.length >= expectedLength) {
                    break; // We have the full packet!
                }
            }
        }

        clearTimeout(readTimeout);
        console.log("Debug Trace responseBuffer: 5.4", responseBuffer)
        if (responseBuffer.length === 0) {
            throw new Error("Device returned empty data");
        }

        return bytesToHex(responseBuffer);
    } catch (err) {
        clearTimeout(readTimeout); // ERROR: Ensure timeout is cleared
        throw err;
    } finally {
        reader.releaseLock(); // ALWAYS release the lock
    }
}

export let isReading = false;
export async function stopReading() {
    isReading = false;
    // showToast("Reading stopped", "info");
}

export async function readData(period_in_seconds) {
    
    if (isReading && period_in_seconds > 0) return;
    console.log("Debug readData", period_in_seconds)

    // 1. Construct Hex Command using the global networkAddress
    const netH = (networkAddress >> 8) & 0xFF;
    const netL = networkAddress & 0xFF;
    const freq = 0xFF
    const cmdList = [0xFA, netH, netL, 0xC9, freq, 0x00];
    cmdList.push(cmdList.reduce((a, b) => a + b, 0) % 0x100);
    const hexCmd = cmdList.map(b => b.toString(16).padStart(2, '0')).join(' ');
    console.log("readData.hexCmd", hexCmd);

    if (period_in_seconds === 0) {
        return await executeSingleRead(hexCmd);
    }

    showToast(`Continuous reading started (${period_in_seconds}s interval)`, "success");
    isReading = true;
    while (isReading) {
        const result = await executeSingleRead(hexCmd);
        if (result && result.parsed) {
            window.processNewData(result.parsed); 
        }

        await new Promise(r => setTimeout(r, period_in_seconds * 1000));

    }
}

async function executeSingleRead(hexCmd) {
    try {
        const responseHex = await writeAndRead(hexCmd);
        const res = await fetch(`${API_BASE}/api/store-reading`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ raw_hex: responseHex })
        });
        return await res.json();
    } catch (err) {
        console.error("Hardware Read Error:", err);
        return null;
    }
}


export async function gotoHome() {
  window.location.href = "/";
}


export async function readSystemInfo() {
//   const res = await fetch(`${API_BASE}/api/read-system-info`);
//   if (!res.ok) throw new Error("Failed to read system info");
//   return res.json();
    const initCmd = "fa ff ff 98 00 00 90";
    const responseHex = await writeAndRead(initCmd);

    const res = await fetch(`${API_BASE}/api/decode-info`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ raw_hex: responseHex })
        });
    
    const data = await res.json();

    if (data.parsed) {
        return data
    }
}

// api.js helper
function generateHexCommand(addr, cmdId, value, valueType = 'int') {
    const high = (addr >> 8) & 0xFF;
    const low = addr & 0xFF;
    let cmdList = [0xFA, high, low, cmdId];

    if (valueType === 'float') {
        // Convert JS float to 4-byte IEEE 754 Big Endian
        const buffer = new ArrayBuffer(4);
        new DataView(buffer).setFloat32(0, value, false);
        cmdList.push(...new Uint8Array(buffer));
    } else if (valueType === 'int') {
        // 2-byte integer Big Endian
        cmdList.push((value >> 8) & 0xFF);
        cmdList.push(value & 0xFF);
    } else if (valueType === 'none') {
        // Some commands (like zero cal) just use 00 00
        cmdList.push(0x00, 0x00);
    }

    // Add Checksum (Sum % 256)
    const checksum = cmdList.reduce((a, b) => a + b, 0) % 0x100;
    cmdList.push(checksum);
    const hexCmd = cmdList.map(b => b.toString(16).padStart(2, '0')).join(' ');
    console.log("generateHexCommand hexCmd", hexCmd);
    return hexCmd;
}


export async function updateSystemSetting(type, inputId) {
    const inputValue = document.getElementById(inputId).value;
    const button = document.querySelector(`button[onclick*="${inputId}"]`);
    const currentNetAddr = networkAddress; //parseInt(window.NETWORK_ADDRESS);
    
    let hexCmd = "";
    let ackKey = "";

    switch (type) {
        case 'smoothing-time':
            hexCmd = generateHexCommand(currentNetAddr, 0x8C, parseInt(inputValue));
            ackKey = "set_smoothing_time_ack";
            break;
        case 'range':
            hexCmd = generateHexCommand(currentNetAddr, 0x9D, parseInt(inputValue));
            ackKey = "set_range_ack";
            break;
        case 'alarm':
            hexCmd = generateHexCommand(currentNetAddr, 0x9A, parseInt(inputValue));
            ackKey = "set_alarm_ack";
            break;
        case 'network-address':
            // Address change uses a broadcast-style or special logic; using 0x97
            hexCmd = generateHexCommand(currentNetAddr, 0x97, parseInt(inputValue));
            ackKey = "set_network_address_ack";
            break;
        case 'calibration-a':
            hexCmd = generateHexCommand(currentNetAddr, 0xCF, parseFloat(inputValue), 'float');
            ackKey = "set_calibration_a_ack";
            break;
        case 'calibration-b':
            hexCmd = generateHexCommand(currentNetAddr, 0xD0, parseFloat(inputValue), 'float');
            ackKey = "set_calibration_b_ack";
            break;
        case 'correction-value':
            hexCmd = generateHexCommand(currentNetAddr, 0x9E, parseFloat(inputValue), 'float');
            ackKey = "set_correction_value_ack";
            break;
        case 'cancel-correction-value':
            hexCmd = generateHexCommand(currentNetAddr, 0xA5, 0, 'none');
            ackKey = "set_cancel_correction_ack";
            break;
    }

    button.disabled = true;
    button.innerText = "Saving...";

    try {
        const responseHex = await writeAndRead(hexCmd);

        const response = await fetch(`${API_BASE}/api/decode-info`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ raw_hex: responseHex })
        });
        const result = await response.json();
        const parsedData = result.parsed || {};
        console.log("updateSystemSetting.parsedData[ackKey]", parsedData[ackKey]);
        if (parsedData[ackKey] === "Success") {
            showToast(`${type.replace(/-/g, ' ')} updated!`, 'success');
            
            // Update local memory if address changed
            if (type === 'network-address') window.NETWORK_ADDRESS = parseInt(inputValue);

            // 3. Refresh System Info to sync UI
            const info = await readSystemInfo();
            updateDeviceInfo(info.parsed);
            populateSystemSettings(info);
        } else {
            showToast("Hardware rejected command", 'error');
        }
    } catch (err) {
        showToast("Communication Error: " + err.message, 'error');
    } finally {
        button.disabled = false;
        button.innerText = "Set";
    }
}

export async function updateCalibrations(type) {
    const currentNetAddr = parseInt(window.NETWORK_ADDRESS);
    let cmdId = 0;
    let ackKey = "";

    switch (type) {
        case 'manual-zero-calibration':
            cmdId = 0xD1;
            ackKey = "set_zero_calibration_ack";
            break;
        case 'cancel-zero-calibration':
            cmdId = 0xD2;
            ackKey = "cancel_zero_calibration_ack";
            break;
        case 'range-calibration':
            cmdId = 0xD3;
            ackKey = "set_range_calibration_ack";
            break;
    }

    const hexCmd = generateHexCommand(currentNetAddr, cmdId, 0, 'none');
    const button = document.querySelector(`button[onclick*="${type}"]`);
    button.disabled = true;

    try {
        const responseHex = await writeAndRead(hexCmd);
        const res = await fetch(`${API_BASE}/api/decode-info`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ raw_hex: responseHex })
        });
        const result = await res.json();

        if (result.parsed && result.parsed[ackKey] === "Success") {
            showToast(`${type.replace(/-/g, ' ')} success!`, 'success');
        } else {
            showToast("Calibration failed", 'error');
        }
    } catch (err) {
        showToast("Error: " + err.message, 'error');
    } finally {
        button.disabled = false;
    }
}

export async function fetchHistory() {
    try {
        const response = await fetch(`${API_BASE}/api/get-reading-history`);
        if (!response.ok) throw new Error("Failed to fetch history");
        return await response.json();
    } catch (err) {
        console.error("History fetch error:", err);
        return { history: [] };
    }
}