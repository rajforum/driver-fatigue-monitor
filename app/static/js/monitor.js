// Initialize Socket.IO
const socket = io();

// DOM Elements
const elements = {
    statusDot: document.getElementById('statusDot'),
    monitorStatus: document.getElementById('monitorStatus'),
    alertStatus: document.getElementById('alertStatus'),
    heartRate: document.getElementById('heartRate'),
    alertness: document.getElementById('alertness'),
    blinkRate: document.getElementById('blinkRate'),
    eyeClosure: document.getElementById('eyeClosure'),
    headPosition: document.getElementById('headPosition'),
    // New metrics card elements
    alertnessCard: document.getElementById('alertnessCard'),
    alertnessStatus: document.getElementById('alertnessStatus'),
    alertnessValue: document.getElementById('alertnessValue'),
    blinkRateValue: document.getElementById('blinkRateValue'),
    eyeClosureValue: document.getElementById('eyeClosureValue'),
    headPositionValue: document.getElementById('headPositionValue'),
    detectionStatusDot: document.getElementById('detectionStatusDot'),
    detectionStatusValue: document.getElementById('detectionStatusValue'),
    lastUpdatedValue: document.getElementById('lastUpdatedValue')
};

// Socket Connection Handlers
socket.on('connect', () => {
    console.log('Connected to server');
    updateConnectionStatus(true);
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
    updateConnectionStatus(false);
});

// Metrics Update Handler
socket.on('metrics_update', (data) => {
    updateMetrics(data);
    updateMetricsCard(data);
});

// Error Handlers
socket.on('metrics_error', (error) => {
    console.error('Metrics error:', error);
    elements.alertStatus.textContent = `Error: ${error.message}`;
    elements.alertStatus.className = 'text-sm text-red-400';
});

socket.on('connect_error', (error) => {
    console.error('Connection error:', error);
    updateConnectionStatus(false);
    elements.monitorStatus.textContent = 'Connection Error';
    elements.detectionStatusValue.textContent = 'Disconnected';
    elements.detectionStatusDot.className = 'h-3 w-3 rounded-full mr-2 bg-gray-500';
});

// Reconnection Handlers
socket.on('reconnect_attempt', () => {
    elements.monitorStatus.textContent = 'Reconnecting...';
});

socket.on('reconnect', () => {
    updateConnectionStatus(true);
});

// Helper Functions
function updateConnectionStatus(isConnected) {
    elements.statusDot.classList.remove(isConnected ? 'bg-red-500' : 'bg-green-500');
    elements.statusDot.classList.add(isConnected ? 'bg-green-500' : 'bg-red-500');
    elements.monitorStatus.textContent = isConnected ? 'Monitoring Active' : 'Disconnected';
}

function updateMetrics(data) {
    if (data.heartRate) {
        elements.heartRate.textContent = `${data.heartRate} BPM`;
    }
    if (data.alertness) {
        elements.alertness.textContent = `${data.alertness}%`;
    }
    if (data.blinkRate) {
        elements.blinkRate.textContent = data.blinkRate;
    }
    if (data.eyeClosure) {
        elements.eyeClosure.textContent = data.eyeClosure;
    }
    if (data.headPosition) {
        elements.headPosition.textContent = data.headPosition;
    }
    if (data.alertStatus) {
        elements.alertStatus.textContent = `Alert Status: ${data.alertStatus}`;
        elements.alertStatus.className = `text-sm ${data.alertStatus.toLowerCase() === 'normal' ? 'text-green-400' : 'text-red-400'}`;
    }
}

function updateMetricsCard(data) {
    // Update Alertness
    elements.alertnessValue.textContent = `${data.alertness}%`;
    elements.alertnessStatus.textContent = data.alertStatus;
    
    // Update status styling
    if (data.alertStatus === 'Normal') {
        elements.alertnessStatus.className = 'px-2 py-1 text-xs rounded-full bg-green-100 text-green-800';
        elements.alertnessCard.className = 'p-4 bg-green-50 rounded-lg';
    } else {
        elements.alertnessStatus.className = 'px-2 py-1 text-xs rounded-full bg-red-100 text-red-800';
        elements.alertnessCard.className = 'p-4 bg-red-50 rounded-lg';
    }

    // Update other metrics
    elements.blinkRateValue.textContent = data.blinkRate;
    elements.eyeClosureValue.textContent = data.eyeClosure;
    elements.headPositionValue.textContent = data.headPosition;
    
    // Update detection status
    elements.detectionStatusDot.className = `h-3 w-3 rounded-full mr-2 ${data.alertStatus === 'Normal' ? 'bg-green-500' : 'bg-red-500'}`;
    
    // Update last updated time
    elements.lastUpdatedValue.textContent = new Date().toLocaleTimeString();
}

// Request metrics update every 5 seconds
setInterval(() => {
    socket.emit('request_metrics');
}, 5000); 