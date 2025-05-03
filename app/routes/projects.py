# app/routes/projects.py
from flask import Blueprint, request
from ..services.project_service import ProjectService
from ..middleware.auth_and_log import AuthAndLogMiddleware
from ..utils.responses import success_response, error_response

projects_bp = Blueprint("projects", __name__, url_prefix="/api/v1/projects")
project_service = ProjectService()

@projects_bp.route("/list", methods=["GET"])
@AuthAndLogMiddleware.authenticate_and_log
def list_projects():
    result, status_code = project_service.list_projects()
    if status_code == 200:
        return success_response(data=result, message="Projects fetched successfully", status_code=status_code)
    return error_response(message=result[0]["error"], status_code=status_code)

@projects_bp.route("/create", methods=["POST"])
@AuthAndLogMiddleware.authenticate_and_log
def create_project():
    data = request.get_json()
    result, status_code = project_service.create_project(data)
    if status_code == 201:
        return success_response(data=result, message=result["message"], status_code=status_code)
    return error_response(message=result["error"], status_code=status_code)


@projects_bp.route("/update/<project_id>", methods=["PUT"])
@AuthAndLogMiddleware.authenticate_and_log
def update_project(project_id):
    data = request.get_json()
    result, status_code = project_service.update_project(project_id, data)
    if status_code == 200:
        return success_response(data=result, message=result["message"], status_code=status_code)
    return error_response(message=result["error"], status_code=status_code)

@projects_bp.route("/archive/<project_id>", methods=["DELETE"])
@AuthAndLogMiddleware.authenticate_and_log
def archive_project(project_id):
    result, status_code = project_service.archive_project(project_id)
    if status_code == 200:
        return success_response(data=result, message=result["message"], status_code=status_code)
    return error_response(message=result["error"], status_code=status_code)


@projects_bp.route("/<project_id>/stats", methods=["GET"])
@AuthAndLogMiddleware.authenticate_and_log
def project_stats(project_id):
    result, status_code = project_service.get_project_stats(project_id)
    if status_code == 200:
        return success_response(data=result, message="Success", status_code=status_code)
    return error_response(message=result["error"], status_code=status_code)

