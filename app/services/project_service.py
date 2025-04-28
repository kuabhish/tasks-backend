# app/services/project_service.py
from flask import request
from ..models.project import Project
from ..utils.logger import app_logger
import traceback
from typing import Tuple, List
from datetime import datetime
from uuid import uuid4
from .. import db

class ProjectService:
    @staticmethod
    def list_projects() -> Tuple[List[dict], int]:
        try:
            user_id = request.decoded.get("user_id")
            customer_id = request.decoded.get("customer_id")
            role = request.decoded.get("role")

            if not user_id or not customer_id:
                return [{"error": "Unauthorized: Invalid token data"}], 401

            # Fetch projects based on role
            query = Project.query.filter_by(customer_id=customer_id)
            if role != "Admin":
                query = query.filter_by(project_manager_id=user_id)

            projects = query.all()
            return [project.to_dict() for project in projects], 200

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