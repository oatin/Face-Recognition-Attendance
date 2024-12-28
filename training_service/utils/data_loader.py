import os
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, Dict, Optional
from functools import lru_cache
from .preprocess import FacePreprocessor
from .api_communicator import APIClient

class DataLoader:
    """Handles loading and processing of training data"""
    def __init__(
        self,
        base_url: str = "http://app:8000",
        landmark_path: str = "utils/shape_predictor_68_face_landmarks.dat",
        max_workers: int = 4
    ):
        self.api_client = APIClient(base_url)
        self.preprocessor = FacePreprocessor(landmark_path=landmark_path)
        self.max_workers = max_workers
        self.label_map: Dict[int, int] = {}
        self.inverse_label_map: Dict[int, int] = {}

    def authenticate(self, username: str, password: str) -> bool:
        """Proxy method to authenticate API client"""
        return self.api_client.authenticate(username, password)

    @lru_cache(maxsize=100)
    def _get_student_info(self, student_id: int) -> Optional[dict]:
        """Get student information with caching."""
        return self.api_client.make_request(
            f"{self.api_client.endpoints.student}{student_id}/"
        )

    def _process_image(
        self, 
        image_data: dict
    ) -> Tuple[Optional[np.ndarray], Optional[int]]:
        """Process a single training image."""
        try:
            image_path = image_data.get('file_path')
            student_id = image_data.get('member')
            
            if not image_path or not student_id:
                return None, None

            full_path = os.path.join('.', image_path) 
            processed_face = self.preprocessor.preprocess_image(full_path)
            
            return (processed_face, student_id) if processed_face is not None else (None, None)
                
        except Exception as e:
            print(f"Error processing image {image_data.get('file_path')}: {str(e)}")
            return None, None

    def load_course_data(self, course_id: int) -> Tuple[np.ndarray, np.ndarray]:
        """Load and preprocess course data efficiently using parallel processing."""
        if not self.api_client.token:
            raise ValueError("Not authenticated. Call authenticate() first.")

        training_data = self.api_client.make_request(
            self.api_client.endpoints.training_image,
            params={'course_id': course_id}
        )

        if not training_data:
            return np.array([]), np.array([])

        images_data = (
            training_data if isinstance(training_data, list) 
            else training_data.get('results', [])
        )

        # Clean image paths
        for image_data in images_data:
            image_data['file_path'] = image_data['file_path'].replace(
                'http://app:8000', ''
            )

        # Process images in parallel
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

        # Prepare and encode data
        X = np.array(X)
        unique_labels = list(set(y))
        self.label_map = {label: idx for idx, label in enumerate(unique_labels)}
        self.inverse_label_map = {v: k for k, v in self.label_map.items()}
        y = np.array([self.label_map[label] for label in y])

        return X, y

    def save_model_info(
        self, 
        course_id: int, 
        description: str, 
        model_path: str
    ) -> bool:
        """Save or update face model information."""
        if not self.api_client.token:
            raise ValueError("Not authenticated. Call authenticate() first.")

        try:
            existing_models = self.api_client.make_request(
                self.api_client.endpoints.face_model,
                params={'course_id': course_id}
            )

            model_data = {
                "course": course_id,
                "description": description,
                "model_path": model_path
            }

            if existing_models and existing_models.get('results', []):
                # Update existing model
                model = existing_models['results'][0]
                model_data['model_version'] = model.get('model_version', 0) + 1
                response = self.api_client.make_request(
                    f"{self.api_client.endpoints.face_model}{model['id']}/",
                    method='patch',
                    json=model_data
                )
            else:
                # Create new model
                model_data['model_version'] = 1
                response = self.api_client.make_request(
                    self.api_client.endpoints.face_model,
                    method='post',
                    json=model_data
                )

            return bool(response)

        except Exception as e:
            print(f"Error saving model info: {str(e)}")
            return False