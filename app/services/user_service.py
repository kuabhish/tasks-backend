from flask import request
from ..models.user import User
from ..models.team_member import TeamMember
from ..models.team import Team
from ..utils.logger import app_logger
import traceback
from typing import Tuple, List
from .. import db

class UserService:
    @staticmethod
    def get_user(user_id: str) -> Tuple[dict, int]:
        try:
            customer_id = request.decoded.get("customer_id")
            role = request.decoded.get("role")
            request_user_id = request.decoded.get("user_id")

            if not customer_id or not request_user_id:
                return {"error": "Unauthorized: Invalid token data"}, 401

            # Allow Admins/Project Managers to view any user, Team Members only their own profile
            if role == "Team Member" and request_user_id != user_id:
                return {"error": "Insufficient permissions"}, 403

            user = User.query.filter_by(id=user_id, customer_id=customer_id).first()
            if not user:
                return {"error": "User not found or unauthorized"}, 404

            user_dict = user.to_dict()
            # Include teams the user is a member of
            team_members = TeamMember.query.filter_by(user_id=user_id).all()
            user_dict['teams'] = [
                Team.query.get(tm.team_id).to_dict() for tm in team_members
            ]

            return {"message": "User fetched successfully", "data": user_dict}, 200

        except Exception as e:
            app_logger.error({
                "function": "UserService.get_user",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            return {"error": f"Failed to fetch user: {str(e)}"}, 500

    @staticmethod
    def list_users() -> Tuple[List[dict], int]:
        try:
            customer_id = request.decoded.get("customer_id")
            role = request.decoded.get("role")

            if not customer_id:
                return [{"error": "Unauthorized: Invalid token data"}], 401

            if role not in ["Admin", "Project Manager"]:
                return [{"error": "Insufficient permissions"}], 403

            users = User.query.filter_by(customer_id=customer_id).all()
            user_dicts = []
            for user in users:
                user_dict = user.to_dict()
                team_members = TeamMember.query.filter_by(user_id=user.id).all()
                user_dict['teams'] = [
                    Team.query.get(tm.team_id).to_dict() for tm in team_members
                ]
                user_dicts.append(user_dict)

            return user_dicts, 200

        except Exception as e:
            app_logger.error({
                "function": "UserService.list_users",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            return [{"error": f"Failed to fetch users: {str(e)}"}], 500