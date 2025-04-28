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