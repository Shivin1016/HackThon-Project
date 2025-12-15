// Configuration
const API_BASE_URL = 'http://localhost:5000';
let socket = null;
let currentLocation = null;
let currentSeverity = 3;

// DOM Elements
const sosBtn = document.getElementById('sosBtn');
const reportModal = document.getElementById('reportModal');
const sosModal = document.getElementById('sosModal');
const alertsContainer = document.getElementById('alertsContainer');

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    // Connect to WebSocket
    connectWebSocket();
    
    // Get user location
    getLocation();
    
    // Load initial data
    loadAlerts();
    loadEmergencyContacts();
    updateStats();
    
    // Setup event listeners
    setupEventListeners();
}

function connectWebSocket() {
    socket = io(API_BASE_URL);
    
    socket.on('connect', () => {
        console.log('Connected to SafeStree server');
        addAlert('Connected to live safety updates', 'info');
    });
    
    socket.on('new_report', (report) => {
        const alertMsg = `New ${report.incident_type} reported nearby`;
        addAlert(alertMsg, 'warning', report);
        updateStats();
    });
    
    socket.on('emergency_alert', (emergency) => {
        const alertMsg = `EMERGENCY SOS triggered nearby!`;
        addAlert(alertMsg, 'emergency', emergency);
        
        // Show notification
        showNotification('Emergency Alert!', {
            body: 'SOS triggered in your area',
            icon: '/icon.png',
            requireInteraction: true
        });
    });
    
    socket.on('disconnect', () => {
        addAlert('Connection lost. Reconnecting...', 'error');
        setTimeout(connectWebSocket, 3000);
    });
}

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                currentLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                updateLocationDisplay();
                updateHeatmap();
            },
            (error) => {
                console.error('Error getting location:', error);
                currentLocation = { lat: 28.6139, lng: 77.2090 }; // Default to Delhi
                updateLocationDisplay();
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    } else {
        alert('Geolocation is not supported by your browser');
        currentLocation = { lat: 28.6139, lng: 77.2090 };
        updateLocationDisplay();
    }
}

function updateLocationDisplay() {
    const locationElement = document.getElementById('currentLocation');
    if (locationElement && currentLocation) {
        locationElement.textContent = 
            `${currentLocation.lat.toFixed(4)}, ${currentLocation.lng.toFixed(4)}`;
    }
}

async function loadAlerts() {
    try {
        // In production, fetch from API
        const mockAlerts = [
            {
                type: 'warning',
                title: 'High Risk Area Detected',
                message: 'Multiple reports near Connaught Place',
                time: '10 mins ago'
            },
            {
                type: 'info',
                title: 'Community Update',
                message: 'New safe zone added: Khan Market area',
                time: '1 hour ago'
            },
            {
                type: 'emergency',
                title: 'Emergency Alert',
                message: 'SOS triggered in South Delhi',
                time: 'Just now'
            }
        ];
        
        alertsContainer.innerHTML = '';
        mockAlerts.forEach(alert => {
            addAlert(alert.message, alert.type, {time: alert.time});
        });
        
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

function addAlert(message, type = 'info', data = {}) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert ${type}`;
    
    const icon = type === 'emergency' ? 'fa-exclamation-triangle' : 
                 type === 'warning' ? 'fa-exclamation-circle' : 'fa-info-circle';
    
    const time = data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : 
                data.time || new Date().toLocaleTimeString();
    
    alertDiv.innerHTML = `
        <i class="fas ${icon}"></i>
        <div class="alert-content">
            <h4>${type.toUpperCase()} ALERT</h4>
            <p>${message}</p>
            <small>${time}</small>
        </div>
    `;
    
    alertsContainer.prepend(alertDiv);
    
    // Auto remove after 30 minutes
    setTimeout(() => {
        alertDiv.remove();
    }, 30 * 60 * 1000);
}

async function loadEmergencyContacts() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/emergency/contacts`);
        const contacts = await response.json();
        
        const contactsElement = document.getElementById('emergencyContacts');
        if (contactsElement) {
            let html = '<h3>Emergency Numbers:</h3>';
            for (const [service, number] of Object.entries(contacts)) {
                html += `
                    <div class="contact-item">
                        <strong>${service.replace('_', ' ').toUpperCase()}:</strong>
                        <a href="tel:${number}">${number}</a>
                    </div>
                `;
            }
            contactsElement.innerHTML = html;
        }
    } catch (error) {
        console.error('Error loading emergency contacts:', error);
    }
}

function updateStats() {
    // Simulate updating statistics
    const stats = {
        communityCount: Math.floor(2500 + Math.random() * 100),
        safeZones: Math.floor(850 + Math.random() * 50),
        incidentsReported: Math.floor(1200 + Math.random() * 30)
    };
    
    Object.keys(stats).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = `${stats[id]}+`;
        }
    });
}

