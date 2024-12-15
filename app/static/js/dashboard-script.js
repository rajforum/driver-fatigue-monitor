// Initialize charts
const heartRateChart = new Chart(document.getElementById('heartRateChart'), {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Heart Rate',
            borderColor: 'rgb(255, 99, 132)',
            data: []
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false
    }
});

const sleepStagesChart = new Chart(document.getElementById('sleepStagesChart'), {
    type: 'doughnut',
    data: {
        labels: ['Deep', 'Light', 'REM', 'Awake'],
        datasets: [{
            data: [0, 0, 0, 0],
            backgroundColor: [
                'rgb(54, 162, 235)',
                'rgb(75, 192, 192)',
                'rgb(153, 102, 255)',
                'rgb(255, 159, 64)'
            ]
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false
    }
});

const activityChart = new Chart(document.getElementById('activityChart'), {
    type: 'bar',
    data: {
        labels: ['Very Active', 'Fairly Active', 'Lightly Active'],
        datasets: [{
            label: 'Minutes',
            backgroundColor: [
                'rgb(255, 99, 132)',
                'rgb(75, 192, 192)',
                'rgb(255, 205, 86)'
            ],
            data: [0, 0, 0]
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false
    }
});

const alertnessTrendChart = new Chart(document.getElementById('alertnessTrendChart'), {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Alertness Level',
            borderColor: 'rgb(75, 192, 192)',
            fill: true,
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            data: []
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                max: 100,
                title: {
                    display: true,
                    text: 'Alertness Level (%)'
                }
            }
        }
    }
});

const eyeMetricsChart = new Chart(document.getElementById('eyeMetricsChart'), {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Blink Rate',
            borderColor: 'rgb(54, 162, 235)',
            data: [],
            yAxisID: 'blinks'
        }, {
            label: 'Eye Closure Duration',
            borderColor: 'rgb(255, 99, 132)',
            data: [],
            yAxisID: 'duration'
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            blinks: {
                type: 'linear',
                position: 'left',
                title: {
                    display: true,
                    text: 'Blinks per Minute'
                }
            },
            duration: {
                type: 'linear',
                position: 'right',
                title: {
                    display: true,
                    text: 'Closure Duration (s)'
                }
            }
        }
    }
});

const yawnPatternChart = new Chart(document.getElementById('yawnPatternChart'), {
    type: 'bar',
    data: {
        labels: [],
        datasets: [{
            label: 'Yawn Frequency',
            backgroundColor: 'rgb(255, 159, 64)',
            data: []
        }, {
            label: 'Yawn Duration',
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
                    text: 'Count / Duration (s)'
                }
            }
        }
    }
});

