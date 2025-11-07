// static/app.js
const API_BASE = '';

// Global state to track sync mode status
let isSyncActive = false;

// --- Helper Functions ---

/**
 * Decodes the raw Tuya HSB/HSV string (HHHHSSSSVVVV) into a standard HEX color string.
 * @param {string} hsvString - Raw color string from DPS 24 (e.g., '010503e803e8')
 * @returns {string} HEX color string (e.g., '#FF0000') or null if invalid.
 */
function tuyaHsvToHex(hsvString) {
    if (!hsvString || hsvString.length < 12) return null;

    try {
        // Extract H, S, V components (4 characters each, hex)
        const h = parseInt(hsvString.substring(0, 4), 16); // 0-360
        const s = parseInt(hsvString.substring(4, 8), 16); // 0-1000
        const v = parseInt(hsvString.substring(8, 12), 16); // 0-1000

        // Convert H (0-360), S (0-1000 -> 0-1), V (0-1000 -> 0-1) to RGB
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

        // Convert 0-1 scale to 0-255, format as hex
        const toHex = (x) => {
            const hex = Math.round(x * 255).toString(16);
            return hex.length === 1 ? '0' + hex : hex;
        };

        const hexR = toHex(r);
        const hexG = toHex(g);
        const hexB = toHex(b);

        return `#${hexR}${hexG}${hexB}`;
    } catch (e) {
        console.error("Failed to decode Tuya HSV string:", e);
        return null;
    }
}


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

// Music Sync Toggle CHECKBOX Listener
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
 * Handles the change event for the Sync checkbox.
 */
function handleSyncToggle(event) {
    const targetState = event.target.checked ? 'on' : 'off';
    syncToggle(targetState);
}


async function updateStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const data = await response.json();
        
        if (data.success && data.status) {
            const dps = data.status;
            
            // --- COLOR PICKER INITIALIZATION/UPDATE ---
            const rawColor = dps['24']; // DPS 24 holds the raw HSB/HSV string
            const hexColor = tuyaHsvToHex(rawColor);
            
            if (hexColor) {
                const colorPicker = document.getElementById('color-picker');
                
                // Only update the picker if it's currently showing a different color
                // to avoid interfering with user interaction.
                if (colorPicker.value.toUpperCase() !== hexColor.toUpperCase()) {
                    colorPicker.value = hexColor;
                }
            }
            // ----------------------------------------

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