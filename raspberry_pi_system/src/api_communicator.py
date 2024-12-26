import requests
import json
from .exceptions import APIConnectionError

class APICommunicator:
    def __init__(self, config):
        self.api_url = config['api']['url']
        self.timeout = config['api']['timeout']
        self.headers = {
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method, endpoint, data=None):
        url = f"{self.api_url}/{endpoint}"
        try:
            response = requests.request(
                method, url, headers=self.headers, data=json.dumps(data), timeout=self.timeout
            )
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            raise APIConnectionError(f"API request failed: {str(e)}")
    
    def get_device_info(self, mac_address):
        """Get device information based on MAC address"""
        endpoint = f"devices/{mac_address}"
        return self._make_request('GET', endpoint)
    
    def get_current_schedule(self, room, day_of_week):
        """Get the current schedule for a room on a specific day"""
        endpoint = f"schedules/{room}/{day_of_week}"
        return self._make_request('GET', endpoint)
    
    def get_face_model(self, course):
        """Get face model for a given course"""
        endpoint = f"models/{course}"
        return self._make_request('GET', endpoint)
