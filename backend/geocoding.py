import requests
from config import Config
import json
from functools import lru_cache
import time

class GeocodingService:
    def __init__(self):
        self.api_key = Config.GOOGLE_MAPS_API_KEY
        self.use_nominatim = not self.api_key  # Fallback to free service
    
    @lru_cache(maxsize=1000)
    def reverse_geocode(self, latitude, longitude):
        """
        Convert coordinates to human-readable address
        Returns: {'name': 'Place Name', 'address': 'Full Address'}
        """
        if self.api_key and not self.use_nominatim:
            return self._google_reverse_geocode(latitude, longitude)
        else:
            return self._nominatim_reverse_geocode(latitude, longitude)
    
    def _google_reverse_geocode(self, lat, lng):
        """Use Google Maps Geocoding API"""
        try:
            url = f"https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'latlng': f"{lat},{lng}",
                'key': self.api_key,
                'result_type': 'street_address|premise|point_of_interest'
            }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                result = data['results'][0]
                
                # Extract place name (try different fields)
                place_name = self._extract_place_name(result)
                full_address = result.get('formatted_address', '')
                
                return {
                    'place_name': place_name,
                    'full_address': full_address,
                    'components': result.get('address_components', []),
                    'source': 'google'
                }
        
        except Exception as e:
            print(f"Google geocoding error: {e}")
        
        return self._nominatim_reverse_geocode(lat, lng)  # Fallback
    
    def _nominatim_reverse_geocode(self, lat, lng):
        """Use free OpenStreetMap Nominatim API"""
        try:
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                'format': 'json',
                'lat': lat,
                'lon': lng,
                'zoom': 18,
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': 'SafeStree-App/1.0'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=5)
            data = response.json()
            
            if 'display_name' in data:
                # Extract place name from address components
                address = data.get('address', {})
                place_name = self._extract_nominatim_place_name(address)
                
                return {
                    'place_name': place_name,
                    'full_address': data.get('display_name', ''),
                    'components': address,
                    'source': 'nominatim'
                }
        
        except Exception as e:
            print(f"Nominatim geocoding error: {e}")
        
        # Return default if both fail
        return {
            'place_name': f"Location ({lat:.4f}, {lng:.4f})",
            'full_address': '',
            'components': {},
            'source': 'default'
        }
    
    def _extract_place_name(self, google_result):
        """Extract best place name from Google result"""
        # Try different fields in order of preference
        address_components = google_result.get('address_components', [])
        
        # Look for specific place types
        place_types = ['establishment', 'point_of_interest', 'premise']
        
        for component in address_components:
            types = component.get('types', [])
            if any(t in place_types for t in types):
                return component.get('long_name', '')
        
        # Fallback to street or locality
        for component in address_components:
            types = component.get('types', [])
            if 'route' in types:  # Street name
                return component.get('long_name', '')
            if 'locality' in types:  # City/town
                return component.get('long_name', '')
        
        # Last resort: use formatted address first part
        address = google_result.get('formatted_address', '')
        return address.split(',')[0].strip()
    
    def _extract_nominatim_place_name(self, address):
        """Extract place name from Nominatim address"""
        # Order of preference for place name
        fields = [
            'amenity',  # Restaurant, café, etc.
            'shop',     # Shop names
            'building',
            'road',     # Street name
            'neighbourhood',
            'suburb',
            'village',
            'town',
            'city'
        ]
        
        for field in fields:
            if field in address:
                return address[field]
        
        return "Unknown Location"
    
    def forward_geocode(self, place_name):
        """Convert place name to coordinates"""
        try:
            if self.api_key and not self.use_nominatim:
                url = f"https://maps.googleapis.com/maps/api/geocode/json"
                params = {
                    'address': place_name,
                    'key': self.api_key
                }
                
                response = requests.get(url, params=params, timeout=5)
                data = response.json()
                
                if data['status'] == 'OK' and data['results']:
                    location = data['results'][0]['geometry']['location']
                    return {
                        'lat': location['lat'],
                        'lng': location['lng']
                    }
            else:
                # Use Nominatim for forward geocoding
                url = "https://nominatim.openstreetmap.org/search"
                params = {
                    'q': place_name,
                    'format': 'json',
                    'limit': 1
                }
                
                headers = {'User-Agent': 'SafeStree-App/1.0'}
                response = requests.get(url, params=params, headers=headers, timeout=5)
                data = response.json()
                
                if data:
                    return {
                        'lat': float(data[0]['lat']),
                        'lng': float(data[0]['lon'])
                    }
        
        except Exception as e:
            print(f"Forward geocoding error: {e}")
        
        return None

# Singleton instance
geocoder = GeocodingService()