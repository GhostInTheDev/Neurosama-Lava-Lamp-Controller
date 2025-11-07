// static/app.js
const API_BASE = '';

// Global state to track sync mode status
let isSyncActive = false;

// --- Helper Functions ---

/**
 * Decodes the raw Tuya HSB/HSV string (HHHHSSSSVVVV) into a standard HEX color string.
 * (Omitted full function for brevity, assumed functional from previous step)
 */
function tuyaHsvToHex(hsvString) {
    if (!hsvString || hsvString.length < 12) return null;
    try {
        const h = parseInt(hsvString.substring(0, 4), 16);
        const s = parseInt(hsvString.substring(4, 8), 16);
        const v = parseInt(hsvString.substring(8, 12), 16);
        const H = h / 360;
        const S = s / 1000;
        const V = v / 1000;

        let r, g, b;
        let i = Math.floor(H * 6);
        let f = H * 6 - i;
        let p = V * (1 - S);
        let q = V * (1 - f * S);
        let t = V * (1 - (1 - f) * S);

        switch (i % 6) {
            case 0: r = V, g = t, b = p; break;
            case 1: r = q, g = V, b = p; break;
            case 2: r = p, g = V, b = t; break;
            case 3: r = p, g = q, b = V; break;
            case 4: r = t, g = p, b = V; break;
            case 5: r = V, g = p, b = q; break;
        }

        const toHex = (x) => {
            const hex = Math.round(x * 255).toString(16);
            return hex.length === 1 ? '0' + hex : hex;
        };

        return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
    } catch (e) {
        return null;
    }
}


// --- EVENT LISTENERS ---

document.addEventListener('DOMContentLoaded', () => {
    // Standard Controls
    document.getElementById('btn-on').addEventListener('click', () => { setPower('on'); });
    document.getElementById('btn-off').addEventListener('click', () => { setPower('off'); });
    document.getElementById('btn-set-color').addEventListener('click', () => {
        const color = document.getElementById('color-picker').value;
        const brightness = document.getElementById('brightness-slider').value;
        setColor(color, brightness);
    });
    document.getElementById('brightness-slider').addEventListener('input', (e) => {
        document.getElementById('brightness-value').textContent = e.target.value;
    });
    document.querySelectorAll('.color-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById('color-picker').value = btn.dataset.color;
            const brightness = document.getElementById('brightness-slider').value;
            setColor(btn.dataset.color, brightness);
        });
    });

    // Sync Toggle
    document.getElementById('btn-sync').addEventListener('change', handleSyncToggle);

    // --- SCHEDULING LISTENERS ---
    document.getElementById('schedule-action').addEventListener('change', updateScheduleForm);
    document.getElementById('btn-add-schedule').addEventListener('click', handleAddSchedule);

    // Initial setup
    fetchEffects();
    fetchSchedules(); // Fetch initial schedules
    updateStatus();
    setInterval(updateStatus, 5000); // Poll status every 5 seconds
});


// --- SCHEDULING LOGIC ---

function updateScheduleForm() {
    const action = document.getElementById('schedule-action').value;
    const colorOptions = document.querySelector('.schedule-on-options');
    const effectOptions = document.querySelector('.schedule-effect-options');

    // Reset visibility
    colorOptions.style.display = 'none';
    effectOptions.style.display = 'none';

    if (action === 'on') {
        colorOptions.style.display = 'flex';
    } else if (action === 'effect' || action === 'sync') {
        effectOptions.style.display = 'flex';
        // Hide effect name selector if action is 'sync'
        document.getElementById('schedule-effect-name').style.display = (action === 'effect' ? 'block' : 'none');
    }
}

async function handleAddSchedule() {
    const action = document.getElementById('schedule-action').value;
    const timeInput = document.getElementById('schedule-time').value;
    
    if (!timeInput) {
        alert("Please set a time for the schedule.");
        return;
    }

    // Convert datetime-local format (YYYY-MM-DDTHH:MM) to YYYY-MM-DD HH:MM
    const time_str = timeInput.replace('T', ' ');

    let data = { action: action, time: time_str };

    if (action === 'on') {
        data.color = document.getElementById('schedule-color').value;
        data.brightness = document.getElementById('schedule-brightness').value;
    } else if (action === 'effect') {
        data.effect = document.getElementById('schedule-effect-name').value;
        data.duration = document.getElementById('schedule-duration').value;
    } else if (action === 'sync') {
        data.duration = document.getElementById('schedule-duration').value;
        data.effect = 'sync'; // Force effect name for API consistency
    }

    const result = await apiCall('/api/schedule/add', data, 'POST', 'Error adding schedule');
    if (result && result.success) {
        alert("Schedule added successfully!");
        fetchSchedules();
        // Optional: clear form inputs
    }
}

async function handleRemoveSchedule(index) {
    if (!confirm(`Are you sure you want to remove schedule #${index}?`)) {
        return;
    }
    
    const result = await apiCall(`/api/schedule/remove/${index}`, {}, 'DELETE', 'Error removing schedule');
    if (result && result.success) {
        alert("Schedule removed successfully!");
        fetchSchedules();
    }
}

