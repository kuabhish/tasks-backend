import time
import jwt
from flask import request, current_app
from functools import wraps
from typing import Callable, Tuple
from ..utils.logger import request_logger, app_logger
from datetime import datetime, timedelta
import traceback

class AuthAndLogMiddleware:
    @staticmethod
    def generate_token(user_id: str, role: str, customer_id: str, expires_in: int = 3600) -> str:
        payload = {
            "user_id": user_id,
            "role": role,
            "customer_id": customer_id,
            "exp": datetime.utcnow() + timedelta(seconds=expires_in),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")

    @staticmethod
    def authenticate_and_log(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            request_info = {
                "event": "before_request",
                "method": request.method,
                "path": request.path,
                "data": request.get_data(as_text=True),
                "timestamp": time.time()
            }

            token = request.headers.get("Authorization")
            if not token:
                request_info["error"] = "No token provided"
                request_logger.warning(request_info)
                return {"message": "Authentication token is missing"}, 401

            if token.startswith("Bearer "):
                token = token[7:]

            try:
                decoded = jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
                request.decoded = decoded
                request_info["decoded"] = decoded
            except jwt.ExpiredSignatureError:
                request_info["error"] = "Token has expired"
                request_logger.error(request_info)
                return {"message": "Token has expired"}, 401
            except jwt.InvalidTokenError as e:
                request_info["error"] = str(e)
                request_logger.error(request_info)
                return {"message": "Invalid token", "details": str(e)}, 401

            request_logger.info(request_info)
            return f(*args, **kwargs)

        return decorated_function