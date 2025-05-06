# app/services/project_service.py
from flask import request
from ..models import Project, Task, Subtask
from ..utils.logger import app_logger
import traceback
from typing import Tuple, List, Dict
from datetime import datetime
from uuid import uuid4
from .. import db
from ..dao import ProjectsDao

class ProjectService:
    @staticmethod
    def list_projects() -> Tuple[List[dict], int]:
        try:
            user_id = request.decoded.get("user_id")
            customer_id = request.decoded.get("customer_id")
            role = request.decoded.get("role")

            if not user_id or not customer_id:
                return [{"error": "Unauthorized: Invalid token data"}], 401

            # projects = query.all()
            result = ProjectsDao.fetch_eligible_projects(
                customer_id=customer_id, 
                role=role, 
                user_id=user_id
            )
            rows = result.mappings().all()
            return [dict(row) for row in rows], 200
            # return [project.to_dict() for project in projects], 200

        except Exception as e:
            app_logger.error({
                "function": "ProjectService.list_projects",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            return [{"error": f"Failed to fetch projects: {str(e)}"}], 500

    @staticmethod
    def create_project(data: dict) -> Tuple[dict, int]:
        try:
            required_fields = ["title", "description", "status", "start_date", "tech_stack"]
            if not all(field in data for field in required_fields):
                return {"error": "Missing required fields"}, 400

            user_id = request.decoded.get("user_id")
            customer_id = request.decoded.get("customer_id")
            role = request.decoded.get("role")

            if not user_id or not customer_id:
                return {"error": "Unauthorized: Invalid token data"}, 401

            if role not in ["Admin", "Project Manager"]:
                return {"error": "Insufficient permissions"}, 403

            project = Project(
                id=str(uuid4()),
                customer_id=customer_id,
                title=data["title"],
                description=data["description"],
                project_manager_id=user_id,
                status=data["status"],
                start_date=datetime.fromisoformat(data["start_date"]),
                end_date=datetime.fromisoformat(data["end_date"]) if data.get("end_date") else None,
                budget=data.get("budget", 0),
                goals=data.get("goals", {}),
                milestones=data.get("milestones", {}),
                tech_stack=data["tech_stack"],
                repository_url=data.get("repository_url", ""),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(project)
            db.session.commit()

            return {"message": "Project created successfully", "project": project.to_dict()}, 201

        except Exception as e:
            app_logger.error({
                "function": "ProjectService.create_project",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            # db.session.rollback()
            return {"error": f"Failed to create project: {str(e)}"}, 500

    @staticmethod
    def update_project(project_id: str, data: dict) -> Tuple[dict, int]:
        try:
            user_id = request.decoded.get("user_id")
            customer_id = request.decoded.get("customer_id")
            role = request.decoded.get("role")
            print("incoming ..")

            if not user_id or not customer_id:
                return {"error": "Unauthorized: Invalid token data"}, 401

            if role not in ["Admin", "Project Manager"]:
                return {"error": "Insufficient permissions"}, 403

            project = Project.query.filter_by(id=project_id, customer_id=customer_id).first()
            if not project:
                return {"error": "Project not found or archived"}, 404

            if role != "Admin" and project.project_manager_id != user_id:
                return {"error": "Unauthorized: You are not the project manager"}, 403

            # Update fields if provided
            if "title" in data:
                project.title = data["title"]
            if "description" in data:
                project.description = data["description"]
            if "status" in data:
                project.status = data["status"]
            if "start_date" in data:
                project.start_date = datetime.fromisoformat(data["start_date"])
            if "end_date" in data:
                project.end_date = datetime.fromisoformat(data["end_date"]) if data["end_date"] else None
            if "budget" in data:
                project.budget = data["budget"]
            if "goals" in data:
                project.goals = data["goals"]
            if "milestones" in data:
                project.milestones = data["milestones"]
            if "tech_stack" in data:
                project.tech_stack = data["tech_stack"]
            if "repository_url" in data:
                project.repository_url = data["repository_url"]
            project.updated_at = datetime.utcnow()

            db.session.commit()

            return {"message": "Project updated successfully", "project": project.to_dict()}, 200

        except Exception as e:
            app_logger.error({
                "function": "ProjectService.update_project",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            db.session.rollback()
            return {"error": f"Failed to update project: {str(e)}"}, 500

    @staticmethod
    def archive_project(project_id: str) -> Tuple[dict, int]:
        try:
            user_id = request.decoded.get("user_id")
            customer_id = request.decoded.get("customer_id")
            role = request.decoded.get("role")

            if not user_id or not customer_id:
                return {"error": "Unauthorized: Invalid token data"}, 401

            if role not in ["Admin", "Project Manager"]:
                return {"error": "Insufficient permissions"}, 403

            project = Project.query.filter_by(id=project_id, customer_id=customer_id).first()
            if not project:
                return {"error": "Project not found or already archived"}, 404

            if role != "Admin" and project.project_manager_id != user_id:
                return {"error": "Unauthorized: You are not the project manager"}, 403

            project.is_archived = True
            project.updated_at = datetime.utcnow()
            db.session.commit()

            return {"message": "Project archived successfully"}, 200

        except Exception as e:
            app_logger.error({
                "function": "ProjectService.archive_project",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            db.session.rollback()
            return {"error": f"Failed to archive project: {str(e)}"}, 500


    @staticmethod
    def get_project_stats(project_id: str) -> Tuple[dict, int]:
        try:
            customer_id = request.decoded.get("customer_id")
            return ProjectsDao.fetch_project_stats(project_id, customer_id)

        except Exception as e:
            app_logger.error({
                "function": "ProjectService.get_project_stats",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            return {"error": f"Failed to fetch project stats: {str(e)}"}, 500
        