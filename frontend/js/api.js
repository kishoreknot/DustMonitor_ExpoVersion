import { showToast, updateDeviceInfo, populateSystemSettings,checkDustLevel } from "./ui.js";

const API_BASE = ""; // same origin (FastAPI)

export async function gotoHome() {
  window.location.href = "/";
}

export async function connectDevice() {

    const btn = document.getElementById('connectBtn');
    const btnText = document.getElementById('btnText');
    const dot = document.getElementById('statusDot');
    const ping = document.getElementById('statusDotPing');
    const spinner = document.getElementById('loadingSpinner');

    btn.disabled = true;
    spinner.classList.remove('hidden');
    btnText.innerText = "Connecting...";
    dot.className = "relative inline-flex rounded-full h-3 w-3 bg-yellow-500";
    ping.className = "absolute inline-flex h-full w-full rounded-full bg-yellow-400 animate-ping opacity-75";

    try {
        const response = await fetch(`${API_BASE}/api/connect-device`, {
            method: "POST",
            headers: { "Content-Type": "application/json" }
            });
            // if (!response.ok) throw new Error("Failed to connect to device");
            const resp = await response.json();
            console.log("device connection status return value", resp.status);
            if (resp.status === "Connected") {
                dot.className = "relative inline-flex rounded-full h-3 w-3 bg-green-500";
                ping.className = "absolute inline-flex h-full w-full rounded-full bg-green-400 animate-ping opacity-75";
                btnText.innerText = "Connected";
                // showToast("Device connected successfully!", 'success');
                try {
                    const info = await readSystemInfo();
                    console.log("System Info:", info);
                    if (info.parsed) {
                    updateDeviceInfo(info.parsed);
                    window.NETWORK_ADDRESS = parseInt(document.getElementById("networkAddressValue_info").textContent);
                    console.log("Updated Device Info on Load, network_address_info", info.parsed.network_address_info);
                    }
                    else {
                    console.error("Failed to fetch system info");
                    }
                } catch (err) {
                    console.error("Error fetching system info:", err);
                }
            } else if (resp.status === "NotConnected") {
                dot.className = "relative inline-flex rounded-full h-3 w-3 bg-red-500";
                ping.className = "absolute inline-flex h-full w-full rounded-full bg-red-400 animate-ping opacity-75";
                btnText.innerText = "Connect Failed. Retry";
                // showToast(`Connection failed: ${resp.error || 'Unknown error'}`, 'error');
            }
    } catch (err) {
        dot.className = "relative inline-flex rounded-full h-3 w-3 bg-red-500";
        ping.className = "absolute inline-flex h-full w-full rounded-full bg-red-400 animate-ping opacity-75";
        btnText.innerText = "Connection Failed. Retry";
        // showToast(`Connection error: ${err.message}`, 'error');
    }
    finally {
        btn.disabled = false;
        spinner.classList.add('hidden');
    }
}

export async function readSystemInfo() {
  const res = await fetch(`${API_BASE}/api/read-system-info`);
  if (!res.ok) throw new Error("Failed to read system info");
  return res.json();
}

export async function readData(period_in_seconds, network_address){
  console.log("readData called with:", period_in_seconds, network_address);
  const res = await fetch(`${API_BASE}/api/read-data`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ period_in_seconds, network_address })
  });
  if (!res.ok) {
    const errorDetail = await res.json();
    throw new Error(errorDetail.detail || "Server Error");
    
  }

  return res.json();
}
  