const fatigueIndicatorsChart = new Chart(document.getElementById('fatigueIndicatorsChart'), {
    type: 'radar',
    data: {
        labels: ['Alertness', 'Eye Activity', 'Yawning', 'Heart Rate'],
        datasets: [{
            label: 'Current State',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgb(75, 192, 192)',
            data: []
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            r: {
                beginAtZero: true,
                max: 100
            }
        }
    }
});

// Function to update dashboard data
async function updateDashboard() {
    try {
        const [heartRate, sleep, activity, fatigue] = await Promise.all([
            fetch('/api/fatigue/fitness_data').then(r => r.json()),
            fetch('/api/fatigue/sleep_data').then(r => r.json()),
            fetch('/api/fatigue/activity_data').then(r => r.json()),
            fetch('/api/fatigue/analyze_fatigue').then(r => r.json())
        ]);

        // Update Heart Rate
        if (heartRate.bucket && heartRate.bucket[0].dataset) {
            const dataset = heartRate.bucket[0].dataset[0].point;
            const timeLabels = dataset.map((_, index) => {
                // Create time labels based on index (e.g., last 60 minutes)
                const now = new Date();
                now.setMinutes(now.getMinutes() - (dataset.length - index - 1));
                return now.toLocaleTimeString();
            });
            
            heartRateChart.data.labels = timeLabels;
            heartRateChart.data.datasets[0].data = dataset.map(point => point.value[0].fpVal);
            heartRateChart.update();
            
            // Get the latest heart rate value
            const latestHeartRate = dataset[dataset.length - 1].value[0].fpVal;
            document.getElementById('currentHeartRate').textContent = `${latestHeartRate} BPM`;
        }

        // Update Sleep Data
        if (sleep.sleep && sleep.sleep[0]) {
            const sleepData = sleep.sleep[0];
            document.getElementById('sleepAnalysisDate').textContent = sleepData.dateOfSleep;
            document.getElementById('sleepDuration').textContent = 
                `${(sleepData.duration / 3600000).toFixed(1)} hrs`;
            document.getElementById('sleepEfficiency').textContent = 
                `${sleepData.efficiency}%`;
            
            const summary = sleepData.levels.summary;
            sleepStagesChart.data.datasets[0].data = [
                summary.deep.minutes,
                summary.light.minutes,
                summary.rem.minutes,
                summary.wake.minutes
            ];
            sleepStagesChart.update();
        }

        // Update Activity Data
        if (activity.summary) {
            activityChart.data.datasets[0].data = [
                activity.summary.veryActiveMinutes,
                activity.summary.fairlyActiveMinutes,
                activity.summary.lightlyActiveMinutes
            ];
            activityChart.update();
        }

        // Update Fatigue Analysis
        if (fatigue) {
            document.getElementById('fatigueScore').textContent = `${fatigue.score}%`;
            document.getElementById('fatigueStatus').textContent = fatigue.level;
            
            // Update factors
            const factorsDiv = document.getElementById('fatigueFactors');
            factorsDiv.innerHTML = Object.entries(fatigue.factors).slice(0,3)
                .map(([key, factorValue]) => `
                    <div class="flex justify-between">
                        <span class="text-gray-600">${key}</span>
                        <span class="font-medium">${factorValue.value}% | ${factorValue.status}s</span>
                    </div>
                `).join('');
            
            // Update recommendations
            const recsUl = document.getElementById('recommendations');
            recsUl.innerHTML = fatigue.recommendations
                .map(rec => `<li>${rec}</li>`)
                .join('');

            // Update Alertness Trend
            const timeLabel = new Date().toLocaleTimeString();
            
            // Update Alertness Trend
            alertnessTrendChart.data.labels.push(timeLabel);
            alertnessTrendChart.data.datasets[0].data.push(fatigue.score);
            if (alertnessTrendChart.data.labels.length > 20) {
                alertnessTrendChart.data.labels.shift();
                alertnessTrendChart.data.datasets[0].data.shift();
            }
            alertnessTrendChart.update();

            // Update Eye Metrics
            eyeMetricsChart.data.labels.push(timeLabel);
            eyeMetricsChart.data.datasets[0].data.push(fatigue.factors.blink_rate.value);
            eyeMetricsChart.data.datasets[1].data.push(fatigue.factors.eye_closure.value);
            if (eyeMetricsChart.data.labels.length > 20) {
                eyeMetricsChart.data.labels.shift();
                eyeMetricsChart.data.datasets[0].data.shift();
                eyeMetricsChart.data.datasets[1].data.shift();
            }
            eyeMetricsChart.update();

            // Update Yawn Pattern
            yawnPatternChart.data.labels.push(timeLabel);
            yawnPatternChart.data.datasets[0].data.push(fatigue.factors.yawn_count.value);
            // yawnPatternChart.data.datasets[1].data.push(fatigue.factors.yawn_duration.value);
            // if (yawnPatternChart.data.labels.length > 20) {
            //     yawnPatternChart.data.labels.shift();
            //     yawnPatternChart.data.datasets[0].data.shift();
            //     yawnPatternChart.data.datasets[1].data.shift();
            // }
            yawnPatternChart.update();

            // Update Fatigue Indicators
            fatigueIndicatorsChart.data.datasets[0].data = [
                fatigue.score,
                fatigue.factors.eye_closure.score,
                // fatigue.factors.head_position.score,
                fatigue.factors.yawn_count.score,
                heartRate ? parseInt(heartRate) : 70
            ];
            fatigueIndicatorsChart.update();
        }

    } catch (error) {
        console.error('Error updating dashboard:', error);
    }
}

// Initialize dashboard when document is ready
document.addEventListener('DOMContentLoaded', () => {
    // Update dashboard immediately and then every 30 seconds
    updateDashboard();
    setInterval(updateDashboard, 30000);
}); 