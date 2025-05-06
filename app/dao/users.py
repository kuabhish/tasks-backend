from ..sources import db
from sqlalchemy import text
import json

class UsersDao:
    @staticmethod
    def fetch_user(user_id: str, customer_id: str, role: str, request_user_id: str) -> dict:
        """
        Fetch a single user and their associated teams.
        """
        try:
            # Authorization checks
            if not customer_id or not request_user_id:
                return {"error": "Unauthorized: Invalid token data"}, 401

            if role == "Team Member" and request_user_id != user_id:
                return {"error": "Insufficient permissions"}, 403

            # Base query to fetch user details
            base_query = """
                SELECT u.*
                FROM users u
                WHERE u.id = :user_id
                AND u.customer_id = :customer_id
            """
            params = {"user_id": user_id, "customer_id": customer_id}

            # Execute query to fetch user
            result = db.session.execute(text(base_query), params).fetchone()
            if not result:
                return {"error": "User not found or unauthorized"}, 404

            # Convert user row to dict
            user_dict = dict(result._mapping)

            # Fetch associated teams
            teams_query = """
                SELECT t.*
                FROM teams t
                JOIN team_members tm ON t.id = tm.team_id
                WHERE tm.user_id = :user_id
            """
            teams_result = db.session.execute(text(teams_query), {"user_id": user_id}).fetchall()
            user_dict['teams'] = [dict(team._mapping) for team in teams_result]

            return {"message": "User fetched successfully", "data": user_dict}, 200

        except Exception as e:
            from ..utils.logger import app_logger
            import traceback
            app_logger.error({
                "function": "UsersDao.fetch_user",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            return {"error": f"Failed to fetch user: {str(e)}"}, 500

    @staticmethod
    def fetch_users(customer_id: str, role: str) -> dict:
        """
        Fetch all users for a customer, including their associated teams.
        """
        try:
            # Authorization checks
            if not customer_id:
                return {"error": "Unauthorized: Invalid token data"}, 401

            if role not in ["Admin", "Project Manager"]:
                return {"error": "Insufficient permissions"}, 403

            # Query to fetch users and aggregate their teams as JSON (PostgreSQL-compatible)
            query = """
                SELECT 
                    u.*,
                    COALESCE(
                        (
                            SELECT json_agg(
                                json_build_object(
                                    'id', t.id,
                                    'name', t.name
                                    -- Add other team fields as needed
                                )
                            )
                            FROM teams t
                            JOIN team_members tm ON t.id = tm.team_id
                            WHERE tm.user_id = u.id
                        ),
                        '[]'::json
                    ) as teams
                FROM users u
                WHERE u.customer_id = :customer_id
            """
            params = {"customer_id": customer_id}

            # Execute query
            results = db.session.execute(text(query), params).fetchall()

            # Convert results to list of dicts
            user_dicts = []
            for row in results:
                user_dict = dict(row._mapping)
                # Teams field is already a Python list (json_agg returns parsed JSON)
                user_dict['teams'] = user_dict['teams'] or []
                user_dicts.append(user_dict)

            return {"message": "Users fetched successfully", "data": user_dicts}, 200

        except Exception as e:
            from ..utils.logger import app_logger
            import traceback
            app_logger.error({
                "function": "UsersDao.fetch_users",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            return {"error": f"Failed to fetch users: {str(e)}"}, 500
        