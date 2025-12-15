from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime
import json
import os
from predict import predict_risk
from models import Report, User, SafetyZone

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory storage (use MongoDB in production)
reports = []
users = []
heatmap_data = []

# Emergency contacts
EMERGENCY_CONTACTS = {
    "police": "100",
    "ambulance": "102",
    "women_helpline": "1091",
    "national_emergency": "112"
}

@app.route('/')
def home():
    return jsonify({
        "message": "SafeStree API",
        "version": "1.0",
        "endpoints": {
            "report_incident": "/api/report",
            "get_heatmap": "/api/heatmap",
            "predict_risk": "/api/predict",
            "emergency": "/api/emergency"
        }
    })

@app.route('/api/report', methods=['POST'])
def report_incident():
    """Submit a safety incident report"""
    try:
        data = request.json
        report = {
            "id": len(reports) + 1,
            "user_id": data.get('user_id'),
            "latitude": float(data.get('latitude')),
            "longitude": float(data.get('longitude')),
            "incident_type": data.get('type', 'harassment'),
            "severity": int(data.get('severity', 3)),
            "description": data.get('description', ''),
            "timestamp": datetime.now().isoformat(),
            "verified": False,
            "upvotes": 0,
            "downvotes": 0,
            "status": "pending"
        }
        
        reports.append(report)
        
        # Broadcast to all connected clients
        socketio.emit('new_report', report)
        
        # Update heatmap
        update_heatmap(report)
        
        return jsonify({
            "success": True,
            "message": "Report submitted successfully",
            "report_id": report["id"]
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@app.route('/api/heatmap', methods=['GET'])
def get_heatmap():
    """Get safety heatmap data"""
    lat = request.args.get('lat', default=28.6139, type=float)  # Default: Delhi
    lng = request.args.get('lng', default=77.2090, type=float)
    radius = request.args.get('radius', default=5, type=float)  # 5km radius
    
    # Filter reports within radius
    nearby_reports = []
    for report in reports:
        # Simple distance calculation (use geopy in production)
        if abs(report['latitude'] - lat) < 0.1 and abs(report['longitude'] - lng) < 0.1:
            nearby_reports.append(report)
    
    # Generate heatmap points
    heatmap_points = []
    for report in nearby_reports[:50]:  # Limit points
        heatmap_points.append({
            "lat": report['latitude'],
            "lng": report['longitude'],
            "weight": report['severity'] * 10,
            "type": report['incident_type']
        })
    
    # Calculate safety score (1-100)
    safety_score = calculate_safety_score(nearby_reports)
    
    return jsonify({
        "center": {"lat": lat, "lng": lng},
        "radius_km": radius,
        "heatmap_data": heatmap_points,
        "safety_score": safety_score,
        "total_reports": len(nearby_reports),
        "last_updated": datetime.now().isoformat()
    })

@app.route('/api/predict', methods=['POST'])
def predict_safety():
    """Predict safety risk for a location"""
    data = request.json
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    time_of_day = data.get('time_of_day', datetime.now().hour)
    
    # Get historical data for location
    location_history = get_location_history(latitude, longitude)
    
    # Use ML model for prediction
    risk_score, risk_level, suggestions = predict_risk(
        latitude, longitude, 
        time_of_day, 
        location_history
    )
    
    return jsonify({
        "risk_score": risk_score,
        "risk_level": risk_level,
        "safety_color": get_safety_color(risk_score),
        "suggestions": suggestions,
        "prediction_time": datetime.now().isoformat()
    })

@app.route('/api/emergency/sos', methods=['POST'])
def emergency_sos():
    """Trigger SOS emergency"""
    data = request.json
    user_id = data.get('user_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    # In production: Send SMS/email to emergency contacts
    # and notify nearby SafeStree users
    
    emergency_data = {
        "user_id": user_id,
        "location": {"lat": latitude, "lng": longitude},
        "timestamp": datetime.now().isoformat(),
        "status": "active",
        "emergency_contacts_notified": list(EMERGENCY_CONTACTS.values())[:2]
    }
    
    # Broadcast emergency
    socketio.emit('emergency_alert', emergency_data)
    
    return jsonify({
        "success": True,
        "message": "SOS activated! Help is on the way.",
        "contacts_notified": emergency_data["emergency_contacts_notified"]
    })

@app.route('/api/emergency/contacts', methods=['GET'])
def get_emergency_contacts():
    """Get emergency contact numbers"""
    return jsonify(EMERGENCY_CONTACTS)

@app.route('/api/reports/verify', methods=['POST'])
def verify_report():
    """Community verification system"""
    data = request.json
    report_id = data.get('report_id')
    action = data.get('action')  # 'upvote' or 'downvote'
    user_id = data.get('user_id')
    
    report = next((r for r in reports if r["id"] == report_id), None)
    
    if report:
        if action == 'upvote':
            report['upvotes'] += 1
        elif action == 'downvote':
            report['downvotes'] += 1
        
        # Auto-verify if enough upvotes
        if report['upvotes'] >= 5 and report['upvotes'] > report['downvotes'] * 2:
            report['verified'] = True
        
        return jsonify({
            "success": True,
            "upvotes": report['upvotes'],
            "downvotes": report['downvotes'],
            "verified": report['verified']
        })
    
    return jsonify({"success": False, "error": "Report not found"}), 404

@app.route('/api/navigation/safe-route', methods=['POST'])
def get_safe_route():
    """Get safest route between two points"""
    data = request.json
    start_lat = data.get('start_lat')
    start_lng = data.get('start_lng')
    end_lat = data.get('end_lat')
    end_lng = data.get('end_lng')
    
    # In production: Use Google Maps API with safety overlay
    # Here we simulate with a simple path
    
    route_points = generate_safe_route(start_lat, start_lng, end_lat, end_lng)
    
    return jsonify({
        "route": route_points,
        "safety_score": 85,  # Would be calculated
        "estimated_time": "15 mins",
        "distance": "2.5 km",
        "warnings": ["Avoid dark alley near point 3", "Well-lit route recommended"]
    })

def update_heatmap(report):
    """Update heatmap data with new report"""
    heatmap_data.append({
        "lat": report['latitude'],
        "lng": report['longitude'],
        "intensity": report['severity'] * 20,
        "time": datetime.now().isoformat()
    })

def calculate_safety_score(reports_list):
    """Calculate safety score from 1-100"""
    if not reports_list:
        return 100
    
    total_severity = sum(r['severity'] for r in reports_list)
    avg_severity = total_severity / len(reports_list)
    
    # Convert to safety score (higher = safer)
    safety_score = max(0, 100 - (avg_severity * 15))
    return int(safety_score)

def get_safety_color(score):
    """Get color based on safety score"""
    if score >= 80:
        return "green"
    elif score >= 60:
        return "yellow"
    elif score >= 40:
        return "orange"
    else:
        return "red"

def get_location_history(lat, lng):
    """Get historical incident data for location"""
    # This would query database in production
    history = [r for r in reports 
               if abs(r['latitude'] - lat) < 0.01 
               and abs(r['longitude'] - lng) < 0.01]
    return history

def generate_safe_route(start_lat, start_lng, end_lat, end_lng):
    """Generate safe route points (simplified)"""
    # In production, use routing algorithm with safety weights
    return [
        {"lat": start_lat, "lng": start_lng, "safety": 85},
        {"lat": (start_lat + end_lat) / 2, "lng": (start_lng + end_lng) / 2, "safety": 70},
        {"lat": end_lat, "lng": end_lng, "safety": 90}
    ]

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'data': 'Connected to SafeStree'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)

from geocoding import geocoder

@app.route('/api/geocode/reverse', methods=['GET'])
def reverse_geocode():
    """Get place name from coordinates"""
    try:
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        
        if not lat or not lng:
            return jsonify({'error': 'Missing coordinates'}), 400
        
        result = geocoder.reverse_geocode(lat, lng)
        
        return jsonify({
            'success': True,
            'location': {
                'latitude': lat,
                'longitude': lng
            },
            'place_name': result['place_name'],
            'full_address': result['full_address'],
            'source': result['source']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/geocode/forward', methods=['GET'])
def forward_geocode():
    """Get coordinates from place name"""
    try:
        place_name = request.args.get('place', '')
        
        if not place_name:
            return jsonify({'error': 'Missing place name'}), 400
        
        result = geocoder.forward_geocode(place_name)
        
        if result:
            return jsonify({
                'success': True,
                'place_name': place_name,
                'coordinates': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Location not found'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500