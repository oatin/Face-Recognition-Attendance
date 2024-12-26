import logging
import logging.config
import os
import json

class Logger:
    def __init__(self, config_file, logger_name):
        self.logger = self._setup_logger(config_file, logger_name)
    
    def _setup_logger(self, config_file, logger_name):
        """Setup logger based on the given configuration file"""
        if not os.path.exists('logs'):
            os.makedirs('logs')

        with open(config_file, 'r') as f:
            config = json.load(f)
        
        logging.config.dictConfig(config)
        logger = logging.getLogger(logger_name)
        return logger
    
    def info(self, message):
        self.logger.info(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def critical(self, message):
        self.logger.critical(message)
    
    def debug(self, message):
        self.logger.debug(message)
