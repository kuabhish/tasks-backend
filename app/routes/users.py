from flask import Blueprint
from ..services.user_service import UserService
from ..middleware.auth_and_log import AuthAndLogMiddleware
from ..utils.responses import success_response, error_response

users_bp = Blueprint("users", __name__, url_prefix="/api/v1/users")
user_service = UserService()

@users_bp.route("/<user_id>", methods=["GET"])
@AuthAndLogMiddleware.authenticate_and_log
def get_user(user_id):
    result, status_code = user_service.get_user(user_id)
    if status_code == 200:
        return success_response(data=result["data"], message=result["message"], status_code=status_code)
    return error_response(message=result["error"], status_code=status_code)

@users_bp.route("/list", methods=["GET"])
@AuthAndLogMiddleware.authenticate_and_log
def list_users():
    result, status_code = user_service.list_users()
    if status_code == 200:
        return success_response(data=result, message="Users fetched successfully", status_code=status_code)
    return error_response(message=result[0]["error"], status_code=status_code)