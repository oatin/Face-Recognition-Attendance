import os
from utils.preprocess import FacePreprocessor

input_folder = "preprocess_image/unknowns/"
output_folder = "preprocess_image/unknown/"

face = FacePreprocessor("utils/shape_predictor_68_face_landmarks.dat")

for filename in os.listdir(input_folder):
    file_path = os.path.join(input_folder, filename)
    
    if os.path.isfile(file_path) and filename.lower().endswith((".jpg", ".jpeg", ".png")):
        print(f"กำลังประมวลผลไฟล์: {filename}")
        face.preprocess_image(image_path=file_path, output_folder=output_folder)
