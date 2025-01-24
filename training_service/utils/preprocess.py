import os
import cv2
import numpy as np
import dlib

class FacePreprocessor:
    def __init__(self, landmark_path='shape_predictor_68_face_landmarks.dat'):
        self.face_detector = dlib.get_frontal_face_detector()
        self.landmark_predictor = dlib.shape_predictor(landmark_path)
        
    def preprocess_image(self, image_path, output_folder="preprocess_image"):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        filename = os.path.basename(image_path)  
        save_path = os.path.join(output_folder, filename)  
        
        image = cv2.imread(image_path)
        if image is None:
            print(f"Cannot read image: {image_path}")
            return None
            
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        faces = self.face_detector(gray)
        if not faces:
            print(f"No faces detected in: {image_path}")
            return None
            
        face = max(faces, key=lambda rect: rect.width() * rect.height())
        
        landmarks = self.landmark_predictor(gray, face)
        landmarks_points = np.array([[p.x, p.y] for p in landmarks.parts()])
        
        left_eye = np.mean(landmarks_points[36:42], axis=0)
        right_eye = np.mean(landmarks_points[42:48], axis=0)
        
        angle = np.degrees(np.arctan2(right_eye[1] - left_eye[1], right_eye[0] - left_eye[0]))
        
        center = tuple(np.mean([left_eye, right_eye], axis=0))
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        aligned_gray = cv2.warpAffine(gray, rotation_matrix, (image.shape[1], image.shape[0]))
        
        x, y, w, h = face.left(), face.top(), face.width(), face.height()
        margin_w = int(0.2 * w)
        margin_h = int(0.2 * h)
        
        top = max(0, y - margin_h)
        bottom = min(aligned_gray.shape[0], y + h + margin_h)
        left = max(0, x - margin_w)
        right = min(aligned_gray.shape[1], x + w + margin_w)
        
        face_region = aligned_gray[top:bottom, left:right]
        
        face_region = cv2.resize(face_region, (224, 224))
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        face_region = clahe.apply(face_region)
        
        face_region = cv2.cvtColor(face_region, cv2.COLOR_GRAY2RGB)
        
        face_region = face_region.astype(np.float32) / 255.0
        
        cv2.imwrite(save_path, (face_region * 255).astype(np.uint8)) 
        print(f"Processed face saved to: {save_path}")
        
        return face_region