// Function to call specific POST APIs
export async function updateSystemSetting(type, inputId) {
    const inputValue = document.getElementById(inputId).value;
    const button = document.querySelector(`button[onclick*="${inputId}"]`);

    const currentNetAddr = parseInt(NETWORK_ADDRESS);

    let payload = {};
    let endpoint = "";
    let ackKey = "";

    switch (type) {
        case 'smoothing-time':
            endpoint = "/api/set-smoothing-time";
            payload = { 
                smoothtime_in_seconds: parseInt(inputValue), 
                network_address: currentNetAddr 
            };
            ackKey = "set_smoothing_time_ack";
            break;
        case 'range':
            endpoint = "/api/set-range";
            payload = { 
                max_range_value: parseInt(inputValue), 
                network_address: currentNetAddr 
            };
            ackKey = "set_range_ack";
            break;
        case 'alarm':
            endpoint = "/api/set-alarm";
            payload = { 
                threshold_value: parseFloat(inputValue), 
                network_address: currentNetAddr 
            };
            ackKey = "set_alarm_ack";
            break;
        case 'network-address':
            endpoint = "/api/set-network-address";
            payload = { 
                address: parseInt(inputValue) 
            }; // NetworkAddressModel only takes 'address'
            ackKey = "set_network_address_ack";
            break;
        case 'calibration-a':
            endpoint = "/api/set-data-calibration";
            payload = { 
                calibration_value: parseFloat(inputValue), 
                network_address: currentNetAddr,
                calibration_type: "A"
            };
            ackKey = "set_calibration_a_ack";
            break;
        case 'calibration-b':
            endpoint = "/api/set-data-calibration";
            payload = { 
                calibration_value: parseFloat(inputValue), 
                network_address: currentNetAddr,
                calibration_type: "B" 
            };
            ackKey = "set_calibration_b_ack";
            break;
        case 'correction-value':
            endpoint = "/api/set-correction-value";
            payload = {
                correction_value: parseInt(inputValue),
                network_address: currentNetAddr            
              };
            ackKey = "set_correction_value_ack";
            break;
        case 'cancel-correction-value':
            endpoint = "/api/set-cancel-correction-value";
            payload = {
                correction_value: 0,
                network_address: currentNetAddr            
              };
            ackKey = "set_cancel_correction_ack";
            break;
        default:
            console.error("Unknown setting type");
            return;
    }
    
    // UI Feedback: Disable button during request
    button.disabled = true;
    const originalText = button.innerText;
    button.innerText = "Saving...";

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        const parsedData = result.parsed || {};
        console.log("API Response Parsed Data:", parsedData);

        if (response.ok && parsedData[ackKey] === "Success") {
            // alert(`${type.toUpperCase()} updated successfully!`);
            showToast(`${type.replace(/-/g, ' ')} updated successfully!`, 'success');
            let sysInfo = null;

            try {
                sysInfo = await readSystemInfo();
                console.log("System Info after update Kishore");
            } catch (err) {
                    console.error("Failed to refresh system info:", err); 
            }

            if (type === 'network-address') {
                window.NETWORK_ADDRESS = parseInt(inputValue);
            } 
            else if (type === 'correction-value') {
                const newCorrValue = parsedData["new_correction_value"];
                const readOnlyCorrectionInput = document.getElementById('readonly-corr-factor');
                if (readOnlyCorrectionInput && newCorrValue !== undefined) {
                    readOnlyCorrectionInput.value = newCorrValue;
                }

            //   We can centralize this below by refreshing all system info at once
            //   const calibrationAInput = document.getElementById('sys-calibration-a');
            //   if (newCorrValue !== undefined && newCorrValue <= 10.0) {
            //     if (calibrationAInput) {
            //       calibrationAInput.value = newCorrValue;
            //     }
            //   }
            //   else if (newCorrValue !== undefined && newCorrValue > 10.0) {
            //     if (calibrationAInput) {
            //       calibrationAInput.value = 10.0;
            //     }
            //   }
            }
            else if (type === 'cancel-correction-value') {
                //Read system info to update correction factor display
                const readOnlyCorrectionInput = document.getElementById('readonly-corr-factor');
                readOnlyCorrectionInput.value = 1.0;
                // try {
                //     const sysInfo = await readSystemInfo();
                //     console.log("System Info after cancel correction value:", sysInfo);
                //     const corrFactorInput = document.getElementById('sys-calibration-a');
                //     const readOnlyCorrectionInput = document.getElementById('readonly-corr-factor');
                //     const CalibrationAValue = document.getElementById('calibrationAValue_info');
                //     if (readOnlyCorrectionInput && corrFactorInput && sysInfo.parsed && sysInfo.parsed.calibration_factor !== undefined) {
                //     corrFactorInput.value = 1.0;
                //     readOnlyCorrectionInput.value = 1.0;
                //     }
                // }catch (err) {
                //     console.error("Failed to refresh system info:", err); 
                // }
            }
            if (sysInfo.parsed) {
                    updateDeviceInfo(sysInfo.parsed);
                    populateSystemSettings(sysInfo);
            }     
        } else {
            // throw new Error(parsedData.detail || "Update failed");
            const errorMsg = parsedData[ackKey] || "Hardware rejected the command";
            showToast(errorMsg, 'error')
        }
    } catch (err) {
        // alert("Error updating hardware: " + err.message);
        const errorLine = err.stack ? err.stack.split('\n')[1] : "Line unknown";
    
        console.error(`Error occurred: ${err.message}`);
        console.error(`Location: ${errorLine.trim()}`);
        showToast("Kishore Connection Error: " + err.message, 'error');
    } finally {
        button.disabled = false;
        button.innerText = originalText;
        
      } 
}

export async function updateCalibrations(type) {
    let inputId = "";
    let endpoint = "";
    let payload = {};
    let ackKey = "";
    const currentNetAddr = parseInt(NETWORK_ADDRESS);

    

    switch (type) {
        case 'manual-zero-calibration':
          endpoint = "/api/set-calibration-setup";
          payload = {
              calibration_type:  "manual-zero-calibration",
              network_address: currentNetAddr            
            };
          ackKey = "set_zero_calibration_ack";
          break;
        case 'cancel-zero-calibration':
          endpoint = "/api/set-calibration-setup";
          payload = {
              calibration_type:  "cancel-zero-calibration",
              network_address: currentNetAddr            
            };
          ackKey = "cancel_zero_calibration_ack";
          break;
        case 'range-calibration':
          endpoint = "/api/set-calibration-setup";
          payload = {
              calibration_type:  "range-calibration",
              network_address: currentNetAddr            
            };
          ackKey = "set_range_calibration_ack";
          break;
    }

    inputId = type;
    const button = document.querySelector(`button[onclick*="${inputId}"]`);

    // UI Feedback: Disable button during request
    button.disabled = true;
    const originalText = button.innerText;
    button.innerText = "Processing...";

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await response.json();

        const parsedData = result.parsed || {};
        console.log("API Response Parsed Data:", parsedData);

        if (parsedData[ackKey] !== "Success") {
            // throw new Error(parsedData.detail || "Update failed");
            const errorMsg = parsedData[ackKey] || "Hardware rejected the command";
            showToast(errorMsg, 'error')
        }
        else {
            showToast(`${type.replace(/-/g, ' ')} command executed successfully!`, 'success');
        }
    } catch (err) {
        // alert("Error updating hardware: " + err.message);
        showToast("Connection Error: " + err.message, 'error');
    } finally {
        button.disabled = false;
        button.innerText = originalText;
    }
}

export async function fetchHistory() {
    try {
        const response = await fetch("/api/get-reading-history");
        if (!response.ok) throw new Error("Failed to fetch history");
        return await response.json();
    } catch (err) {
        console.error("History fetch error:", err);
        return { history: [] };
    }
}