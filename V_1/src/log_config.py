import logging
import os
import sys
from datetime import datetime

def setup_logging(log_level=logging.INFO):
    """
    Set up logging confisguration for the application
    :param log_level: The minimum logging level to record
    :return: The configured logger
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create a log file with timestamp
    log_file = os.path.join(logs_dir, f"pss_companion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Clear any existing handlers
    logger.handlers = []
    
    # Create file handler for logging to a file
    file_handler = logging.FileHandler(log_file)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    file_handler.setLevel(log_level)
    logger.addHandler(file_handler)
    
    # Create console handler for logging to console
    console_handler = logging.StreamHandler(sys.stdout)
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)
    
    # Create a specific logger for the application
    app_logger = logging.getLogger('pss_companion.main')
    
    # Log that the logging system is set up
    app_logger.info(f"Logging system initialized. Log file: {log_file}")

    cleanup_logs()

    app_logger.info("Log cleanup complete")
    
    return app_logger, log_file

def cleanup_logs():
    """
    Remove old log files from the logs directory
    Keep the last 5 log files
    """
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
    log_files.sort()
    
    # Keep the last 5 log files
    for f in log_files[:-5]:
        os.remove(os.path.join(logs_dir, f))
        
    return len(log_files) - 5