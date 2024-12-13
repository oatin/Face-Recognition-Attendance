import cv2
import numpy as np
import dlib

class FacePreprocessor:
    def __init__(self, landmark_path='shape_predictor_68_face_landmarks.dat'):
        self.face_detector = dlib.get_frontal_face_detector()
        self.landmark_predictor = dlib.shape_predictor(landmark_path)
        
    def preprocess_image(self, image_path):
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return None
            
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_detector(gray)
        if not faces:
            return None
            
        # Get largest face
        face = max(faces, key=lambda rect: rect.width() * rect.height())
        
        # Get landmarks
        landmarks = self.landmark_predictor(gray, face)
        landmarks_points = np.array([[p.x, p.y] for p in landmarks.parts()])
        
        # Align face using eyes position
        left_eye = np.mean(landmarks_points[36:42], axis=0)
        right_eye = np.mean(landmarks_points[42:48], axis=0)
        
        # Calculate angle for alignment
        angle = np.degrees(np.arctan2(right_eye[1] - left_eye[1], right_eye[0] - left_eye[0]))
        
        # Rotate image
        center = tuple(np.mean([left_eye, right_eye], axis=0))
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        aligned_gray = cv2.warpAffine(gray, rotation_matrix, (image.shape[1], image.shape[0]))
        
        # Crop face region
        x, y, w, h = face.left(), face.top(), face.width(), face.height()
        margin_w = int(0.2 * w)
        margin_h = int(0.2 * h)
        
        top = max(0, y - margin_h)
        bottom = min(aligned_gray.shape[0], y + h + margin_h)
        left = max(0, x - margin_w)
        right = min(aligned_gray.shape[1], x + w + margin_w)
        
        face_region = aligned_gray[top:bottom, left:right]
        
        # Resize to standard size
        face_region = cv2.resize(face_region, (224, 224))
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        face_region = clahe.apply(face_region)
        
        # Convert back to RGB (needed for MobileNetV2)
        face_region = cv2.cvtColor(face_region, cv2.COLOR_GRAY2RGB)
        
        # Normalize
        face_region = face_region.astype(np.float32) / 255.0
        
        return face_region