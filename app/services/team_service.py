from flask import request
from ..models.team import Team
from ..models.team_member import TeamMember
from ..models.user import User
from ..utils.logger import app_logger
import traceback
from typing import Tuple, List
from datetime import datetime
from uuid import uuid4
from .. import db
from ..dao import TeamsDao  # Import the new DAO

class TeamService:
    @staticmethod
    def create_team(data: dict) -> Tuple[dict, int]:
        try:
            required_fields = ["name"]
            if not all(field in data for field in required_fields):
                return {"error": "Missing required fields"}, 400

            customer_id = request.decoded.get("customer_id")
            role = request.decoded.get("role")

            if not customer_id:
                return {"error": "Unauthorized: Invalid token data"}, 401

            if role not in ["Admin", "Project Manager"]:
                return {"error": "Insufficient permissions"}, 403

            team = Team(
                id=str(uuid4()),
                customer_id=customer_id,
                name=data["name"],
                description=data.get("description"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(team)
            db.session.commit()

            return {"message": "Team created successfully", "team": team.to_dict()}, 201

        except Exception as e:
            app_logger.error({
                "function": "TeamService.create_team",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            # db.session.rollback()
            return {"error": f"Failed to create team: {str(e)}"}, 500

    @staticmethod
    def list_teams() -> Tuple[List[dict], int]:
        try:
            customer_id = request.decoded.get("customer_id")
            role = request.decoded.get("role")
            user_id = request.decoded.get("user_id")

            result, status = TeamsDao.fetch_teams(customer_id, role, user_id)
            # Adjust response format to match original
            if status == 200:
                return result["data"], 200
            return [result], status

        except Exception as e:
            app_logger.error({
                "function": "TeamService.list_teams",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            return [{"error": f"Failed to fetch teams: {str(e)}"}], 500

    @staticmethod
    def add_team_member(team_id: str, data: dict) -> Tuple[dict, int]:
        try:
            user_id = data.get("user_id")
            if not user_id:
                return {"error": "Missing user_id"}, 400

            customer_id = request.decoded.get("customer_id")
            role = request.decoded.get("role")

            if not customer_id:
                return {"error": "Unauthorized: Invalid token data"}, 401

            if role not in ["Admin", "Project Manager"]:
                return {"error": "Insufficient permissions"}, 403

            team = Team.query.filter_by(id=team_id, customer_id=customer_id).first()
            if not team:
                return {"error": "Team not found or unauthorized"}, 404

            user = User.query.filter_by(id=user_id, customer_id=customer_id).first()
            if not user:
                return {"error": "User not found or unauthorized"}, 404

            existing_member = TeamMember.query.filter_by(team_id=team_id, user_id=user_id).first()
            if existing_member:
                return {"error": "User is already a member of this team"}, 400

            team_member = TeamMember(
                user_id=user_id,
                team_id=team_id,
                joined_at=datetime.utcnow()
            )
            db.session.add(team_member)
            db.session.commit()

            return {
                "message": "User added to team successfully",
                "teamMember": {
                    **team_member.to_dict(),
                    'user': user.to_dict()
                }
            }, 201

        except Exception as e:
            app_logger.error({
                "function": "TeamService.add_team_member",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            # db.session.rollback()
            return {"error": f"Failed to add user to team: {str(e)}"}, 500

    @staticmethod
    def remove_team_member(team_id: str, user_id: str) -> Tuple[dict, int]:
        try:
            customer_id = request.decoded.get("customer_id")
            role = request.decoded.get("role")

            if not customer_id:
                return {"error": "Unauthorized: Invalid token data"}, 401

            if role not in ["Admin", "Project Manager"]:
                return {"error": "Insufficient permissions"}, 403

            team = Team.query.filter_by(id=team_id, customer_id=customer_id).first()
            if not team:
                return {"error": "Team not found or unauthorized"}, 404

            team_member = TeamMember.query.filter_by(team_id=team_id, user_id=user_id).first()
            if not team_member:
                return {"error": "User is not a member of this team"}, 404

            db.session.delete(team_member)
            db.session.commit()

            return {"message": "User removed from team successfully"}, 200

        except Exception as e:
            app_logger.error({
                "function": "TeamService.remove_team_member",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            # db.session.rollback()
            return {"error": f"Failed to remove user from team: {str(e)}"}, 500
        