// Modal Functions
function openReportModal() {
    reportModal.style.display = 'flex';
    getLocation();
}

function closeModal() {
    reportModal.style.display = 'none';
    sosModal.style.display = 'none';
}

function rateSeverity(level) {
    currentSeverity = level;
    const stars = document.querySelectorAll('.severity-stars i');
    stars.forEach((star, index) => {
        if (index < level) {
            star.className = 'fas fa-star';
        } else {
            star.className = 'far fa-star';
        }
    });
    document.getElementById('severity').value = level;
}

// Report Submission
document.getElementById('reportForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    if (!currentLocation) {
        alert('Please enable location services');
        return;
    }
    
    const formData = {
        user_id: 'user_' + Math.floor(Math.random() * 1000),
        latitude: currentLocation.lat,
        longitude: currentLocation.lng,
        type: document.getElementById('incidentType').value,
        severity: currentSeverity,
        description: document.getElementById('description').value
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/report`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Report submitted successfully!');
            closeModal();
            document.getElementById('reportForm').reset();
            rateSeverity(3); // Reset to default
        } else {
            alert('Error submitting report: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to submit report. Please try again.');
    }
});

// SOS Functions
sosBtn.addEventListener('click', function() {
    sosModal.style.display = 'flex';
});

function cancelSOS() {
    sosModal.style.display = 'none';
}

async function confirmSOS() {
    if (!currentLocation) {
        alert('Location required for SOS');
        return;
    }
    
    const sosData = {
        user_id: 'user_' + Math.floor(Math.random() * 1000),
        latitude: currentLocation.lat,
        longitude: currentLocation.lng
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/emergency/sos`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(sosData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('EMERGENCY SOS ACTIVATED! Help is on the way.');
            closeModal();
            
            // Start countdown for automatic police notification
            startEmergencyCountdown();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Emergency signal sent to community');
        closeModal();
    }
}

function startEmergencyCountdown() {
    let countdown = 60;
    const countdownElement = document.createElement('div');
    countdownElement.className = 'emergency-countdown';
    countdownElement.innerHTML = `
        <div class="countdown-content">
            <h3><i class="fas fa-siren-on"></i> EMERGENCY ACTIVE</h3>
            <p>Police will be notified in: <span id="countdown">${countdown}</span>s</p>
            <button onclick="cancelEmergency()">CANCEL EMERGENCY</button>
        </div>
    `;
    
    document.body.appendChild(countdownElement);
    
    const countdownInterval = setInterval(() => {
        countdown--;
        document.getElementById('countdown').textContent = countdown;
        
        if (countdown <= 0) {
            clearInterval(countdownInterval);
            notifyPolice();
            countdownElement.remove();
        }
    }, 1000);
    
    window.cancelEmergency = function() {
        clearInterval(countdownInterval);
        countdownElement.remove();
        addAlert('Emergency cancelled', 'info');
    };
}

function notifyPolice() {
    // In production, call actual emergency API
    addAlert('Police have been notified of your emergency', 'emergency');
}

// Other Functions
function checkRouteSafety() {
    if (!currentLocation) {
        alert('Please enable location services first');
        return;
    }
    
    // Simulate route safety check
    const safetyScore = 85 + Math.floor(Math.random() * 15);
    const color = safetyScore >= 80 ? 'green' : 
                  safetyScore >= 60 ? 'yellow' : 
                  safetyScore >= 40 ? 'orange' : 'red';
    
    alert(`Route Safety Score: ${safetyScore}/100\nStatus: ${color.toUpperCase()}\n\nRecommendations:\n• Stay in well-lit areas\n• Avoid shortcuts\n• Share your live location`);
}

function showEmergencyContacts() {
    alert('Emergency Contacts:\n\n🚓 Police: 100\n🏥 Ambulance: 102\n👩 Women Helpline: 1091\n🇮🇳 National Emergency: 112\n\nTap to call any number.');
}

function openSafetyMap() {
    window.location.href = 'maps.html';
}

function updateHeatmap() {
    if (currentLocation) {
        // In production, fetch actual heatmap data
        console.log('Updating heatmap for location:', currentLocation);
    }
}

function showNotification(title, options) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, options);
    } else if (Notification.permission !== 'denied') {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                new Notification(title, options);
            }
        });
    }
}

function setupEventListeners() {
    // Close modal when clicking outside
    window.onclick = function(event) {
        if (event.target === reportModal) {
            reportModal.style.display = 'none';
        }
        if (event.target === sosModal) {
            sosModal.style.display = 'none';
        }
    };
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+Shift+S for SOS
        if (e.ctrlKey && e.shiftKey && e.key === 'S') {
            e.preventDefault();
            sosModal.style.display = 'flex';
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            closeModal();
        }
    });
    
    // Periodic updates
    setInterval(updateStats, 30000); // Update stats every 30 seconds
    setInterval(loadAlerts, 60000); // Refresh alerts every minute
}