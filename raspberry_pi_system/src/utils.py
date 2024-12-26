import os
import json
from datetime import datetime, time

def load_config(config_path):
    """Load configuration file"""
    with open(config_path, 'r') as f:
        return json.load(f)

def ensure_directory_exists(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def time_in_range(start: time, end: time, current: time):
    """Check if current time is between start and end"""
    if start <= end:
        return start <= current <= end
    else:  # Over midnight
        return start <= current or current <= end

def format_time(time_obj):
    """Format time object to string"""
    return time_obj.strftime("%H:%M:%S")

def parse_time(time_str):
    """Parse time string to time object"""
    return datetime.strptime(time_str, "%H:%M:%S").time()