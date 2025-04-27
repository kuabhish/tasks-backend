from flask import Blueprint, request
from ..services.time_entry_service import TimeEntryService
from ..middleware.auth_and_log import AuthAndLogMiddleware
from ..utils.responses import success_response, error_response

time_entries_bp = Blueprint("time_entries", __name__, url_prefix="/api/v1/time-entries")
time_entry_service = TimeEntryService()

@time_entries_bp.route("/list", methods=["GET"])
@AuthAndLogMiddleware.authenticate_and_log
def list_time_entries():
    project_id = request.args.get("project_id")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    result, status_code = time_entry_service.list_time_entries(project_id, start_date, end_date)
    if status_code == 200:
        return success_response(data=result, message="Time entries fetched successfully", status_code=status_code)
    return error_response(message=result[0]["error"], status_code=status_code)

@time_entries_bp.route("/create", methods=["POST"])
@AuthAndLogMiddleware.authenticate_and_log
def create_time_entry():
    data = request.get_json()
    result, status_code = time_entry_service.create_time_entry(data)
    if status_code == 201:
        return success_response(data=result, message=result["message"], status_code=status_code)
    return error_response(message=result["error"], status_code=status_code)