from fastapi import FastAPI, BackgroundTasks, HTTPException
from datetime import datetime, time
import pytz
import os
from utils.data_loader import DataLoader
from utils.model import FaceRecognitionModel
import logging
import uvicorn
from fastapi.responses import FileResponse

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Training time window
TRAINING_START = time(18, 0)  # 18:00
TRAINING_END = time(6, 0)     # 06:00

def is_training_time():
    current_time = datetime.now(pytz.UTC).time()
    if TRAINING_START < TRAINING_END:
        return TRAINING_START <= current_time <= TRAINING_END
    else:  # Handle overnight window
        return current_time >= TRAINING_START or current_time <= TRAINING_END

async def train_course_model(course_id: int):
    try:
        # Initialize data loader and load course data
        data_loader = DataLoader()
        X, y, student_ids = data_loader.load_course_data(course_id)
        
        if len(X) == 0:
            logger.error(f"No valid training images found for course {course_id}")
            return
            
        # Initialize and train model
        model = FaceRecognitionModel(num_classes=len(set(y)))
        model_path = f"models/course_{course_id}_{datetime.now().strftime('%Y%m%d')}"
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Train the model
        trained_model, history = model.train(X, y, model_path=model_path)
        
        # Save model info to database
        data_loader.save_model_info(course_id, model_path, student_ids)
        
        logger.info(f"Successfully trained model for course {course_id}")
        
    except Exception as e:
        logger.error(f"Error training model for course {course_id}: {str(e)}")

@app.post("/train/{course_id}")
async def trigger_training(course_id: int, background_tasks: BackgroundTasks):
    if not is_training_time():
        raise HTTPException(
            status_code=403,
            detail="Training is only allowed between 18:00 and 06:00"
        )
    
    background_tasks.add_task(train_course_model, course_id)
    return {"message": f"Training started for course {course_id}"}

@app.get("/model/download/{device_id}")
async def get_device_model(device_id: int):
    conn = DataLoader().get_connection()
    cur = conn.cursor()
    
    try:
        # Get pending model assignment
        cur.execute("""
            SELECT fm.model_path 
            FROM face_model_assignment fma
            JOIN face_model fm ON fma.model_id = fm.id
            WHERE fma.device_id = %s AND fma.status = 'pending'
            ORDER BY fm.created_at DESC
            LIMIT 1
        """, (device_id,))
        
        result = cur.fetchone()
        if not result:
            raise HTTPException(
                status_code=404,
                detail="No pending model assignments"
            )
            
        model_path = result[0]
        
        # Update assignment status
        cur.execute("""
            UPDATE face_model_assignment
            SET status = 'downloaded', downloaded_at = CURRENT_TIMESTAMP
            WHERE device_id = %s AND status = 'pending'
        """, (device_id,))
        
        conn.commit()
        
        return FileResponse(model_path)
        
    finally:
        cur.close()
        conn.close()