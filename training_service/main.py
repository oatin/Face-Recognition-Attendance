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
        # Initialize and authenticate
        loader = DataLoader(base_url="http://app:8000")
        loader.authenticate("a", "a")

        # Load course data
        X, y = loader.load_course_data(course_id=course_id)

        model = FaceRecognitionModel(num_classes=len(set(y)))
        model_path = f"models/course_{course_id}_.keras"
        os.makedirs(os.path.dirname(model_path), exist_ok=True)

        # Train the model
        trained_model, history = model.train(X, y, model_path=f"{model_path}")
        
        # Save model info
        success = loader.save_model_info(
            course_id=course_id,
            description="",
            model_path=model_path
        )
        logger.info(f"Successfully trained model for course {course_id}")
        
    except Exception as e:
        logger.error(f"Error training model for course {course_id}: {str(e)}")
        raise  # Re-raise the exception for debugging if needed

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
    """
    Get the latest model for a specific device.
    """
    downloader = DataLoader()
    
    # Authenticate - you might want to set these values from environment variables
    if not downloader.authenticate("a", "a"):
        raise HTTPException(
            status_code=500,
            detail="Failed to authenticate with API"
        )
    
    # Get latest model path
    model_path = downloader.get_latest_model_path(device_id)
    if not model_path:
        raise HTTPException(
            status_code=404,
            detail="No pending model assignments"
        )
    
    # Verify file exists
    if not os.path.exists(model_path):
        raise HTTPException(
            status_code=404,
            detail="Model file not found"
        )
    
    # Update assignment status
    if not downloader.update_assignment_status(device_id):
        print(f"Warning: Failed to update assignment status for device {device_id}")
    
    return FileResponse(model_path)