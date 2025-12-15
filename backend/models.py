from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class Location(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None

class User(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    emergency_contacts: List[str] = []
    created_at: datetime = datetime.now()
    is_verified: bool = False

class Report(BaseModel):
    id: int
    user_id: str
    location: Location
    incident_type: str  # harassment, assault, theft, etc.
    severity: int = 3  # 1-5 scale
    description: str
    timestamp: datetime = datetime.now()
    verified: bool = False
    upvotes: int = 0
    downvotes: int = 0
    media_urls: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user123",
                "location": {"latitude": 28.6139, "longitude": 77.2090},
                "incident_type": "harassment",
                "severity": 3,
                "description": "Group following me",
                "verified": False
            }
        }

class SafetyZone(BaseModel):
    id: int
    location: Location
    radius_meters: float
    safety_score: int  # 0-100
    color_code: str  # green, yellow, orange, red
    last_updated: datetime
    active_reports: int = 0