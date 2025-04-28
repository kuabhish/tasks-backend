from flask import Blueprint, request
from ..services.team_service import TeamService
from ..middleware.auth_and_log import AuthAndLogMiddleware
from ..utils.responses import success_response, error_response

teams_bp = Blueprint("teams", __name__, url_prefix="/api/v1/teams")
team_service = TeamService()

@teams_bp.route("/create", methods=["POST"])
@AuthAndLogMiddleware.authenticate_and_log
def create_team():
    data = request.get_json()
    result, status_code = team_service.create_team(data)
    if status_code == 201:
        return success_response(data=result, message=result["message"], status_code=status_code)
    return error_response(message=result["error"], status_code=status_code)

@teams_bp.route("/list", methods=["GET"])
@AuthAndLogMiddleware.authenticate_and_log
def list_teams():
    result, status_code = team_service.list_teams()
    if status_code == 200:
        return success_response(data=result, message="Teams fetched successfully", status_code=status_code)
    return error_response(message=result[0]["error"], status_code=status_code)

@teams_bp.route("/<team_id>/members", methods=["POST"])
@AuthAndLogMiddleware.authenticate_and_log
def add_team_member(team_id):
    data = request.get_json()
    result, status_code = team_service.add_team_member(team_id, data)
    if status_code == 201:
        return success_response(data=result, message=result["message"], status_code=status_code)
    return error_response(message=result["error"], status_code=status_code)

@teams_bp.route("/<team_id>/members/<user_id>", methods=["DELETE"])
@AuthAndLogMiddleware.authenticate_and_log
def remove_team_member(team_id, user_id):
    result, status_code = team_service.remove_team_member(team_id, user_id)
    if status_code == 200:
        return success_response(data=result, message=result["message"], status_code=status_code)
    return error_response(message=result["error"], status_code=status_code)