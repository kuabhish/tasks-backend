from flask import request
from ..models.task import Task
from ..models.subtask import Subtask
from ..models.project import Project
from ..models.user import User
from ..models.team import Team
from ..utils.logger import app_logger
import traceback
from typing import Tuple, List
from datetime import datetime
from uuid import uuid4
from .. import db

class TaskService:
    @staticmethod
    def list_tasks(project_id: str = None) -> Tuple[List[dict], int]:
        try:
            user_id = request.decoded.get("user_id")
            customer_id = request.decoded.get("customer_id")
            role = request.decoded.get("role")
            if not user_id or not customer_id:
                return [{"error": "Unauthorized: Invalid token data"}], 401
            query = Task.query.filter_by(customer_id=customer_id)
            if project_id:
                query = query.filter_by(project_id=project_id)
            if role == "Team Member":
                query = query.join(Subtask, Task.id == Subtask.task_id).filter(Subtask.assigned_user_id == user_id)
            tasks = query.all()
            task_dicts = []
            for task in tasks:
                task_dict = task.to_dict()
                subtasks = Subtask.query.filter_by(task_id=task.id).all()
                task_dict['subtasks'] = [subtask.to_dict() for subtask in subtasks]
                completed = len([s for s in subtasks if s.status == 'Completed'])
                task_dict['completion_percentage'] = round((completed / len(subtasks) * 100) if subtasks else 0)
                task_dicts.append(task_dict)
            return task_dicts, 200
        except Exception as e:
            app_logger.error({
                "function": "TaskService.list_tasks",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            return [{"error": f"Failed to fetch tasks: {str(e)}"}], 500

    @staticmethod
    def create_task(data: dict) -> Tuple[dict, int]:
        try:
            required_fields = ["title", "status", "project_id"]
            if not all(field in data for field in required_fields):
                return {"error": "Missing required fields"}, 400

            user_id = request.decoded.get("user_id")
            customer_id = request.decoded.get("customer_id")
            role = request.decoded.get("role")

            if not user_id or not customer_id:
                return {"error": "Unauthorized: Invalid token data"}, 401

            if role not in ["Admin", "Project Manager"]:
                return {"error": "Insufficient permissions"}, 403

            project = Project.query.filter_by(id=data["project_id"], customer_id=customer_id).first()
            if not project:
                return {"error": "Project not found or unauthorized"}, 404

            task = Task(
                id=str(uuid4()),
                customer_id=customer_id,
                project_id=data["project_id"],
                category_id=data.get("category_id"),
                title=data["title"],
                description=data.get("description", ""),
                status=data["status"],
                priority=data.get("priority", "Medium"),
                due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
                tags=data.get("tags", []),
                estimated_duration=data.get("estimated_duration"),
                actual_duration=data.get("actual_duration", 0),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(task)
            db.session.commit()

            task_dict = task.to_dict()
            task_dict['subtasks'] = []
            return {"message": "Task created successfully", "task": task_dict}, 201

        except Exception as e:
            app_logger.error({
                "function": "TaskService.create_task",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            db.session.rollback()
            return {"error": f"Failed to create task: {str(e)}"}, 500

    @staticmethod
    def update_task(task_id: str, data: dict) -> Tuple[dict, int]:
        try:
            user_id = request.decoded.get("user_id")
            customer_id = request.decoded.get("customer_id")
            role = request.decoded.get("role")

            if not user_id or not customer_id:
                return {"error": "Unauthorized: Invalid token data"}, 401

            if role not in ["Admin", "Project Manager"]:
                return {"error": "Insufficient permissions"}, 403

            task = Task.query.filter_by(id=task_id, customer_id=customer_id).first()
            if not task:
                return {"error": "Task not found or unauthorized"}, 404

            # Update fields if provided
            if "title" in data:
                task.title = data["title"]
            if "description" in data:
                task.description = data.get("description", "")
            if "status" in data:
                task.status = data["status"]
                # Set end_date when status is changed to Completed
                if data["status"] == "Completed" and not task.end_date:
                    task.end_date = datetime.utcnow()
                # Clear end_date if status is changed from Completed to something else
                elif data["status"] != "Completed" and task.end_date:
                    task.end_date = None
            if "priority" in data:
                task.priority = data["priority"]
            if "due_date" in data:
                task.due_date = datetime.fromisoformat(data["due_date"]) if data["due_date"] else None
            if "tags" in data:
                task.tags = data.get("tags", [])
            if "estimated_duration" in data:
                task.estimated_duration = data.get("estimated_duration")
            if "actual_duration" in data:
                task.actual_duration = data.get("actual_duration", 0)
            if "category_id" in data:
                task.category_id = data.get("category_id")

            task.updated_at = datetime.utcnow()
            db.session.commit()

            task_dict = task.to_dict()
            subtasks = Subtask.query.filter_by(task_id=task.id).all()
            task_dict['subtasks'] = [subtask.to_dict() for subtask in subtasks]
            return {"message": "Task updated successfully", "task": task_dict}, 200

        except Exception as e:
            app_logger.error({
                "function": "TaskService.update_task",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            db.session.rollback()
            return {"error": f"Failed to update task: {str(e)}"}, 500

    @staticmethod
    def delete_task(task_id: str) -> Tuple[dict, int]:
        try:
            user_id = request.decoded.get("user_id")
            customer_id = request.decoded.get("customer_id")
            role = request.decoded.get("role")

            if not user_id or not customer_id:
                return {"error": "Unauthorized: Invalid token data"}, 401

            if role not in ["Admin", "Project Manager"]:
                return {"error": "Insufficient permissions"}, 403

            task = Task.query.filter_by(id=task_id, customer_id=customer_id).first()
            if not task:
                return {"error": "Task not found or unauthorized"}, 404

            db.session.delete(task)
            db.session.commit()

            return {"message": "Task deleted successfully"}, 200

        except Exception as e:
            app_logger.error({
                "function": "TaskService.delete_task",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            db.session.rollback()
            return {"error": f"Failed to delete task: {str(e)}"}, 500

    @staticmethod
    def create_subtask(data: dict) -> Tuple[dict, int]:
        try:
            required_fields = ["title", "status", "task_id"]
            if not all(field in data for field in required_fields):
                return {"error": "Missing required fields"}, 400

            user_id = request.decoded.get("user_id")
            customer_id = request.decoded.get("customer_id")
            role = request.decoded.get("role")

            if not user_id or not customer_id:
                return {"error": "Unauthorized: Invalid token data"}, 401

            if role not in ["Admin", "Project Manager"]:
                return {"error": "Insufficient permissions"}, 403

            task = Task.query.filter_by(id=data["task_id"], customer_id=customer_id).first()
            if not task:
                return {"error": "Parent task not found or unauthorized"}, 404

            assigned_user_id = data.get("assigned_user_id")
            if assigned_user_id:
                user = User.query.filter_by(id=assigned_user_id, customer_id=customer_id).first()
                if not user:
                    return {"error": "Assigned user not found or unauthorized"}, 404

            assigned_team_id = data.get("assigned_team_id")
            if assigned_team_id:
                team = Team.query.filter_by(id=assigned_team_id, customer_id=customer_id).first()
                if not team:
                    return {"error": "Assigned team not found or unauthorized"}, 404

            subtask = Subtask(
                id=str(uuid4()),
                task_id=data["task_id"],
                title=data["title"],
                description=data.get("description", ""),
                status=data["status"],
                assigned_user_id=assigned_user_id,
                assigned_team_id=assigned_team_id,
                due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
                tags=data.get("tags", []),
                estimated_duration=data.get("estimated_duration"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(subtask)
            db.session.commit()

            return {"message": "Subtask created successfully", "subtask": subtask.to_dict()}, 201

        except Exception as e:
            app_logger.error({
                "function": "TaskService.create_subtask",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            db.session.rollback()
            return {"error": f"Failed to create subtask: {str(e)}"}, 500

    @staticmethod
    def update_subtask(subtask_id: str, data: dict) -> Tuple[dict, int]:
        try:
            user_id = request.decoded.get("user_id")
            customer_id = request.decoded.get("customer_id")
            role = request.decoded.get("role")

            if not user_id or not customer_id:
                return {"error": "Unauthorized: Invalid token data"}, 401

            if role not in ["Admin", "Project Manager"]:
                return {"error": "Insufficient permissions"}, 403

            subtask = Subtask.query.join(Task).filter(
                Subtask.id == subtask_id,
                Task.customer_id == customer_id
            ).first()
            if not subtask:
                return {"error": "Subtask not found or unauthorized"}, 404

            # Check if subtask status is changing from Not Started
            previous_status = subtask.status
            if "status" in data and data["status"] != previous_status:
                if previous_status == "Not Started" and data["status"] in ["In Progress", "Completed"]:
                    # Update parent task's start_date and status
                    parent_task = subtask.task
                    if not parent_task.start_date:
                        parent_task.start_date = datetime.utcnow()
                    if parent_task.status == "Not Started":
                        parent_task.status = "In Progress"
                        parent_task.updated_at = datetime.utcnow()

            # Update subtask fields if provided
            if "title" in data:
                subtask.title = data["title"]
            if "description" in data:
                subtask.description = data.get("description", "")
            if "status" in data:
                subtask.status = data["status"]
            if "assigned_user_id" in data:
                assigned_user_id = data.get("assigned_user_id")
                if assigned_user_id:
                    user = User.query.filter_by(id=assigned_user_id, customer_id=customer_id).first()
                    if not user:
                        return {"error": "Assigned user not found or unauthorized"}, 404
                subtask.assigned_user_id = assigned_user_id
            if "assigned_team_id" in data:
                assigned_team_id = data.get("assigned_team_id")
                if assigned_team_id:
                    team = Team.query.filter_by(id=assigned_team_id, customer_id=customer_id).first()
                    if not team:
                        return {"error": "Assigned team not found or unauthorized"}, 404
                subtask.assigned_team_id = assigned_team_id
            if "due_date" in data:
                subtask.due_date = datetime.fromisoformat(data["due_date"]) if data["due_date"] else None
            if "tags" in data:
                subtask.tags = data.get("tags", [])
            if "estimated_duration" in data:
                subtask.estimated_duration = data.get("estimated_duration")

            subtask.updated_at = datetime.utcnow()
            db.session.commit()

            return {"message": "Subtask updated successfully", "subtask": subtask.to_dict()}, 200

        except Exception as e:
            app_logger.error({
                "function": "TaskService.update_subtask",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            db.session.rollback()
            return {"error": f"Failed to update subtask: {str(e)}"}, 500

    @staticmethod
    def delete_subtask(subtask_id: str) -> Tuple[dict, int]:
        try:
            user_id = request.decoded.get("user_id")
            customer_id = request.decoded.get("customer_id")
            role = request.decoded.get("role")

            if not user_id or not customer_id:
                return {"error": "Unauthorized: Invalid token data"}, 401

            if role not in ["Admin", "Project Manager"]:
                return {"error": "Insufficient permissions"}, 403

            subtask = Subtask.query.join(Task).filter(
                Subtask.id == subtask_id,
                Task.customer_id == customer_id
            ).first()
            if not subtask:
                return {"error": "Subtask not found or unauthorized"}, 404

            db.session.delete(subtask)
            db.session.commit()

            return {"message": "Subtask deleted successfully"}, 200

        except Exception as e:
            app_logger.error({
                "function": "TaskService.delete_subtask",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            db.session.rollback()
            return {"error": f"Failed to delete subtask: {str(e)}"}, 500