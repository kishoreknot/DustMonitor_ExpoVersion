export function updateReading(parsed) {
  if (!parsed) return;

  document.querySelector("#networkAddressValue").textContent =
    parsed.network_address ?? "--";

  document.querySelector("#dustConcentrationValue").textContent =
    parsed.dust_concentration ?? "--";

  document.querySelector("#pcbTempValue").textContent =
    parsed.pcb_temperature ?? "--";

  document.querySelector("#currentLoopValue").textContent =
    parsed.current_loop ?? "--";

  document.querySelector("#ldValue").textContent =
    parsed.ld ?? "--";

  document.querySelector("#pdValue").textContent =
    parsed.pd ?? "--";

}

export function updateDeviceInfo(parsed) {
  console.log("updateDeviceInfo called with:", parsed);

  if (!parsed) return; 
  document.querySelector("#networkAddressValue_info").textContent = 
    parsed.network_address_info ?? "--";
  
  document.querySelector("#rangeValue_info").textContent = 
    parsed.range ?? "--";

  document.querySelector("#alarmThresholdValue_info").textContent = 
    parsed.alarm_threshold ?? "--";
    
  // document.querySelector("#smoothingTimeValue_info").textContent = 
  //   parsed.smoothing_time_sec ?? "--";

  document.querySelector("#calibrationAValue_info").textContent = 
    parsed.calibration_a ?? "--";

  document.querySelector("#calibrationBValue_info").textContent = 
    parsed.calibration_b ?? "--";

  // document.querySelector("#tempAuthDaysValue_info").textContent = 
  //   parsed.temp_auth_days ?? "--";

  // document.querySelector("#MSN_info").textContent = 
  //   parsed.MSN ?? "--";

  document.querySelector("#userHoursValue_info").textContent = 
    parsed.TimeUserHours ?? "--";
}

//Dark Mode Toggle Key Central Logic
const DARK_MODE_KEY = "dark-mode";

export function initDarkMode() {
  const isDarkMode = localStorage.getItem(DARK_MODE_KEY) === "true";

  if (isDarkMode === "enabled") {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
}

export function toggleDarkMode() {
  console.log('Inside ToggleDarkMode')
  const innerHTML = document.documentElement;
  const isDarkMode = innerHTML.classList.toggle("dark");
  localStorage.setItem(DARK_MODE_KEY, isDarkMode ? "enabled" : "disabled");
}


export function switchCorrectionTab(tabId) {
    // 1. Hide all tab content
    document.querySelectorAll('.corr-content').forEach(el => el.classList.add('hidden'));
    
    // 2. Show selected content
    document.getElementById(tabId).classList.remove('hidden');

    // 3. Reset all button styles
    document.querySelectorAll('.corr-tab-btn').forEach(btn => {
        btn.classList.remove('bg-white', 'dark:bg-slate-700', 'shadow-sm', 'text-blue-600', 'dark:text-blue-400');
        btn.classList.add('text-slate-600', 'dark:text-slate-400');
    });

    // 4. Set active style for clicked button
    const activeBtn = document.getElementById(`btn-${tabId}`);
    activeBtn.classList.add('bg-white', 'dark:bg-slate-700', 'shadow-sm', 'text-blue-600', 'dark:text-blue-400');
    activeBtn.classList.remove('text-slate-600', 'dark:text-slate-400');
}

export async function handleModifyCalibration(type, inputId) {
    const value = document.getElementById(inputId).value;
    console.log(`Setting ${type} to: ${value}`);

    // await updateSystemSetting(type, inputId);
    
    // Here you will eventually call your API (api.js)
    // Example: await api.setCalibration(type, value);
}


// Function to populate the fields from readSystemInfo
export function populateSystemSettings(info) {
    if (!info) return;
    
    const mapping = {
        // 'sys-smoothing': info.parsed.smoothing_time_sec,
        'sys-range': info.parsed.range,
        'sys-alarm': info.parsed.alarm_threshold,
        'sys-network': info.parsed.network_address_info,
        'sys-calibration-a': info.parsed.calibration_a,
        'sys-calibration-b': info.parsed.calibration_b,
        'readonly-corr-factor': info.parsed.calibration_factor 
    };

    for (const [id, value] of Object.entries(mapping)) {
        const input = document.getElementById(id);
        if (input) input.value = value;
    }
}


// Helper to show professional inline notifications
export function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    
    // Define colors based on success or error
    const bgColor = type === 'success' ? 'bg-emerald-500' : 'bg-red-500';
    const icon = type === 'success' 
        ? '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>'
        : '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>';

    // Set classes for animation and styling
    toast.className = `flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg text-white transform transition-all duration-300 translate-x-full opacity-0 ${bgColor}`;
    toast.innerHTML = `${icon} <span class="text-sm font-medium">${message}</span>`;

    container.appendChild(toast);

    // Animate In: Slide from right
    setTimeout(() => {
        toast.classList.remove('translate-x-full', 'opacity-0');
        toast.classList.add('translate-x-0', 'opacity-100');
    }, 10);

    // Animate Out and Remove after 2 seconds
    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-[-20px]'); // Slide up slightly while fading
        setTimeout(() => toast.remove(), 3000);
    }, 1000);
}

