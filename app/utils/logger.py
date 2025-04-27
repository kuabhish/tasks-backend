import logging

# Application logger
app_logger = logging.getLogger("app")
app_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
app_logger.addHandler(handler)

# Request logger
request_logger = logging.getLogger("request")
request_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
request_logger.addHandler(handler)