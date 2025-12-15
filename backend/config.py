import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Config
    SECRET_KEY = os.getenv('SECRET_KEY', 'safestree-secret-key-2024')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    
    # MongoDB Config
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/safestree')
    
    # Emergency Services Config
    POLICE_API_KEY = os.getenv('POLICE_API_KEY', '')
    AMBULANCE_API_KEY = os.getenv('AMBULANCE_API_KEY', '')
    
    # SMS Service (for emergency alerts)
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '')
    
    # Map API Keys
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')
    
    # Security
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Rate Limiting
    RATE_LIMIT = os.getenv('RATE_LIMIT', '100 per minute')
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads/'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'mov'}