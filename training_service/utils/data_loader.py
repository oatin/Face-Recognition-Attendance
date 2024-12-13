import os
import numpy as np
import psycopg2
from .preprocess import FacePreprocessor

class DataLoader:
    def __init__(self, db_url="postgres://admin:a@db:5432/db_face_scan"):
        self.db_url = db_url
        self.preprocessor = FacePreprocessor()
    
    def get_connection(self):
        return psycopg2.connect(self.db_url)

    def load_course_data(self, course_id):
        conn = self.get_connection()
        cur = conn.cursor()
        
        try:
            # Get enrolled students' training images
            query = """
                SELECT ti.image_path, s.student_id 
                FROM training_image ti
                JOIN student s ON ti.student_id = s.id
                JOIN enrollment e ON s.id = e.student_id
                WHERE e.course_id = %s AND ti.status = 'active'
            """
            cur.execute(query, (course_id,))
            results = cur.fetchall()
            
            X = []  # Preprocessed images
            y = []  # Labels
            student_ids = []  # Keep track of student IDs
            
            print(f"Processing {len(results)} images for course {course_id}")
            
            for image_path, student_id in results:
                processed_face = self.preprocessor.preprocess_image(image_path)
                if processed_face is not None:
                    X.append(processed_face)
                    y.append(student_id)
                    student_ids.append(student_id)
            
            return np.array(X), np.array(y), student_ids
            
        finally:
            cur.close()
            conn.close()
    
    def save_model_info(self, course_id, model_path, student_ids):
        conn = self.get_connection()
        cur = conn.cursor()
        
        try:
            # Create new model record
            cur.execute("""
                INSERT INTO face_model (course_id, model_path, status, created_at)
                VALUES (%s, %s, 'active', CURRENT_TIMESTAMP)
                RETURNING id
            """, (course_id, model_path))
            
            model_id = cur.fetchone()[0]
            
            # Update device assignments
            cur.execute("""
                INSERT INTO face_model_assignment (device_id, model_id, status)
                SELECT d.id, %s, 'pending'
                FROM device d
                JOIN schedule s ON d.room_id = s.room_id
                WHERE s.course_id = %s
            """, (model_id, course_id))
            
            conn.commit()
            return model_id
            
        finally:
            cur.close()
            conn.close()