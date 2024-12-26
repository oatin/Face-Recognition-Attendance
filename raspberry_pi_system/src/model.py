import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
from .logger import Logger
from .exceptions import ModelLoadError

class FaceModel:
    def __init__(self, config):
        self.config = config
        self.model = None
        self.model_path = None
        self.logger = Logger(config['logging']['app_log'], 'Face_Model')
        
        # Initialize GPU memory growth to avoid taking all GPU memory
        physical_devices = tf.config.list_physical_devices('GPU')
        if physical_devices:
            try:
                for device in physical_devices:
                    tf.config.experimental.set_memory_growth(device, True)
                self.logger.info("GPU memory growth enabled")
            except:
                self.logger.warning("GPU memory growth configuration failed")

    def load_model(self, model_path):
        """Load Keras model from path"""
        try:
            if self.model_path != model_path:
                self.model = load_model(model_path, compile=False)
                self.model.compile(
                    optimizer='adam',
                    loss='sparse_categorical_crossentropy',
                    metrics=['accuracy']
                )
                self.model_path = model_path
                self.logger.info(f"Successfully loaded model from {model_path}")
                return True
            return False
        except Exception as e:
            raise ModelLoadError(f"Error loading model: {str(e)}")

    def preprocess_image(self, face_image):
        """Preprocess face image for model input"""
        try:
            # Resize to expected input size
            target_size = self.config['model']['input_shape']
            face_image = tf.image.resize(face_image, target_size[:2])
            
            # Normalize pixel values
            face_image = face_image / 255.0
            
            # Add batch dimension
            face_image = np.expand_dims(face_image, axis=0)
            return face_image
        except Exception as e:
            self.logger.error(f"Error preprocessing image: {str(e)}")
            return None

    def predict(self, face_image):
        """Make prediction on face image"""
        if self.model is None:
            self.logger.error("No model loaded")
            return None

        try:
            # Preprocess image
            processed_image = self.preprocess_image(face_image)
            if processed_image is None:
                return None

            # Make prediction
            predictions = self.model.predict(processed_image)
            
            # Get top prediction
            predicted_class = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class])

            return {
                "student_id": str(predicted_class),  # Map to actual student ID
                "confidence": confidence
            }
        except Exception as e:
            self.logger.error(f"Error during prediction: {str(e)}")
            return None