from flask import Blueprint, current_app, request
from ..services.auth_service import AuthService
from ..utils.responses import success_response, error_response
from ..middleware.auth_and_log import AuthAndLogMiddleware
import jwt
from ..utils.logger import app_logger
import traceback


auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")
auth_service = AuthService()

@auth_bp.route("/register", methods=["POST"])
def register():
    print("REGISTER API HIT", flush=True)
    data = request.get_json()
    result, status_code = auth_service.register(data)
    print("DATA RECEIVED:", data, flush=True)
    if status_code == 201:
        return success_response(data=result, message=result["message"], status_code=status_code)
    return error_response(message=result["error"], status_code=status_code)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    result, status_code = auth_service.login(data)
    if status_code == 200:
        return success_response(data=result, message=result["message"], status_code=status_code)
    return error_response(message=result["error"], status_code=status_code)

@auth_bp.route("/refresh", methods=["POST"])
def refresh_token():
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return error_response(message="Missing or invalid token", status_code=401)

        token = auth_header.split(" ")[1]
        # Decode the token to extract user info
        try:
            decoded = jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
            user_id = decoded["user_id"]
            role = decoded["role"]
            customer_id = decoded["customer_id"]
        except jwt.ExpiredSignatureError:
            return error_response(message="Token has expired", status_code=401)
        except jwt.InvalidTokenError:
            return error_response(message="Invalid token", status_code=401)

        # Generate a new token
        new_token = AuthAndLogMiddleware.generate_token(user_id, role, customer_id)
        return success_response(
            data={"token": new_token},
            message="Token refreshed successfully",
            status_code=200
        )
    except Exception as e:
        app_logger.error({
            "function": "refresh_token",
            "error": str(e),
            "traceback": traceback.format_exc()
        })
        return error_response(message=f"Failed to refresh token: {str(e)}", status_code=500)