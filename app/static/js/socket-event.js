// Initialize Socket.IO with reconnection options
const socket = io({
    path: '/socket.io',
    reconnection: true,           // Enable reconnection
    reconnectionAttempts: 10,     // Maximum number of reconnection attempts
    reconnectionDelay: 1000,      // How long to wait before attempting a new reconnection (1 second)
    reconnectionDelayMax: 5000,   // Maximum amount of time to wait between reconnections (5 seconds)
    timeout: 10000,              // Connection timeout before a connect_error event is emitted
    autoConnect: true            // Automatically connect upon creation
});

// Track connection state
let isConnected = false;
let reconnectAttempts = 0;


// Connection event handlers
socket.on('connect', () => {
    console.log('Connected to server');
    isConnected = true;
    reconnectAttempts = 0;
    updateConnectionStatus(true);
    
    // Request initial data after connection
    requestInitialData();
});

socket.on('disconnect', (reason) => {
    console.log('Disconnected from server:', reason);
    isConnected = false;
    updateConnectionStatus(false);
    
    // If the disconnection wasn't initiated by the client, try to reconnect
    if (reason === 'io server disconnect') {
        // The disconnection was initiated by the server, so manually reconnect
        socket.connect();
    }
    // Otherwise, the socket will automatically try to reconnect
});

socket.on('connect_error', (error) => {
    console.log('Connection error:', error);
    updateConnectionStatus(false);
    reconnectAttempts++;
    
    if (reconnectAttempts >= 10) {
        console.log('Maximum reconnection attempts reached');
        showReconnectionError();
    }
});

socket.on('reconnecting', (attemptNumber) => {
    console.log('Attempting to reconnect...', attemptNumber);
    const monitorStatus = document.getElementById('monitorStatus');
    if (monitorStatus) {
        monitorStatus.textContent = `Reconnecting (Attempt ${attemptNumber})...`;
        monitorStatus.className = 'text-yellow-600';
    }
});

socket.on('reconnect', (attemptNumber) => {
    console.log('Reconnected after', attemptNumber, 'attempts');
    isConnected = true;
    reconnectAttempts = 0;
    updateConnectionStatus(true);
    requestInitialData();
});

socket.on('reconnect_error', (error) => {
    console.log('Reconnection error:', error);
    showReconnectionError();
});

socket.on('reconnect_failed', () => {
    console.log('Failed to reconnect');
    showReconnectionError();
});


// Helper functions
function requestInitialData() {
    // Request all necessary data after connection/reconnection
    socket.emit('request_metrics');
    socket.emit('request_trends');
}


// Add a manual reconnect function
function manualReconnect() {
    if (!isConnected) {
        socket.connect();
    }
}

// Add a heartbeat to check connection
setInterval(() => {
    if (isConnected) {
        socket.emit('ping');
    }
}, 30000); // Every 30 seconds

// Handle heartbeat response
socket.on('pong', () => {
    console.log('Heartbeat received');
});

// Socket event handlers
socket.on('metrics_update', (data) => {
    updateMetricsDisplay(data);
    updatePerformanceMetrics(data);
});

socket.on('alert', (data) => {
    handleAlert(data);
    addAlertToHistory(data);
});


// Request metrics update every 5 seconds
setInterval(() => {
    socket.emit('request_metrics');
}, 3000);


// Socket event for trends
socket.on('trends_update', (data) => {
    updateCharts(data);
});

// Request trends update every 4 seconds
setInterval(() => {
    socket.emit('request_trends');
}, 4000);

// Add socket event for trend analysis
socket.on('trend_analysis', (data) => {
    updateTrendAnalysis(data);
});