import os
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, Dict, Optional
from functools import lru_cache
from .preprocess import FacePreprocessor
from .api_communicator import APIClient

from PIL import Image
from sklearn.utils import shuffle

class DataLoader:
    def __init__(
        self,
        base_url: str = "http://app:8000",
        landmark_path: str = "utils/shape_predictor_68_face_landmarks.dat",
        max_workers: int = 1
    ):
        self.api_client = APIClient(base_url)
        self.preprocessor = FacePreprocessor(landmark_path=landmark_path)
        self.max_workers = max_workers
        self.label_map: Dict[int, int] = {}
        self.inverse_label_map: Dict[int, int] = {}

    def authenticate(self, username: str, password: str) -> bool:
        return self.api_client.authenticate(username, password)

    @lru_cache(maxsize=100)
    def _get_student_info(self, student_id: int) -> Optional[dict]:
        return self.api_client.make_request(
            f"{self.api_client.endpoints.member}{student_id}/"
        )

    def _process_image(
        self, 
        image_data: dict
    ) -> Tuple[Optional[np.ndarray], Optional[int]]:
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
        if not self.api_client.token:
            raise ValueError("Not authenticated. Call authenticate() first.")

        training_data = self.api_client.make_request(
            self.api_client.endpoints.training_image,
            params={'course_id': course_id}
        )

        if not training_data:
            return np.array([]), np.array([]), np.array([])

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

        unknown_folder = "preprocess_image/unknown"
        if os.path.exists(unknown_folder):
            for filename in os.listdir(unknown_folder):
                if filename.endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(unknown_folder, filename)
                    try:
                        image = Image.open(image_path).resize((224, 224))
                        image = np.array(image) / 255.0  
                        X.append(image)
                        y.append("unknown")  
                    except Exception as e:
                        print(f"Error loading image {image_path}: {e}")
        if not X:
            return np.array([]), np.array([]), np.array([])

        # Prepare and encode data
        X = np.array(X)
        unique_labels = list(set(y))
        self.label_map = {label: idx for idx, label in enumerate(unique_labels)}
        self.inverse_label_map = {v: k for k, v in self.label_map.items()}
        y = np.array([self.label_map[label] for label in y])

        X, y = shuffle(X, y, random_state=42)
        return X, y, self.inverse_label_map