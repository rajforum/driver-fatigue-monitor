// Session variables
let sessionStartTime = new Date();
let alertCount = 0;
let alertnessValues = [];

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
    sessionTime: document.getElementById('sessionTime'),
    fpsCounter: document.getElementById('fpsCounter'),
    processingTime: document.getElementById('processingTime'),
    alertHistory: document.getElementById('alertHistory'),
    sessionDuration: document.getElementById('sessionDuration'),
    alertCount: document.getElementById('alertCount'),
    avgAlertness: document.getElementById('avgAlertness'),
    avgHeartRate: document.getElementById('avgHeartRate'),
    alertnessTrend: document.getElementById('alertnessTrend'),
    headPositionDetails: document.getElementById('headPositionDetails'),
    detectionDetails: document.getElementById('detectionDetails'),
    lastUpdateTime: document.getElementById('lastUpdateTime'),
    yawnRateValue: document.getElementById('yawnRateValue'),
};

// Update session time
function updateSessionTime() {
    const now = new Date();
    const diff = now - sessionStartTime;
    const hours = Math.floor(diff / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    elements.sessionTime.textContent = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    // elements.sessionDuration.textContent = elements.sessionTime.textContent.replace('Session Time: ', '');
}

// Update metrics display
function updateMetricsDisplay(data) {
    // Update all metrics
    if (data.heartRate) {
        elements.heartRate.textContent = `${data.heartRate} BPM`;
        elements.heartRate.className = 'text-2xl font-bold text-gray-800';
    }

    if (data.alertness) {
        elements.alertness.textContent = `${data.alertness}%`;
        elements.alertnessValue.textContent = `${data.alertness}%`;
        alertnessValues.push(parseFloat(data.alertness));
        updateAlertnessStatistics();
    }

    if (data.blinkRate) {
        elements.blinkRateValue.textContent = data.blinkRate;
        elements.blinkRateValue.className = 'text-2xl font-bold text-gray-800';
    }

    if (data.eyeClosure) {
        elements.eyeClosureValue.textContent = data.eyeClosure.replace('s', '');
        elements.eyeClosureValue.className = 'text-2xl font-bold text-gray-800';
    }

    if (data.headPosition) {
        elements.headPositionValue.textContent = data.headPosition;
        elements.headPositionValue.className = 'text-2xl font-bold text-gray-800';
        updateHeadPositionDetails(data.headPosition);
    }

    if (data.yawnCount) {
        elements.yawnRateValue.textContent = data.yawnCount;
        elements.yawnRateValue.className = 'text-2xl font-bold text-gray-800';
    }

    // Update last update time
    elements.lastUpdateTime.textContent = new Date().toLocaleTimeString();

    // Update detection status
    updateDetectionStatus(data);
}

// Update alertness statistics
function updateAlertnessStatistics() {
    if (alertnessValues.length > 0) {
        const avg = alertnessValues.reduce((a, b) => a + b) / alertnessValues.length;
        elements.avgAlertness.textContent = `${avg.toFixed(1)}%`;

        // Calculate trend
        const recentValues = alertnessValues.slice(-5);
        if (recentValues.length >= 2) {
            const trend = recentValues[recentValues.length - 1] - recentValues[0];
            elements.alertnessTrend.textContent = trend > 0 ? '↑ Improving' : trend < 0 ? '↓ Declining' : '→ Stable';
            elements.alertnessTrend.className = `text-xs ${trend > 0 ? 'text-green-500' : trend < 0 ? 'text-red-500' : 'text-gray-500'}`;
        }
    }
}

// Add alert to history
function addAlertToHistory(alert) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `p-2 rounded ${alert.level === 'danger' ? 'bg-red-100' : 'bg-yellow-100'}`;
    alertDiv.innerHTML = `
        <div class="flex justify-between items-center">
            <span class="text-sm font-medium">${alert.message}</span>
            <span class="text-xs text-gray-500">${new Date(alert.timestamp).toLocaleTimeString()}</span>
        </div>
    `;
    elements.alertHistory.insertBefore(alertDiv, elements.alertHistory.firstChild);
    if (elements.alertHistory.children.length > 5) {
        elements.alertHistory.removeChild(elements.alertHistory.lastChild);
    }
    alertCount++;
    elements.alertCount.textContent = alertCount;
}

