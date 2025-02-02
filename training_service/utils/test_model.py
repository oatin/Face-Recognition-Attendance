import os
import cv2
import numpy as np

from .model import create_triplets

def load_images_from_directory(directory_path, image_size=(224, 224)):
    X_data = []
    y_data = []
    class_labels = {}
    current_label = 0

    # อ่านโฟลเดอร์ย่อย
    for member_folder in sorted(os.listdir(directory_path)):
        folder_path = os.path.join(directory_path, member_folder)
        if not os.path.isdir(folder_path):
            continue

        # กำหนด label สำหรับแต่ละ member
        class_labels[member_folder] = current_label

        # อ่านภาพในแต่ละโฟลเดอร์
        for image_file in os.listdir(folder_path):
            image_path = os.path.join(folder_path, image_file)
            
            # โหลดภาพและ resize ให้ขนาด 224x224
            image = cv2.imread(image_path)
            if image is None:
                continue
            image = cv2.resize(image, image_size)
            image = image / 255.0  # Normalize

            X_data.append(image)
            y_data.append(current_label)
        
        current_label += 1

    return np.array(X_data), np.array(y_data), class_labels

dataset_path = r"C:\Users\oat40\OneDrive\Desktop\Face-Recognition-Attendance\media\training_images"
X_images, y_labels, class_mapping = load_images_from_directory(dataset_path)

print(f"Shape of X_images: {X_images.shape}")
print(f"Shape of y_labels: {y_labels.shape}")
print(f"Class Mapping: {class_mapping}")
triplets = create_triplets(X_images, y_labels)
X_train = np.array([np.concatenate([a, p, n]) for a, p, n in triplets])
y_train = np.zeros((X_train.shape[0],))
