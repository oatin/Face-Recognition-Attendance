import json
import os
import signal
import sys
from threading import Event
from .scheduler import Scheduler
from .model_manager import ModelManager
from .model import FaceModel
from .face_recognition import FaceRecognition
from .api_communicator import APICommunicator
from .logger import Logger
from .monitoring import SystemMonitor

class MainApplication:
    def __init__(self):
        # Load configurations
        with open('config/config.json', 'r') as f:
            self.config = json.load(f)
            
        # Initialize logger
        self.logger = Logger(self.config['logging']['app_log'], 'MainApp')
        
        # Initialize components
        self.api = APICommunicator(self.config)
        self.model_manager = ModelManager(self.config)
        self.face_model = FaceModel(self.config)
        self.face_recognition = FaceRecognition(self.config, self.face_model)
        self.scheduler = Scheduler(
            self.config, 
            self.api, 
            self.model_manager,
            self.face_recognition
        )
        self.monitor = SystemMonitor(self.config)
        
        # Initialize shutdown event
        self.shutdown_event = Event()

    def setup_signal_handlers(self):
        """Setup handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info("Shutdown signal received")
            self.shutdown_event.set()
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def run(self):
        """Main application loop"""
        try:
            self.setup_signal_handlers()
            self.logger.info("Starting face recognition system")
            
            # Start scheduler
            self.scheduler.start()
            
            # Main loop
            while not self.shutdown_event.is_set():
                # Check system health
                if not self.monitor.check_system_health():
                    self.logger.warning("System health check failed")
                
                # Sleep for monitoring interval
                self.shutdown_event.wait(
                    self.config['monitoring']['check_interval']
                )
                
        except Exception as e:
            self.logger.error(f"Critical error in main loop: {str(e)}")
            raise
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup resources"""
        self.logger.info("Cleaning up resources")
        self.scheduler.stop()
        # Additional cleanup if needed

def main():
    app = MainApplication()
    app.run()

if __name__ == "__main__":
    main()