async function fetchSchedules() {
    try {
        const response = await fetch(`${API_BASE}/api/schedule/list`);
        const data = await response.json();
        const tbody = document.getElementById('schedules-tbody');
        tbody.innerHTML = '';
        
        if (data.success && data.schedules.length > 0) {
            data.schedules.forEach((schedule, index) => {
                const row = tbody.insertRow();
                const indexCell = index + 1;
                
                // Format Time: Remove seconds and timezone info
                const time = new Date(schedule.time).toLocaleString('en-US', {
                    year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                });
                
                let details = '';
                if (schedule.action === 'on') {
                    details = `${schedule.color} @ ${schedule.brightness}%`;
                } else if (schedule.action === 'effect') {
                    details = `${schedule.effect.toUpperCase()} (${schedule.duration}s)`;
                } else if (schedule.action === 'sync') {
                    details = `SYNC (${schedule.duration}s)`;
                }

                row.insertCell().textContent = indexCell;
                row.insertCell().textContent = time;
                row.insertCell().textContent = schedule.action.toUpperCase();
                row.insertCell().textContent = details;
                
                const removeCell = row.insertCell();
                const btn = document.createElement('button');
                btn.textContent = 'Remove';
                btn.className = 'btn btn-remove';
                btn.onclick = () => handleRemoveSchedule(indexCell);
                removeCell.appendChild(btn);
            });
        } else {
            const row = tbody.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 5;
            cell.textContent = "No scheduled jobs.";
        }
    } catch (error) {
        console.error('Error fetching schedules:', error);
        document.getElementById('schedules-tbody').innerHTML = '<tr><td colspan="5">Error loading schedules.</td></tr>';
    }
}


// --- STANDARD API AND UI LOGIC ---

async function apiCall(endpoint, data = {}, method = 'POST', errorMessage = 'API error') {
    try {
        const response = await fetch(endpoint, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: method === 'GET' ? null : JSON.stringify(data)
        });
        const result = await response.json();
        if (!result.success) {
            alert(`${errorMessage}: ${result.error}`);
        }
        return result;
    } catch (error) {
        alert(`Network Error: ${error.message}`);
    }
}

async function setPower(state) {
    const result = await apiCall(`${API_BASE}/api/power`, { state });
    if (result && result.success) updateStatus();
}

async function setColor(color, brightness = 100) {
    await apiCall(`${API_BASE}/api/color`, {
        type: 'hex',
        value: color,
        brightness: parseInt(brightness)
    }, 'POST', 'Error setting color');
}

async function fetchEffects() {
    fetch('/api/effects')
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('effects-container');
            const select = document.getElementById('schedule-effect-name');
            container.innerHTML = '';
            select.innerHTML = '';

            data.effects.forEach(effect => {
                // UI Buttons
                const btn = document.createElement('button');
                btn.className = 'btn btn-effect';
                btn.textContent = effect.charAt(0).toUpperCase() + effect.slice(1);
                btn.addEventListener('click', () => apiCall('/api/effect', { name: effect }));
                container.appendChild(btn);

                // Scheduling Select Options
                const option = document.createElement('option');
                option.value = effect;
                option.textContent = effect.charAt(0).toUpperCase() + effect.slice(1);
                select.appendChild(option);
            });
            updateScheduleForm(); // Initialize form visibility after loading effects
        });
}

// ... (Rest of the functions: updateStatus, updateSyncButtonUI, handleSyncToggle) ...

/**
 * Handles the change event for the Sync checkbox.
 */
function handleSyncToggle(event) {
    const targetState = event.target.checked ? 'on' : 'off';
    
    // We update the device state immediately, and updateStatus() will confirm
    // whether the device accepted the state change (i.e., if mode became 'music').
    syncToggle(targetState);
}

/**
 * API call to toggle the Music Sync state (DPS 21/25/27 sequence).
 */
async function syncToggle(state) {
    try {
        const response = await fetch(`${API_BASE}/api/sync_toggle`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ state })
        });
        const data = await response.json();
        
        if (!data.success) {
            alert('Error toggling sync: ' + data.error);
            updateStatus(); 
        }
    } catch (error) {
        alert('Connection error during sync toggle: ' + error);
        updateStatus();
    }
}

/**
 * Updates the appearance of the Sync Toggle based on the active state.
 * @param {boolean} isActive - Whether the device is currently in 'music' mode.
 */
function updateSyncButtonUI(isActive) {
    const toggle = document.getElementById('btn-sync');
    const statusSpan = document.getElementById('sync-status');
    
    // Set the checkbox checked state based on device status
    toggle.checked = isActive;

    if (isActive) {
        statusSpan.textContent = "ACTIVE";
        statusSpan.style.color = '#00AA00';
    } else {
        statusSpan.textContent = "OFF";
        statusSpan.style.color = '#cc0000';
    }
}

async function updateStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const data = await response.json();
        
        if (data.success && data.status) {
            const dps = data.status;
            
            // COLOR PICKER INITIALIZATION/UPDATE
            const rawColor = dps['24']; // DPS 24 holds the raw HSB/HSV string
            const hexColor = tuyaHsvToHex(rawColor);
            
            if (hexColor) {
                const colorPicker = document.getElementById('color-picker');
                if (colorPicker.value.toUpperCase() !== hexColor.toUpperCase()) {
                    colorPicker.value = hexColor;
                }
            }

            // Check DPS 21 (Mode) to determine sync state
            const currentMode = dps['21'];
            isSyncActive = currentMode === 'music';
            
            // Update UI based on the device's actual mode
            updateSyncButtonUI(isSyncActive);
            
            // Format the status box content
            document.getElementById('status').innerHTML = `
                <strong>Power:</strong> ${dps['20'] ? 'ON' : 'OFF'} (DPS 20)<br>
                <strong>Mode:</strong> ${currentMode} (DPS 21)<br>
                <strong>Raw DPS:</strong> ${JSON.stringify(dps, null, 2).substring(0, 150)}...
            `;

        }
    } catch (error) {
        document.getElementById('status').textContent = 'Error loading status';
    }
}