export function checkDustLevel() {
    const container = document.getElementById('alarm-threshold-alert');
    const currentVal = parseFloat(document.getElementById('dustConcentrationValue').innerText);
    const thresholdVal = parseFloat(document.getElementById('alarmThresholdValue_info').innerText);
    console.log("CurrentVal", currentVal);
    console.log("thresholdVal", thresholdVal);

    if (currentVal > thresholdVal) {
        console.log("Alarm style would be added here")
        // Toggle our custom animation
        container.classList.add('animate-alarm', 'text-orange');
    } else {
        container.classList.remove('animate-alarm', 'text-white');
    }
}

// ********* Chart Logic *** needs refinement
let dustChart = null;

export function initChart() {
    const ctx = document.getElementById('historyChart').getContext('2d');
    
    dustChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], // Timestamps
            datasets: [{
                label: 'Dust Concentration (mg/m³)',
                data: [],
                borderColor: '#3b82f6', // blue-500
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true,
                tension: 0.4, // Smoothing
                pointRadius: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(200, 200, 200, 0.1)' } },
                x: { grid: { display: false } }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// Function to add a single new point to the chart
export function addChartData(timestamp, value) {
    if (!dustChart) return;

    // Add new data
    dustChart.data.labels.push(timestamp);
    dustChart.data.datasets[0].data.push(value);

    // Keep only the last 50 points on the screen
    if (dustChart.data.labels.length > 50) {
        dustChart.data.labels.shift();
        dustChart.data.datasets[0].data.shift();
    }

    dustChart.update('none'); // Update without animation for performance
}

// Function to load bulk history from new API
export function loadFullHistory(historyArray) {
    if (!dustChart) return;
    
    dustChart.data.labels = historyArray.map(h => h.timestamp);
    dustChart.data.datasets[0].data = historyArray.map(h => h.dust);
    dustChart.update();
}

export function updateDustAlert() {
    const dustElement = document.getElementById('dustConcentrationValue');
    const thresholdElement = document.getElementById('alarmThresholdValue_info');
    const card = document.getElementById('dustConcDiv');
    
    // 1. Get Chart Instance
    const chart = Chart.getChart("historyChart"); 

    const concentration = parseFloat(dustElement.innerText);
    const threshold = parseFloat(thresholdElement.innerText);

    if (!isNaN(concentration) && !isNaN(threshold) && chart) {
        const isAlarm = concentration > threshold;

        // Toggle Card Classes
        card.classList.toggle('from-orange-500', isAlarm);
        card.classList.toggle('to-red-600', isAlarm);
        card.classList.toggle('animate-pulse', isAlarm);
        card.classList.toggle('from-emerald-400', !isAlarm);
        card.classList.toggle('to-teal-500', !isAlarm);

        // 2. Update Chart Colors
        const alarmColor = 'rgba(239, 68, 68, 1)';    // Tailwind red-500
        const normalColor = 'rgba(16, 185, 129, 1)';   // Tailwind emerald-500
        const alarmFill = 'rgba(239, 68, 68, 0.1)'; 
        const normalFill = 'rgba(16, 185, 129, 0.1)';

        chart.data.datasets[0].borderColor = isAlarm ? alarmColor : normalColor;
        chart.data.datasets[0].backgroundColor = isAlarm ? alarmFill : normalFill;
        
        // Refresh the chart to show changes
        chart.update('none'); // 'none' prevents reset animations for a smoother look
    }
}