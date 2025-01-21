import cv2
import numpy as np
from mtcnn import MTCNN
import math
import os

def calculate_angles(landmarks):
    right_eye = landmarks['right_eye']
    left_eye = landmarks['left_eye']
    nose = landmarks['nose']
    
    theta1 = math.degrees(math.atan2(right_eye[1] - nose[1], right_eye[0] - nose[0]))
    theta2 = math.degrees(math.atan2(left_eye[1] - nose[1], left_eye[0] - nose[0]))
    
    return theta1, theta2

def detect_face_pose(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
        
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Failed to load image: {image_path}")
    
    detector = MTCNN()
    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    faces = detector.detect_faces(image)
    
    if not faces:
        return False, "No face detected"
    
    landmarks = faces[0]['keypoints']
    
    theta1, theta2 = calculate_angles(landmarks)
    
    if -10 <= theta1 <= 10 and -10 <= theta2 <= 10:
        return True, "Frontal Face"
    elif theta1 < -10 and theta2 < -10:
        return True, "Left Profile"
    elif theta1 > 10 and theta2 > 10:
        return True, "Right Profile"
    else:
        return False, "Invalid pose detected"