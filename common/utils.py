from facenet_pytorch import MTCNN
from PIL import Image
import numpy as np
import os

mtcnn = MTCNN(
    image_size=224,
    min_face_size=20,
    thresholds=[0.6, 0.7, 0.7],
    factor=0.8,
    device='cpu' 
)

def np_angle(a, b, c):
    ba = np.array(a) - np.array(b)
    bc = np.array(c) - np.array(b)
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    return np.degrees(angle)

def predFacePose(image_path):
    if not os.path.exists(image_path):
        return False, "File does not exist"
    
    try:
        im = Image.open(image_path)
        if im.mode != "RGB": 
            im = im.convert('RGB')

        bbox, probs, landmarks_list = mtcnn.detect(im, landmarks=True)

        if landmarks_list is None or probs is None:
            return False, "No face detected in the image"

        for landmarks, prob in zip(landmarks_list, probs):
            if prob > 0.9: 
                angR = np_angle(landmarks[0], landmarks[1], landmarks[2])  
                angL = np_angle(landmarks[1], landmarks[0], landmarks[2])  

                if 35 <= int(angR) <= 56 and 35 <= int(angL) <= 57:
                    return True, "Frontal Face"
                elif angR < angL:
                    return True, "Right Profile"
                else:
                    return True, "Left Profile"
            else:
                return False, f"Invalid pose detected: Low detection probability ({prob:.2f})"
        
        return False, "No valid face pose detected"
    except Exception as e:
        return False, f"Error processing image: {str(e)}"