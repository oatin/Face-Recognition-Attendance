from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from datetime import datetime, time
import pytz
import os
from utils.data_loader import DataLoader
from utils.model import FaceRecognitionModel
import logging
from typing import Tuple
import json

class ModelTrainer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    @staticmethod
    def is_training_time() -> bool:
        TRAINING_START = time(18, 0)  # 18:00
        TRAINING_END = time(6, 0)     # 06:00
        
        current_time = datetime.now(pytz.UTC).time()
        if TRAINING_START < TRAINING_END:
            return TRAINING_START <= current_time <= TRAINING_END
        return current_time >= TRAINING_START or current_time <= TRAINING_END

    async def train_course_model(self, course_id: int) -> None:
        try:
            loader = DataLoader(base_url="http://app:8000")
            loader.authenticate("a", "a")

            X, y, inverse_label_map = loader.load_course_data(course_id=course_id)
            model = FaceRecognitionModel(num_classes=len(set(y)))
            model_path = f"models/course_{course_id}_.keras"
            label_map = f"models/label_map_{course_id}.json"
            os.makedirs(os.path.dirname(model_path), exist_ok=True)

            trained_model, history = model.train(X, y, model_path=model_path)
            success = loader.save_model_info(
                course_id=course_id,
                description="",
                model_path=model_path,
                inverse_label_map=label_map
            )
            
            with open(label_map, 'w') as f:
                json.dump(inverse_label_map, f)

            self.logger.info(f"Successfully trained model for course {course_id}")
            
        except Exception as e:
            self.logger.error(
                f"Error training model for course {course_id}: {str(e)}"
            )
            raise

app = FastAPI()
trainer = ModelTrainer()

@app.post("/train/{course_id}")
async def trigger_training(course_id: int, background_tasks: BackgroundTasks):
    # if not trainer.is_training_time():
    #     raise HTTPException(
    #         status_code=403,
    #         detail="Training is only allowed between 18:00 and 06:00"
    #     )
    
    background_tasks.add_task(trainer.train_course_model, course_id)
    return {"message": f"Training started for course {course_id}"}

@app.get("/download/{course_id}")
async def download_model(course_id: int):
    try:
        loader = DataLoader(base_url="http://app:8000")
        loader.authenticate("a", "a")

        response = loader.api_client.make_request(
            loader.api_client.endpoints.face_model,
            params={'course_id': course_id}
        )

        if not response or "results" not in response or not response["results"]:
            raise HTTPException(
                status_code=404, 
                detail=f"No model found for course_id {course_id}."
            )

        model_data = response["results"][0]
        model_path = model_data.get("model_path")

        if not model_path:
            raise HTTPException(status_code=404, detail="Model path not provided.")

        if not os.path.exists(model_path):
            raise HTTPException(
                status_code=404, 
                detail=f"Model file '{model_path}' does not exist."
            )

        return FileResponse(
            path=model_path,
            filename=os.path.basename(model_path),
            media_type="application/octet-stream"
        )

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(e)}"}
        )
    
@app.get("/download_label_map/{course_id}")
async def download_label_map(course_id: int):
    try:
        loader = DataLoader(base_url="http://app:8000")
        loader.authenticate("a", "a")

        response = loader.api_client.make_request(
            loader.api_client.endpoints.face_model,
            params={'course_id': course_id}
        )

        if not response or "results" not in response or not response["results"]:
            raise HTTPException(
                status_code=404,
                detail=f"No label map found for course_id {course_id}."
            )

        model_data = response["results"][0]
        inverse_label_map_path = model_data.get("inverse_label_map")

        if not inverse_label_map_path or not os.path.exists(inverse_label_map_path):
            raise HTTPException(
                status_code=404,
                detail=f"Inverse label map file '{inverse_label_map_path}' does not exist."
            )

        with open(inverse_label_map_path, "r") as f:
            inverse_label_map = json.load(f)

        return JSONResponse(content=inverse_label_map)

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(e)}"}
        )