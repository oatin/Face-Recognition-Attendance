import psutil
import time
from .logger import Logger

class SystemMonitor:
    def __init__(self, config):
        self.logger = Logger(config['logging']['monitoring_log'], 'SystemMonitor')
        self.thresholds = config['monitoring']['thresholds']

    def check_system_health(self):
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        
        health_status = {
            'cpu': cpu_percent < self.thresholds['cpu_max'],
            'memory': memory_percent < self.thresholds['memory_max'],
            'disk': disk_usage < self.thresholds['disk_max']
        }
        
        self._log_health_status(health_status)
        return all(health_status.values())

    def _log_health_status(self, status):
        for resource, is_healthy in status.items():
            if not is_healthy:
                self.logger.warning(f"{resource} usage exceeds threshold")