// Add Connection Status Banner
function showReconnectionError() {
    const monitorStatus = document.getElementById('monitorStatus');
    const statusDot = document.getElementById('statusDot');
    
    if (monitorStatus) {
        monitorStatus.textContent = 'Connection Failed - Please Refresh';
        monitorStatus.className = 'text-red-600 font-bold';
    }
    
    if (statusDot) {
        statusDot.className = 'h-3 w-3 bg-red-500 rounded-full';
    }
    
    // Show a user-friendly error message
    const alertDiv = document.createElement('div');
    alertDiv.className = 'fixed top-4 left-1/2 transform -translate-x-1/2 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded shadow-lg z-50';
    alertDiv.innerHTML = `
        <div class="text-center">
            <strong class="font-bold block mb-1">Connection Lost!</strong>
            <span class="block mb-2">Unable to reconnect to server. Please refresh the page.</span>
            <button onclick="location.reload()" 
                    class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition-colors duration-200">
                Refresh Page
            </button>
        </div>
    `;
    document.body.appendChild(alertDiv);
}

// Start updating session time
setInterval(updateSessionTime, 1000);

// Initialize
updateSessionTime();

// Add these functions to monitor.js
function updateDetectionStatus(data) {
    // Update detection status and details
    const statusDot = elements.detectionStatusDot;
    const statusValue = elements.detectionStatusValue;
    const details = elements.detectionDetails;

    if (data.isDetecting) {
        statusDot.className = 'h-3 w-3 rounded-full mr-2 bg-green-500';
        statusValue.textContent = 'Active';
        statusValue.className = 'text-lg font-bold text-green-600';
        
        // Update eye state in details
        if (data.eyeState) {
            const eyeStateText = data.eyeState === 'closed' ? 'Eyes Closed!' : 'Eyes Open';
            const eyeStateColor = data.eyeState === 'closed' ? 'text-red-500' : 'text-green-500';
            details.innerHTML = `Face Detected - <span class="${eyeStateColor} font-medium">${eyeStateText}</span>`;
        }
    } else {
        statusDot.className = 'h-3 w-3 rounded-full mr-2 bg-red-500';
        statusValue.textContent = 'No Face Detected';
        statusValue.className = 'text-lg font-bold text-red-600';
        details.textContent = 'Searching for face...';
    }
}

function updateHeadPositionDetails(position) {
    const details = elements.headPositionDetails;
    const positionMessages = {
        'Centered': 'Proper driving position',
        'Left': 'Head turned left',
        'Right': 'Head turned right',
        'Up': 'Looking up',
        'Down': 'Looking down - Warning!'
    };

    const positionColors = {
        'Centered': 'text-green-500',
        'Left': 'text-yellow-500',
        'Right': 'text-yellow-500',
        'Up': 'text-yellow-500',
        'Down': 'text-red-500'
    };

    details.textContent = positionMessages[position] || 'Unknown position';
    details.className = `text-xs ${positionColors[position] || 'text-gray-500'}`;
}

function handleAlert(data) {
    const { level, message } = data;
    
    // Update alert status
    elements.alertStatus.textContent = `Alert Status: ${level.toUpperCase()}`;
    elements.alertStatus.className = `text-sm ${level === 'normal' ? 'text-green-400' : 'text-red-400'}`;

    // Update alertness card
    const alertnessCard = elements.alertnessCard;
    const alertnessStatus = elements.alertnessStatus;

    const colors = {
        normal: {
            card: 'bg-green-50',
            status: 'bg-green-100 text-green-800'
        },
        warning: {
            card: 'bg-yellow-50',
            status: 'bg-yellow-100 text-yellow-800'
        },
        danger: {
            card: 'bg-red-50',
            status: 'bg-red-100 text-red-800'
        }
    };

    const currentColors = colors[level] || colors.normal;
    alertnessCard.className = `p-4 rounded-lg ${currentColors.card}`;
    alertnessStatus.className = `px-2 py-1 text-xs rounded-full ${currentColors.status}`;
    alertnessStatus.textContent = level.toUpperCase();

    // Play alert sound for warning and danger
    if (level !== 'normal') {
        playAlertSound();
        showNotification("Driver Fatigue Alert", message);
    }
}

function playAlertSound() {
    try {
        const audio = new Audio('/static/audio/alert.mp3');
        audio.play();
    } catch (error) {
        console.error('Error playing alert sound:', error);
    }
}

function showNotification(title, message) {
    if (Notification.permission === "granted") {
        new Notification(title, {
            body: message,
            icon: "/static/img/alert-icon.png"
        });
    } else if (Notification.permission !== "denied") {
        Notification.requestPermission().then(permission => {
            if (permission === "granted") {
                showNotification(title, message);
            }
        });
    }
}

// Add performance metrics update
function updatePerformanceMetrics(data) {
    if (data.fps) {
        elements.fpsCounter.textContent = Math.round(data.fps);
    }
    if (data.processingTime) {
        elements.processingTime.textContent = Math.round(data.processingTime);
    }
}

