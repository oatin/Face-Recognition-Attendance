from datetime import datetime
import schedule
import time
from threading import Thread, Event
from .logger import Logger
from .exceptions import APIConnectionError

class Scheduler:
    def __init__(self, config, api_communicator, model_manager, face_recognition):
        self.config = config
        self.api = api_communicator
        self.model_manager = model_manager
        self.face_recognition = face_recognition
        self.logger = Logger(config['logging']['app_log'], 'Scheduler')
        
        self.current_schedule = None
        self.running = False
        self.stop_event = Event()
        self.thread = None

    def start(self):
        """Start scheduler in separate thread"""
        self.running = True
        self.stop_event.clear()
        self.thread = Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        self.logger.info("Scheduler started")

    def stop(self):
        """Stop scheduler"""
        self.running = False
        self.stop_event.set()
        if self.thread:
            self.thread.join()
        self.logger.info("Scheduler stopped")

    def _run(self):
        """Main scheduler loop"""
        # Schedule periodic checks
        schedule.every(self.config['scheduler']['check_interval']).seconds.do(
            self.check_schedule
        )
        
        while self.running:
            schedule.run_pending()
            self.stop_event.wait(1)  # Check stop event every second

    def check_schedule(self):
        """Check current schedule and update if needed"""
        try:
            current_time = datetime.now()
            day_of_week = current_time.strftime('%A').upper()
            
            # Get device info
            device_info = self.api.get_device_info(
                self.config['device']['mac_address']
            )
            if not device_info:
                raise APIConnectionError("Failed to get device info")
            
            # Get current schedules
            schedules = self.api.get_current_schedule(
                device_info['room'],
                day_of_week
            )
            
            if schedules:
                self._process_schedules(schedules, current_time)
            else:
                self._handle_no_schedule()
                
        except Exception as e:
            self.logger.error(f"Schedule check error: {str(e)}")

    def _process_schedules(self, schedules, current_time):
        """Process schedule list and update if needed"""
        for schedule in schedules:
            start_time = datetime.strptime(
                schedule['start_time'],
                '%H:%M:%S'
            ).time()
            end_time = datetime.strptime(
                schedule['end_time'],
                '%H:%M:%S'
            ).time()
            
            if start_time <= current_time.time() <= end_time:
                if (self.current_schedule is None or 
                    self.current_schedule['id'] != schedule['id']):
                    self._update_schedule(schedule)
                return
        
        self._handle_no_schedule()

    def _update_schedule(self, schedule):
        """Update current schedule and model"""
        try:
            self.current_schedule = schedule
            self.logger.info(f"Updated schedule: {schedule['course']}")
            
            # Get and update model
            model_info = self.api.get_face_model(schedule['course'])
            if model_info:
                # Download model if needed
                model_path = self.model_manager.download_model(
                    model_info['model_path'],
                    model_info['model_version']
                )
                
                # Activate model
                current_model_path = self.model_manager.activate_model(model_path)
                
                # Load model
                self.face_recognition.model.load_model(current_model_path)
                
                # Clean up old models
                self.model_manager.cleanup_old_models()
            
        except Exception as e:
            self.logger.error(f"Schedule update error: {str(e)}")

    def _handle_no_schedule(self):
        """Handle case when no schedule is active"""
        if self.current_schedule is not None:
            self.current_schedule = None
            self.logger.info("No active schedule")