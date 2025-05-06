### app/ utils/logger.py
import logging
from logging.handlers import RotatingFileHandler
from functools import wraps
import time



APPLICATION_LOG_PATH = "logs/application.log"

appHandler = RotatingFileHandler(
    APPLICATION_LOG_PATH, maxBytes=100000, backupCount=1)
appHandler.setFormatter(logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"))

app_logger = logging.getLogger("app_logger")
app_logger.setLevel(logging.INFO)
app_logger.addHandler(appHandler)





REQUEST_LOG_PATH = "logs/request.log"

requestHandler = RotatingFileHandler(REQUEST_LOG_PATH, maxBytes=100000, backupCount=1)
requestHandler.setFormatter(logging.Formatter("%(message)s"))


request_logger = logging.getLogger("request_logger")
request_logger.setLevel(logging.INFO)
request_logger.addHandler(requestHandler)



RTIME_LOG_PATH = "logs/rtime.log"
rtimeHandler = RotatingFileHandler(RTIME_LOG_PATH, maxBytes=100000, backupCount=1)
rtimeHandler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
rtime_logger = logging.getLogger("rtime_logger")
rtime_logger.setLevel(logging.INFO)
rtime_logger.addHandler(rtimeHandler)

def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()  # High-precision timer
        try:
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            execution_time_ms = (end_time - start_time) * 1000  # Convert to milliseconds
            rtime_logger.info(
                f"Function: {func.__qualname__}, "
                f"ExecutionTimeMs: {execution_time_ms:.2f}"
            )
            return result
        except Exception as e:
            end_time = time.perf_counter()
            execution_time_ms = (end_time - start_time) * 1000
            rtime_logger.error(
                f"Function: {func.__qualname__}, "
                f"ExecutionTimeMs: {execution_time_ms:.2f}, "
                f"Error: {str(e)}"
            )
            raise
    return wrapper
