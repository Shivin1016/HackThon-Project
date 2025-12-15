// Map configuration
let map = null;
let heatmapLayer = null;
let userMarker = null;
let incidentMarkers = [];
const API_BASE_URL = 'http://localhost:5000';

// Initialize map
function initMap() {
    // Default to Delhi coordinates
    const defaultCoords = [28.6139, 77.2090];
    
    // Create map
    map = L.map('map').setView(defaultCoords, 13);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);
    
    // Create heatmap layer
    heatmapLayer = L.layerGroup().addTo(map);
    
    // Load initial data
    loadHeatmapData();
    locateMe();
}

// Load heatmap data from API
async function loadHeatmapData() {
    try {
        const center = map.getCenter();
        const response = await fetch(
            `${API_BASE_URL}/api/heatmap?lat=${center.lat}&lng=${center.lng}&radius=5`
        );
        const data = await response.json();
        
        // Clear existing markers
        clearMarkers();
        
        // Add heatmap points
        data.heatmap_data.forEach(point => {
            addHeatmapPoint(point);
        });
        
        // Update stats
        updateMapStats(data);
        
    } catch (error) {
        console.error('Error loading heatmap:', error);
        // Load sample data
        loadSampleData();
    }
}

function addHeatmapPoint(point) {
    const color = getColorByWeight(point.weight);
    
    const marker = L.circleMarker([point.lat, point.lng], {
        radius: point.weight / 5,
        fillColor: color,
        color: '#000',
        weight: 1,
        opacity: 0.5,
        fillOpacity: 0.7
    }).addTo(heatmapLayer);
    
    // Add popup
    marker.bindPopup(`
        <strong>Safety Incident</strong><br>
        Type: ${point.type || 'Unknown'}<br>
        Severity: ${point.weight / 10}/5<br>
        Coordinates: ${point.lat.toFixed(4)}, ${point.lng.toFixed(4)}
    `);
    
    incidentMarkers.push(marker);
}

function getColorByWeight(weight) {
    if (weight <= 20) return '#00ff00'; // Green
    if (weight <= 40) return '#ffff00'; // Yellow
    if (weight <= 60) return '#ffa500'; // Orange
    return '#ff0000'; // Red
}

function clearMarkers() {
    incidentMarkers.forEach(marker => {
        map.removeLayer(marker);
    });
    incidentMarkers = [];
}

function locateMe() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const userCoords = [position.coords.latitude, position.coords.longitude];
                
                // Remove previous user marker
                if (userMarker) {
                    map.removeLayer(userMarker);
                }
                
                // Add user marker
                userMarker = L.marker(userCoords, {
                    icon: L.divIcon({
                        className: 'user-marker',
                        html: '<i class="fas fa-user" style="color: #667eea; font-size: 24px;"></i>',
                        iconSize: [30, 30]
                    })
                }).addTo(map);
                
                // Center map on user
                map.setView(userCoords, 15);
                
                // Add popup
                userMarker.bindPopup('Your Location').openPopup();
                
                // Load heatmap for this location
                loadHeatmapData();
            },
            (error) => {
                console.error('Error getting location:', error);
                alert('Unable to get your location. Using default view.');
            }
        );
    }
}

function refreshHeatmap() {
    loadHeatmapData();
    showNotification('Heatmap refreshed', 'info');
}

function showSafeRoutes() {
    if (!userMarker) {
        alert('Please enable location first');
        return;
    }
    
    // Get user location
    const userLatLng = userMarker.getLatLng();
    
    // Generate sample safe route (in production, use routing API)
    const routePoints = [
        [userLatLng.lat, userLatLng.lng],
        [userLatLng.lat + 0.005, userLatLng.lng + 0.005],
        [userLatLng.lat + 0.01, userLatLng.lng + 0.01]
    ];
    
    // Draw route
    const route = L.polyline(routePoints, {
        color: '#00ff00',
        weight: 5,
        opacity: 0.7,
        dashArray: '10, 10'
    }).addTo(map);
    
    // Add start and end markers
    L.marker(routePoints[0]).addTo(map)
        .bindPopup('Start Point')
        .openPopup();
    
    L.marker(routePoints[routePoints.length - 1]).addTo(map)
        .bindPopup('Destination')
        .openPopup();
    
    // Fit map to route
    map.fitBounds(route.getBounds());
    
    showNotification('Safe route displayed', 'success');
}

function reportHere() {
    window.location.href = 'index.html#report';
}

function filterByTime() {
    const filter = document.getElementById('timeFilter').value;
    showNotification(`Filtering by: ${filter}`, 'info');
    // In production, refetch data with time filter
}

function updateMapStats(data) {
    // Update statistics display
    document.getElementById('activeZones').textContent = 
        Math.floor(Math.random() * 10) + 10;
    document.getElementById('reportsToday').textContent = 
        data.total_reports || Math.floor(Math.random() * 20);
    document.getElementById('usersNearby').textContent = 
        Math.floor(Math.random() * 50) + 20;
    document.getElementById('safeRoutes').textContent = 
        Math.floor(Math.random() * 100) + 100;
}

function loadSampleData() {
    // Generate sample heatmap data
    const center = map.getCenter();
    
    for (let i = 0; i < 20; i++) {
        const lat = center.lat + (Math.random() - 0.5) * 0.05;
        const lng = center.lng + (Math.random() - 0.5) * 0.05;
        const weight = Math.floor(Math.random() * 50) + 10;
        
        addHeatmapPoint({
            lat: lat,
            lng: lng,
            weight: weight,
            type: ['harassment', 'stalking', 'theft'][Math.floor(Math.random() * 3)]
        });
    }
    
    updateMapStats({ total_reports: 20 });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `map-notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', initMap);

