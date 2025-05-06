from ..sources import db
from sqlalchemy import text

class TeamsDao:
    @staticmethod
    def fetch_teams(customer_id: str, role: str, user_id: str) -> dict:
        """
        Fetch all teams for a customer, including their members and user details.
        """
        try:
            if not customer_id:
                return {"error": "Unauthorized: Invalid token data"}, 401

            # Base query to fetch teams and aggregate members
            query = """
                SELECT 
                    t.id,
                    t.customer_id AS "customerId",
                    t.name,
                    t.description,
                    to_char(t.created_at, 'YYYY-MM-DD"T"HH24:MI:SS.US"Z"') AS "createdAt",
                    to_char(t.updated_at, 'YYYY-MM-DD"T"HH24:MI:SS.US"Z"') AS "updatedAt",
                    COALESCE(
                        (
                            SELECT json_agg(
                                json_build_object(
                                    'user_id', tm.user_id,
                                    'team_id', tm.team_id,
                                    'joined_at', to_char(tm.joined_at, 'YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
                                    'user', json_build_object(
                                        'id', u.id,
                                        'customerId', u.customer_id,
                                        'username', u.username,
                                        'email', u.email,
                                        'role', u.role,
                                        'createdAt', to_char(u.created_at, 'YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
                                        'updatedAt', to_char(u.updated_at, 'YYYY-MM-DD"T"HH24:MI:SS.US"Z"')
                                    )
                                )
                            )
                            FROM team_members tm
                            JOIN users u ON tm.user_id = u.id
                            WHERE tm.team_id = t.id
                        ),
                        '[]'::json
                    ) AS members
                FROM teams t
                WHERE t.customer_id = :customer_id
            """
            params = {"customer_id": customer_id}

            # Restrict to user's teams for Team Member role
            if role == "Team Member":
                query += """
                    AND t.id IN (
                        SELECT team_id 
                        FROM team_members 
                        WHERE user_id = :user_id
                    )
                """
                params["user_id"] = user_id

            # Execute query
            results = db.session.execute(text(query), params).fetchall()

            # Convert results to list of dicts
            team_dicts = [dict(row._mapping) for row in results]

            return {"message": "Teams fetched successfully", "data": team_dicts}, 200

        except Exception as e:
            from ..utils.logger import app_logger
            import traceback
            app_logger.error({
                "function": "TeamsDao.fetch_teams",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            return {"error": f"Failed to fetch teams: {str(e)}"}, 500
          