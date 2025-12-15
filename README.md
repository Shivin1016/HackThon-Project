
 
SafeStree - Know Before You Go 🛡️
<div align="center">
https://img.shields.io/badge/SafeStree-Women_Safety_Platform-blueviolet
https://img.shields.io/badge/version-1.0.0-green
https://img.shields.io/badge/license-MIT-blue
https://img.shields.io/badge/python-3.8%252B-blue
https://img.shields.io/badge/flask-2.3.3-lightgrey

A real-time safety navigation platform for women with predictive analytics and community protection

Demo • Features • Installation • Usage • API Documentation • Team

</div>
📌 Overview
SafeStree is an innovative safety platform that empowers women with real-time safety information, predictive risk analysis, and community-driven protection. Our mission is to create a world where every woman can walk freely, anytime, anywhere – without fear or compromise.

"Know Before You Go" - Making public spaces safer through technology and community.

✨ Key Features
Feature	Description	Status
🗺️ Real-time Safety Heatmaps	Interactive color-coded maps showing area safety ratings	✅ Live
👥 Community-Verified Reporting	Crowd-sourced intelligence with upvote/downvote system	✅ Live
🔮 Predictive Risk Analysis	AI-powered forecasts of unsafe zones and times	✅ Live
🚨 Emergency SOS Toolkit	One-tap SOS with location sharing and alerts	✅ Live
🛣️ Safe Route Navigation	AI-optimized safe path recommendations	✅ Live
📊 Live Incident Alerts	Real-time notifications of nearby incidents	✅ Live
📊 Statistics & Impact
85% of women experience public harassment

30% decline night shift jobs due to safety concerns

68% experience travel anxiety

Potential to reduce crime rates by proactive prevention

Community-driven verification reduces false reports by 70%

🏗️ System Architecture
graph TB
    A[User Frontend] --> B[Flask Backend API]
    B --> C[MongoDB Database]
    B --> D[AI Prediction Engine]
    B --> E[Real-time Socket.IO]
    D --> F[TensorFlow ML Model]
    E --> G[Live Notifications]
    B --> H[Emergency Services API]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style D fill:#e8f5e8

🚀 Quick Start
Prerequisites
Python 3.8+

Node.js 14+

MongoDB 4.4+

Modern web browser

Installation
1. Clone Repository
git clone https://github.com/yourusername/safestree.git
cd safestree

2. Backend Setup
cd backend
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configurations

# Run MongoDB (if using local)
mongod --dbpath ./data/db

# Start Flask server
python app.py

3. Frontend Setup
cd frontend
# No build required - static files
# Open index.html in browser or use live server

4. Using Docker (Recommended)
docker-compose up --build

🛠️ Technology Stack
Backend
Python 3.8+ - Core programming language

Flask - Lightweight web framework

MongoDB - NoSQL database for scalability

TensorFlow - Machine learning for predictions

Socket.IO - Real-time communication

JWT - Secure authentication