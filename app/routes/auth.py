from flask import Blueprint, request
from ..services.auth_service import AuthService
from ..utils.responses import success_response, error_response

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