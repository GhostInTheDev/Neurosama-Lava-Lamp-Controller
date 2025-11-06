// static/app.js
const API_BASE = '';

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

// API functions
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

async function updateStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const data = await response.json();
        if (data.success) {
            document.getElementById('status').textContent = 
                JSON.stringify(data.status, null, 2);
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
            data.effects.forEach(effect => {
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