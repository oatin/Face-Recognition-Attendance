import requests
from typing import Dict, Optional, Any
from dataclasses import dataclass

@dataclass
class APIEndpoints:
    enrollment: str
    member: str
    training_image: str
    face_model: str
    schedule: str
    device: str
    course: str
    config: str

    @classmethod
    def from_base_url(cls, base_url: str) -> 'APIEndpoints':
        base = base_url.rstrip('/')
        return cls(
            enrollment=f"{base}/api/Enrollment/",
            member=f"{base}/api/members/",
            training_image=f"{base}/api/TrainingImageViewSet/",
            face_model=f"{base}/api/FaceModel/",
            schedule=f"{base}/api/Schedule/",
            device=f"{base}/api/device/",
            course=f"{base}/api/courses/",
            config=f"{base}/api/service-configs/by-service/Training/"
        )

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.token: Optional[str] = None
        self.endpoints = APIEndpoints.from_base_url(self.base_url)

    def authenticate(self, username: str, password: str) -> bool:
        try:
            response = requests.post(
                f"{self.base_url}/api/token/",
                json={"username": username, "password": password},
                timeout=10
            )
            response.raise_for_status()
            self.token = response.json()["access"]
            return True
        except requests.exceptions.RequestException as e:
            print(f"Authentication failed: {str(e)}")
            return False

    @property
    def headers(self) -> Dict[str, str]:
        if not self.token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def make_request(
        self, 
        url: str, 
        method: str = 'get', 
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        try:
            response = requests.request(
                method, 
                url,
                headers=self.headers,
                timeout=10,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {str(e)}")
            if hasattr(response, 'text'):
                print(f"Response text: {response.text}")
            return None