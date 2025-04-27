import logging
from logging.handlers import RotatingFileHandler


# # Application logger
# APPLICATION_LOG_PATH = "logs/application.log"
# app_logger = logging.getLogger("app")
# app_logger.setLevel(logging.INFO)
# handler = logging.StreamHandler()
# handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
# app_logger.addHandler(handler)

# # Request logger
# request_logger = logging.getLogger("request")
# request_logger.setLevel(logging.INFO)
# handler = logging.StreamHandler()
# handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
# request_logger.addHandler(handler)


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
