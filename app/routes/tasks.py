from flask import Blueprint, request
from ..services.task_service import TaskService
from ..middleware.auth_and_log import AuthAndLogMiddleware
from ..utils.responses import success_response, error_response

tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/v1/tasks")
task_service = TaskService()

@tasks_bp.route("/list", methods=["GET"])
@AuthAndLogMiddleware.authenticate_and_log
def list_tasks():
    project_id = request.args.get("project_id")
    result, status_code = task_service.list_tasks(project_id)
    if status_code == 200:
        return success_response(data=result, message="Tasks fetched successfully", status_code=status_code)
    return error_response(message=result[0]["error"], status_code=status_code)

@tasks_bp.route("/create", methods=["POST"])
@AuthAndLogMiddleware.authenticate_and_log
def create_task():
    data = request.get_json()
    result, status_code = task_service.create_task(data)
    if status_code == 201:
        return success_response(data=result, message=result["message"], status_code=status_code)
    return error_response(message=result["error"], status_code=status_code)

@tasks_bp.route("/update/<task_id>", methods=["PUT"])
@AuthAndLogMiddleware.authenticate_and_log
def update_task(task_id):
    data = request.get_json()
    result, status_code = task_service.update_task(task_id, data)
    if status_code == 200:
        return success_response(data=result, message=result["message"], status_code=status_code)
    return error_response(message=result["error"], status_code=status_code)

@tasks_bp.route("/delete/<task_id>", methods=["DELETE"])
@AuthAndLogMiddleware.authenticate_and_log
def delete_task(task_id):
    result, status_code = task_service.delete_task(task_id)
    if status_code == 200:
        return success_response(data=result, message=result["message"], status_code=status_code)
    return error_response(message=result["error"], status_code=status_code)

@tasks_bp.route("/subtasks/create", methods=["POST"])
@AuthAndLogMiddleware.authenticate_and_log
def create_subtask():
    data = request.get_json()
    result, status_code = task_service.create_subtask(data)
    if status_code == 201:
        return success_response(data=result, message=result["message"], status_code=status_code)
    return error_response(message=result["error"], status_code=status_code)

@tasks_bp.route("/subtasks/update/<subtask_id>", methods=["PUT"])
@AuthAndLogMiddleware.authenticate_and_log
def update_subtask(subtask_id):
    data = request.get_json()
    result, status_code = task_service.update_subtask(subtask_id, data)
    if status_code == 200:
        return success_response(data=result, message=result["message"], status_code=status_code)
    return error_response(message=result["error"], status_code=status_code)

@tasks_bp.route("/subtasks/delete/<subtask_id>", methods=["DELETE"])
@AuthAndLogMiddleware.authenticate_and_log
def delete_subtask(subtask_id):
    result, status_code = task_service.delete_subtask(subtask_id)
    if status_code == 200:
        return success_response(data=result, message=result["message"], status_code=status_code)
    return error_response(message=result["error"], status_code=status_code)
