import cv2
import numpy as np
from datetime import datetime
from .logger import Logger
from .exceptions import FaceRecognitionError

class FaceRecognition:
    def __init__(self, config, model):
        self.config = config
        self.model = model
        self.logger = Logger(config['logging']['attendance_log'], 'FaceRecognition')
        
        # Load face detection cascade
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Initialize camera
        self.camera = None
        self.initialize_camera()

    def initialize_camera(self):
        """Initialize camera with configured settings"""
        try:
            camera_index = self.config['device']['camera_index']
            self.camera = cv2.VideoCapture(camera_index)
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 
                          self.config['camera']['width'])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 
                          self.config['camera']['height'])
            
            if not self.camera.isOpened():
                raise FaceRecognitionError("Failed to initialize camera")
                
            self.logger.info("Camera initialized successfully")
        except Exception as e:
            raise FaceRecognitionError(f"Camera initialization error: {str(e)}")

    def detect_faces(self, frame):
        """Detect faces in frame"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=self.config['face_detection']['scale_factor'],
                minNeighbors=self.config['face_detection']['min_neighbors'],
                minSize=tuple(self.config['face_detection']['min_face_size'])
            )
            return faces
        except Exception as e:
            self.logger.error(f"Face detection error: {str(e)}")
            return []

    def process_frame(self):
        """Process a single frame"""
        try:
            ret, frame = self.camera.read()
            if not ret:
                raise FaceRecognitionError("Failed to capture frame")

            faces = self.detect_faces(frame)
            results = []
            
            for (x, y, w, h) in faces:
                # Extract and preprocess face
                face_img = frame[y:y+h, x:x+w]
                
                # Get prediction
                prediction = self.model.predict(face_img)
                if prediction:
                    results.append({
                        'bbox': (x, y, w, h),
                        'prediction': prediction
                    })
                    
                    # Draw rectangle around face
                    if self.config['debug']['show_detection']:
                        cv2.rectangle(
                            frame, 
                            (x, y), 
                            (x+w, y+h), 
                            (0, 255, 0), 
                            2
                        )

            return frame, results
        except Exception as e:
            self.logger.error(f"Frame processing error: {str(e)}")
            return None, []

    def cleanup(self):
        """Release camera resources"""
        if self.camera is not None:
            self.camera.release()