// Chart configurations
const chartConfigs = {
    alertness: {
        chart: null,
        config: {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Alertness Level',
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1,
                    data: []
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        }
    },
    heartRate: {
        chart: null,
        config: {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Heart Rate (BPM)',
                    borderColor: 'rgb(255, 99, 132)',
                    tension: 0.1,
                    data: []
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        }
    },
    blinkRate: {
        chart: null,
        config: {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Blink Rate',
                    backgroundColor: 'rgb(153, 102, 255)',
                    data: []
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Blinks per minute'
                        }
                    }
                }
            }
        }
    },
    eyeClosure: {
        chart: null,
        config: {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Eye Closure Duration',
                    backgroundColor: 'rgb(255, 159, 64)',
                    data: []
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Duration (seconds)'
                        }
                    }
                }
            }
        }
    }
};

// Initialize charts
function initializeCharts() {
    chartConfigs.alertness.chart = new Chart(
        document.getElementById('alertnessChart'),
        chartConfigs.alertness.config
    );
    
    chartConfigs.heartRate.chart = new Chart(
        document.getElementById('heartRateChart'),
        chartConfigs.heartRate.config
    );
}

// Update charts with new data
function updateCharts(trendData) {
    const { labels, datasets } = trendData;
    
    // Update existing charts
    chartConfigs.alertness.chart.data.labels = labels;
    chartConfigs.alertness.chart.data.datasets[0].data = datasets.alertness;
    chartConfigs.alertness.chart.update();
    
    chartConfigs.heartRate.chart.data.labels = labels;
    chartConfigs.heartRate.chart.data.datasets[0].data = datasets.heartRate;
    chartConfigs.heartRate.chart.update();

    // Update blink rate bar chart
    chartConfigs.blinkRate.chart.data.labels = labels;
    chartConfigs.blinkRate.chart.data.datasets[0].data = datasets.blinkRate;
    chartConfigs.blinkRate.chart.update();

    // Update eye closure scatter plot
    chartConfigs.eyeClosure.chart.data.datasets[0].data = labels.map((label, i) => ({
        x: label,
        y: datasets.eyeClosure[i]
    }));
    chartConfigs.eyeClosure.chart.update();
}

// Initialize charts when document is ready
document.addEventListener('DOMContentLoaded', () => {
    initializeCharts();
    socket.emit('request_trends');
});

// Add trend analysis display
function updateTrendAnalysis(analysis) {
    const trendSummary = document.getElementById('trendSummary');
    const fatigueScore = document.getElementById('fatigueScore');
    
    // Update trend summary
    if (trendSummary) {
        trendSummary.textContent = analysis.summary;
        trendSummary.className = `text-sm ${analysis.fatigue_score.level === 'normal' ? 'text-green-600' : 'text-red-600'}`;
    }

    // Update fatigue score
    if (fatigueScore) {
        fatigueScore.textContent = `${analysis.fatigue_score.score}%`;
        fatigueScore.className = `text-2xl font-bold ${
            analysis.fatigue_score.level === 'normal' ? 'text-green-600' : 
            analysis.fatigue_score.level === 'moderate' ? 'text-yellow-600' : 
            'text-red-600'
        }`;
    }
}

// Add this function near the top with other utility functions
function updateConnectionStatus(isConnected) {
    const statusDot = elements.statusDot;
    const monitorStatus = elements.monitorStatus;

    if (isConnected) {
        statusDot.className = 'h-3 w-3 bg-green-500 rounded-full';
        monitorStatus.textContent = 'Connected';
        monitorStatus.className = 'text-green-600';
        
        // Request initial metrics
        socket.emit('request_metrics');
        socket.emit('request_trends');
    } else {
        statusDot.className = 'h-3 w-3 bg-red-500 rounded-full';
        monitorStatus.textContent = 'Disconnected';
        monitorStatus.className = 'text-red-600';
        
        // Update UI elements to show disconnected state
        elements.alertStatus.textContent = 'Connection Lost';
        elements.alertStatus.className = 'text-sm text-red-400';
        
        // Update detection status
        if (elements.detectionStatusDot && elements.detectionStatusValue) {
            elements.detectionStatusDot.className = 'h-3 w-3 rounded-full mr-2 bg-gray-500';
            elements.detectionStatusValue.textContent = 'Connection Lost';
            elements.detectionStatusValue.className = 'text-lg font-bold text-gray-600';
            elements.detectionDetails.textContent = 'Waiting for connection...';
        }
    }
}