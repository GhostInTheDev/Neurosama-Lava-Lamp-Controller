// static/app.js
const API_BASE = '';

// Global state to track sync mode status
let isSyncActive = false;

// --- EVENT LISTENERS ---

// Power controls
document.getElementById('btn-on').addEventListener('click', () => {
    setPower('on');
});

document.getElementById('btn-off').addEventListener('click', () => {
    setPower('off');
});

// Color picker
document.getElementById('btn-set-color').addEventListener('click', () => {
    const color = document.getElementById('color-picker').value;
    const brightness = document.getElementById('brightness-slider').value;
    setColor(color, brightness);
});

// Brightness slider
document.getElementById('brightness-slider').addEventListener('input', (e) => {
    document.getElementById('brightness-value').textContent = e.target.value;
});

// Quick color buttons
document.querySelectorAll('.color-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const color = btn.dataset.color;
        setColor(color);
    });
});

// NEW: Music Sync Toggle CHECKBOX Listener
document.getElementById('btn-sync').addEventListener('change', handleSyncToggle);

// --- UI UPDATE FUNCTIONS ---

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

// --- API FUNCTIONS ---

async function setPower(state) {
    try {
        const response = await fetch(`${API_BASE}/api/power`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({state})
        });
        const data = await response.json();
        if (data.success) {
            updateStatus();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Connection error: ' + error);
    }
}

async function setColor(color, brightness = 100) {
    try {
        const response = await fetch(`${API_BASE}/api/color`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                type: 'hex',
                value: color,
                brightness: parseInt(brightness)
            })
        });
        const data = await response.json();
        if (!data.success) {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Connection error: ' + error);
    }
}

async function runEffect(effectName) {
    try {
        const response = await fetch(`${API_BASE}/api/effect`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                name: effectName,
                duration: 30
            })
        });
        const data = await response.json();
        if (!data.success) {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Connection error: ' + error);
    }
}

/**
 * NEW: API call to toggle the Music Sync state (DPS 21/25/27 sequence).
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
            // Must force UI update to show the mismatch with the device state
            updateStatus(); 
        }
    } catch (error) {
        alert('Connection error during sync toggle: ' + error);
        // Must force UI update to show the mismatch with the device state
        updateStatus();
    }
}

/**
 * NEW: Handles the change event for the Sync checkbox.
 */
function handleSyncToggle(event) {
    const targetState = event.target.checked ? 'on' : 'off';
    
    // We update the device state immediately, and updateStatus() will confirm
    // whether the device accepted the state change (i.e., if mode became 'music').
    syncToggle(targetState);
}


async function updateStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const data = await response.json();
        
        if (data.success && data.status) {
            const dps = data.status;
            
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

async function loadEffects() {
    try {
        const response = await fetch(`${API_BASE}/api/effects`);
        const data = await response.json();
        if (data.success) {
            const container = document.getElementById('effects-container');
            container.innerHTML = '';
            // Filter out 'sync' from the effects list as it has its own dedicated button
            data.effects.filter(effect => effect !== 'sync').forEach(effect => {
                const btn = document.createElement('button');
                btn.className = 'effect-btn';
                btn.textContent = effect.replace('_', ' ').toUpperCase();
                btn.addEventListener('click', () => runEffect(effect));
                container.appendChild(btn);
            });
        }
    } catch (error) {
        console.error('Error loading effects:', error);
    }
}

// Initialize
loadEffects();
updateStatus();
setInterval(updateStatus, 5000); // Update status every 5 seconds