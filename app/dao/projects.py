from ..sources import db
from sqlalchemy import text

class ProjectsDao:
    @staticmethod
    def fetch_eligible_projects(customer_id, role, user_id):
        base_query = """
            SELECT * FROM projects
            WHERE customer_id = :customer_id
            AND (is_archived IS NOT TRUE)
        """

        params = {"customer_id": customer_id}

        if role != 'Admin':
            base_query += " AND project_manager_id = :user_id"
            params["user_id"] = user_id

        return db.session.execute(text(base_query), params)
