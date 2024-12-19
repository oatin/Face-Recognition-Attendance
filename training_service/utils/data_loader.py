import os
import numpy as np
import requests
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, List, Dict, Optional
from functools import lru_cache
from .preprocess import FacePreprocessor

class DataLoader:
    def __init__(
        self,
        base_url: str = "http://app:8000",
        landmark_path: str = "utils/shape_predictor_68_face_landmarks.dat",
        max_workers: int = 4
    ):
        """
        Initialize DataLoader with configuration.
        
        Args:
            base_url: Base URL for API endpoints
            landmark_path: Path to facial landmark predictor file
            max_workers: Maximum number of threads for parallel processing
        """
        self.base_url = base_url.rstrip('/')
        self.preprocessor = FacePreprocessor(landmark_path=landmark_path)
        self.token = None
        self.max_workers = max_workers
        
        # API endpoints
        self.endpoints = {
            'enrollment': f"{self.base_url}/api/Enrollment/",
            'student': f"{self.base_url}/api/Student/",
            'training_image': f"{self.base_url}/api/TrainingImageViewSet/",
            'face_model': f"{self.base_url}/api/FaceModel/",
            'face_model_assignment': f"{self.base_url}/api/FaceModelAssignment/",
            'schedule': f"{self.base_url}/api/Schedule/",
            'device': f"{self.base_url}/api/device/"
        }

    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate with the API and get JWT token."""
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
        """Get headers with JWT token."""
        if not self.token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def _make_request(self, url: str, method: str = 'get', **kwargs) -> Optional[dict]:
        """Make API request with error handling and retries."""
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

    @lru_cache(maxsize=100)
    def _get_student_info(self, student_id: int) -> Optional[dict]:
        """Get student information with caching."""
        return self._make_request(f"{self.endpoints['student']}{student_id}/")

    def _process_image(self, image_data: dict) -> Tuple[Optional[np.ndarray], Optional[int]]:
        """Process a single training image."""
        try:
            image_path = image_data.get('file_path')
            student_id = image_data.get('member')
            
            if not image_path or not student_id:
                return None, None

            full_path = os.path.join('.', image_path) 
            
            processed_face = self.preprocessor.preprocess_image(full_path)
            
            if processed_face is not None:
                return processed_face, student_id
                
        except Exception as e:
            print(f"Error processing image {image_data.get('file_path')}: {str(e)}")
        
        return None, None

    def load_course_data(self, course_id: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load and preprocess course data efficiently using parallel processing.
        
        Args:
            course_id: Course ID to load data for
            
        Returns:
            Tuple of (processed_images, labels)
        """
        if not self.token:
            raise ValueError("Not authenticated. Call authenticate() first.")

        # Get all training images for the course
        params = {'course_id': course_id}
        training_data = self._make_request(
            self.endpoints['training_image'],
            params=params
        )

        if not training_data:
            return np.array([]), np.array([])

        # Process images in parallel
        images_data = training_data if isinstance(training_data, list) else training_data.get('results', [])

        for image_data in images_data:
            image_data['file_path'] = image_data['file_path'].replace('http://app:8000', '')
        
        X = []
        y = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(self._process_image, images_data))
            
            for processed_face, student_id in results:
                if processed_face is not None and student_id is not None:
                    X.append(processed_face)
                    y.append(student_id)

        if not X:
            return np.array([]), np.array([])

        # Convert to numpy arrays and encode labels
        X = np.array(X)
        unique_labels = list(set(y))
        label_map = {label: idx for idx, label in enumerate(unique_labels)}
        y = np.array([label_map[label] for label in y])

        self.label_map = label_map
        self.inverse_label_map = {v: k for k, v in label_map.items()}

        print(X,y)
        return X, y

    def save_model_info(self, course_id: int, description: str, model_path: str) -> bool:
        """Save or update face model information."""
        if not self.token:
            raise ValueError("Not authenticated. Call authenticate() first.")

        try:
            # Check existing model
            existing_models = self._make_request(
                self.endpoints['face_model'],
                params={'course_id': course_id}
            )

            model_data = {
                "course_id": course_id,
                "description": description,
                "model_path": model_path
            }

            if existing_models and existing_models.get('results', []):
                # Update existing model
                model = existing_models['results'][0]
                model_data['model_version'] = model.get('model_version', 0) + 1
                response = self._make_request(
                    f"{self.endpoints['face_model']}{model['id']}/",
                    method='patch',
                    json=model_data
                )
            else:
                # Create new model
                model_data['model_version'] = 1
                response = self._make_request(
                    self.endpoints['face_model'],
                    method='post',
                    json=model_data
                )

            if response and response.get('id'):
                self._assign_model_to_devices(response['id'], course_id)
                return True

            return False

        except Exception as e:
            print(f"Error saving model info: {str(e)}")
            return False

    def _assign_model_to_devices(self, model_id: int, course_id: int) -> None:
        """Assign model to relevant devices."""
        schedules = self._make_request(
            self.endpoints['schedule'],
            params={'course': course_id}
        )

        if not schedules:
            return

        schedule_list = schedules if isinstance(schedules, list) else schedules.get('results', [])
        
        for schedule in schedule_list:
            room_id = schedule.get('room')
            if not room_id:
                continue

            devices = self._make_request(
                self.endpoints['device'],
                params={'room': room_id}
            )

            if not devices:
                continue

            device_list = devices if isinstance(devices, list) else devices.get('results', [])
            
            for device in device_list:
                assignment_data = {
                    "device": device['id'],
                    "model": model_id
                }
                
                self._make_request(
                    self.endpoints['face_model_assignment'],
                    method='post',
                    json=assignment_data
                )
    def get_latest_model_path(self, device_id: int) -> Optional[str]:
        """Get the latest model path for a device."""
        try:
            # Get latest model assignment for device
            response = requests.get(
                f"{self.base_url}/api/FaceModelAssignment/",
                params={
                    "device": device_id,
                    "ordering": "-model__created_at"
                },
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            assignments = response.json()

            if not assignments or not assignments.get('results'):
                return None

            latest_assignment = assignments['results'][0]
            model_id = latest_assignment.get('model')

            if not model_id:
                return None

            # Get model details
            response = requests.get(
                f"{self.base_url}/api/FaceModel/{model_id}/",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            model_data = response.json()

            return model_data.get('model_path')

        except requests.exceptions.RequestException as e:
            print(f"API request failed: {str(e)}")
            return None

    def update_assignment_status(self, device_id: int) -> bool:
        """Update the assignment status for a device."""
        try:
            response = requests.patch(
                f"{self.base_url}/api/FaceModelAssignment/",
                params={"device": device_id},
                json={"assigned_at": "now"},
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Failed to update assignment status: {str(e)}")
            return False