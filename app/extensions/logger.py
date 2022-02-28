import os
import time
from loguru import logger


def log_init():
    LOG_PATH = "../logs"
    os.makedirs(LOG_PATH, exist_ok=True)
    info_log_path = os.path.join(LOG_PATH, 'info')
    error_log_path = os.path.join(LOG_PATH, 'error')
    os.makedirs(info_log_path, exist_ok=True)
    os.makedirs(error_log_path, exist_ok=True)
    log_path_info = os.path.join(info_log_path, f'{time.strftime("%Y-%m-%d")}_info.log')
    log_path_error = os.path.join(error_log_path, f'{time.strftime("%Y-%m-%d")}_error.log')
    logger.add(log_path_error, rotation="12:00", retention="2 days", enqueue=True, level="ERROR")
    logger.add(log_path_info, rotation="12:00", retention="2 days", enqueue=True, level="INFO")
