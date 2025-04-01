from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from datetime import datetime, time
import pytz
import os
import json
import asyncio
import logging
from typing import Tuple

from utils.data_loader import DataLoader
from utils.model import FaceRecognitionModel

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
# ตั้งค่า Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ตั้งค่า FastAPI
app = FastAPI()

# ตั้งค่าโซนเวลาไทย
tz_bangkok = pytz.timezone('Asia/Bangkok')

class ModelTrainer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    async def train_course_model(self, course_id: int) -> None:
        try:
            loader = DataLoader(base_url="http://app:8000")
            loader.authenticate("a", "a")

            # ดึงข้อมูล Enrollment ของ course_id
            enrollments = loader.api_client.make_request(
                loader.api_client.endpoints.enrollment,
                params={'course_id': course_id}
            )

            if not enrollments or "results" not in enrollments:
                self.logger.warning(f"Skipping training for course {course_id} - Unable to fetch enrollment data")
                return

            enrollment_count = len(enrollments.get('results', []))

            # ดึง FaceModel ของ course_id
            existing_models = loader.api_client.make_request(
                loader.api_client.endpoints.face_model,
                params={'course_id': course_id}
            )

            if existing_models and existing_models.get('results', []):
                face_model = existing_models['results'][0]
                last_enrollment_count = face_model.get("last_enrollment_count", 0)

                if enrollment_count == last_enrollment_count:
                    self.logger.info(f"Skipping training for course {course_id} - No new enrollments ({enrollment_count})")
                    return

            # โหลดข้อมูลการฝึก
            X, y, inverse_label_map = loader.load_course_data(course_id=course_id)
            if X.size == 0 or y.size == 0:
                self.logger.info(f"Skipping training for course {course_id} - No training data found")
                return

            model = FaceRecognitionModel(num_classes=len(set(y)))

            model_path = f"models/course_{course_id}.keras"
            label_map = f"models/label_map_{course_id}.json"

            os.makedirs(os.path.dirname(model_path), exist_ok=True)

            trained_model, history = model.train(X, y, model_path=model_path)

            # อัปเดตค่า Enrollment ล่าสุดที่ใช้เทรน
            model_data = {
                "course": course_id,
                "description": "",
                "model_path": model_path,
                "inverse_label_map": label_map,
                "last_enrollment_count": enrollment_count
            }

            if existing_models and existing_models.get('results', []):
                model_data['model_version'] = face_model.get('model_version', 0) + 1
                response = loader.api_client.make_request(
                    f"{loader.api_client.endpoints.face_model}{face_model['id']}/",
                    method='patch',
                    json=model_data
                )
            else:
                model_data['model_version'] = 1
                response = loader.api_client.make_request(
                    loader.api_client.endpoints.face_model,
                    method='post',
                    json=model_data
                )

            with open(label_map, 'w') as f:
                json.dump(inverse_label_map, f)

            self.logger.info(f"Successfully trained model for course {course_id} - {enrollment_count} enrollments")

        except Exception as e:
            self.logger.error(f"Error training model for course {course_id}: {str(e)}")
            raise

trainer = ModelTrainer()

async def train_all_courses():
    loader = DataLoader(base_url="http://app:8000")
    loader.authenticate("a", "a")

    courses = loader.api_client.make_request(loader.api_client.endpoints.course)

    if not courses or "results" not in courses:
        print("No courses found. Skipping training.")
        return

    for course in courses["results"]:
        course_id = course["id"]
        print(f"Training started for course {course_id}")
        await trainer.train_course_model(course_id)

def setup_scheduler():
    scheduler = BackgroundScheduler(timezone=tz_bangkok)

    last_hour = None
    last_minute = None

    def update_scheduler():
        nonlocal last_hour, last_minute 
        try:  
            loader = DataLoader(base_url="http://app:8000")
            loader.authenticate("a", "a")
            config = loader.api_client.make_request(loader.api_client.endpoints.config)

            if not config:
                print("No config data found. Skipping this cycle.")
                return

            config_dict = {item['key']: item['value'] for item in config if 'key' in item and 'value' in item}

            hour = int(config_dict.get('hour', 18))
            minute = int(config_dict.get('minute', 0))

            if hour != last_hour or minute != last_minute:
                print(f"Updating Scheduler to {hour}:{minute}")

                try:
                    scheduler.remove_job('train_all_courses_job')
                except Exception as e:
                    print("No existing job or error removing job:", e)

                scheduler.add_job(
                    lambda: asyncio.run(train_all_courses()),
                    CronTrigger(hour=hour, minute=minute, timezone=tz_bangkok),
                    id='train_all_courses_job'
                )

                last_hour = hour
                last_minute = minute

        except Exception as e:
            print(f"Error in update_scheduler: {e}")

    scheduler.add_job(update_scheduler, IntervalTrigger(minutes=1))

    scheduler.start()
    print("Scheduler started and will check for config updates every 1 minute.")

setup_scheduler()

@app.post("/train/{course_id}")
async def trigger_training(course_id: int, background_tasks: BackgroundTasks):
    loader = DataLoader(base_url="http://app:8000")
    loader.authenticate("a", "a")

    enrollments = loader.api_client.make_request(
        loader.api_client.endpoints.enrollment,
        params={'course_id': course_id}
    )

    if not enrollments or "results" not in enrollments:
        return JSONResponse(
            status_code=400,
            content={"message": f"Skipping training for course {course_id} - Unable to fetch enrollment data"}
        )

    enrollment_count = len(enrollments.get('results', []))

    existing_models = loader.api_client.make_request(
        loader.api_client.endpoints.face_model,
        params={'course_id': course_id}
    )

    if existing_models and existing_models.get('results', []):
        face_model = existing_models['results'][0]
        last_enrollment_count = face_model.get("last_enrollment_count", 0)

        if enrollment_count == last_enrollment_count:
            return JSONResponse(
                status_code=400,
                content={"message": f"Skipping training for course {course_id} - No new enrollments ({enrollment_count})"}
            )

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
