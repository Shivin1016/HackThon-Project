from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
        self.db = self.client['safestree_db']
        
        # Collections
        self.reports = self.db['reports']
        self.users = self.db['users']
        self.safety_zones = self.db['safety_zones']
        self.emergency_logs = self.db['emergency_logs']
        
        # Create indexes
        self.create_indexes()
    
    def create_indexes(self):
        """Create database indexes for performance"""
        # Geospatial index for location-based queries
        self.reports.create_index([("location", "2dsphere")])
        self.safety_zones.create_index([("location", "2dsphere")])
        
        # Other indexes
        self.reports.create_index([("timestamp", -1)])
        self.reports.create_index([("verified", 1)])
        self.users.create_index([("email", 1)], unique=True)
    
    def add_report(self, report_data):
        """Add a new incident report"""
        report_data['created_at'] = datetime.now()
        report_data['updated_at'] = datetime.now()
        result = self.reports.insert_one(report_data)
        return str(result.inserted_id)
    
    def get_nearby_reports(self, latitude, longitude, radius_km=5, limit=100):
        """Get reports within radius of given coordinates"""
        query = {
            "location": {
                "$nearSphere": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "$maxDistance": radius_km * 1000  # Convert km to meters
                }
            }
        }
        
        reports = list(self.reports.find(query).limit(limit))
        
        # Convert ObjectId to string
        for report in reports:
            report['_id'] = str(report['_id'])
        
        return reports
    
    def update_report_votes(self, report_id, action, user_id):
        """Update votes for a report"""
        update_field = "upvotes" if action == "upvote" else "downvotes"
        
        result = self.reports.update_one(
            {"_id": report_id},
            {"$inc": {update_field: 1}}
        )
        
        # Check if report should be auto-verified
        if self.should_auto_verify(report_id):
            self.reports.update_one(
                {"_id": report_id},
                {"$set": {"verified": True}}
            )
        
        return result.modified_count > 0
    
    def should_auto_verify(self, report_id):
        """Check if report should be auto-verified based on votes"""
        report = self.reports.find_one({"_id": report_id})
        
        if not report:
            return False
        
        upvotes = report.get('upvotes', 0)
        downvotes = report.get('downvotes', 0)
        
        # Auto-verify if: upvotes >= 5 AND upvotes > downvotes * 2
        return upvotes >= 5 and upvotes > downvotes * 2
    
    def add_user(self, user_data):
        """Add a new user"""
        user_data['created_at'] = datetime.now()
        user_data['updated_at'] = datetime.now()
        result = self.users.insert_one(user_data)
        return str(result.inserted_id)
    
    def log_emergency(self, emergency_data):
        """Log an emergency event"""
        emergency_data['timestamp'] = datetime.now()
        result = self.emergency_logs.insert_one(emergency_data)
        return str(result.inserted_id)

# Singleton instance
db_instance = Database()