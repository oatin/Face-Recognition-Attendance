import os
import numpy as np
import psycopg2
from .preprocess import FacePreprocessor

class DataLoader:
    def __init__(self, db_url="postgres://admin:a@db:5432/db_face_scan_attendance"):
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
                LEFT JOIN public.courses_enrollment e ON s.student_id = e.student_id AND e.course_id = %s;
            """
            cur.execute(query, (course_id,))
            results = cur.fetchall()
            
            X = []  # Preprocessed images
            y = []  # Labels
            student_ids = []  # Keep track of student IDs
            
            print(f"Processing {len(results)} images for course {course_id}")
            
            for image_path, student_id in results:
                processed_face = self.preprocessor.preprocess_image(f"media/{image_path}")
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
        model_version = 1
        description = ""
        try:
            # Create new model record
            cur.execute("""
                INSERT INTO public.devices_facemodel (id, model_version, created_at, description, model_path)
                VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s)
                RETURNING id
            """, (model_id, model_version, description, model_path))
            
            model_id = cur.fetchone()[0]
            
            # Update device assignments
            cur.execute("""
                INSERT INTO public.devices_facemodelassignment (id, assigned_at, device_id, model_id)
                SELECT d.id, CURRENT_TIMESTAMP, d.id, %s
                FROM public.devices_device d
                JOIN public.attendance_schedule s ON d.room_id = s.room_id
                WHERE s.course_id = %s
            """, (model_id, course_id))
            
            conn.commit()
            return model_id
            
        finally:
            cur.close()
            conn.close()