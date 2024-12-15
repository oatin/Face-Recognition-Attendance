import os
import numpy as np
import psycopg2
from .preprocess import FacePreprocessor

class DataLoader:
    def __init__(self, db_url="postgres://admin:a@db:5432/db_face_scan"):
        self.db_url = db_url
        self.preprocessor = FacePreprocessor(landmark_path="utils/shape_predictor_68_face_landmarks.dat")
    
    def get_connection(self):
        return psycopg2.connect(self.db_url)

    def load_course_data(self, course_id):
        conn = self.get_connection()
        cur = conn.cursor()
        
        try:
            # Get enrolled students' training images
            query = """
                SELECT ti.file_path, s.student_id
                FROM public.devices_trainingimage ti
                LEFT JOIN public.members_student s ON ti.member_id = s.member_id
                LEFT JOIN public.courses_enrollment e ON s.student_id = e.student_id AND e.course_id = %s
                WHERE s.student_id IS NOT NULL;
            """
            cur.execute(query, (course_id,))
            results = cur.fetchall()
            
            X = []  # Preprocessed images
            original_labels = []  # Original student IDs
            
            print(f"Processing {len(results)} images for course {course_id}")
            
            for image_path, student_id in results:
                processed_face = self.preprocessor.preprocess_image(f"media/{image_path}")
                if processed_face is not None:
                    X.append(processed_face)
                    original_labels.append(student_id)
            
            # Convert original labels to continuous numbers starting from 0
            unique_labels = list(set(original_labels))
            label_map = {label: idx for idx, label in enumerate(unique_labels)}
            y = np.array([label_map[label] for label in original_labels])
            
            # Store the mapping for later use (optional)
            self.label_map = label_map
            self.inverse_label_map = {v: k for k, v in label_map.items()}
            
            print(f"Original labels: {original_labels}")
            print(f"Encoded labels: {y}")
            print(f"Label mapping: {label_map}")
            
            return np.array(X), y
            
        finally:
            cur.close()
            conn.close()
    
    def save_model_info(self, course_id, description, model_path):
        """Check if course_id has been trained, if yes update model_version, else insert new record starting at version 1"""
        conn = self.get_connection()
        cur = conn.cursor()
        
        try:
            # Check if course_id has been trained
            cur.execute("""
                SELECT id FROM public.devices_facemodel WHERE course_id = %s
            """, (course_id,))
            existing_model = cur.fetchone()
            
            if existing_model:
                # If model exists, update model_version by incrementing the current version
                cur.execute("""
                    UPDATE public.devices_facemodel
                    SET model_version = model_version + 1, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (existing_model[0],))
            else:
                # If model doesn't exist, insert new model record with model_version starting at 1
                cur.execute("""
                    INSERT INTO public.devices_facemodel (course_id, model_version, description, model_path, created_at)
                    VALUES (%s, 1, %s, %s, CURRENT_TIMESTAMP)
                    RETURNING id
                """, (course_id, description, model_path))
                model_id = cur.fetchone()[0]

                # Update device assignments
                cur.execute("""
                    INSERT INTO public.devices_facemodelassignment (device_id, model_id, assigned_at)
                    SELECT d.id, %s, CURRENT_TIMESTAMP
                    FROM public.devices_device d
                    JOIN public.attendance_schedule s ON d.room_id = s.room_id
                    WHERE s.course_id = %s
                """, (model_id, course_id))
            
            conn.commit()
            
        finally:
            cur.close()
            conn.close()