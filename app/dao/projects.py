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

    @staticmethod
    def fetch_project_stats(project_id: str, customer_id: str) -> dict:
        """
        Fetch statistics for a project: total tasks, total subtasks, completed subtasks, and completion rate.
        """
        try:
            if not customer_id:
                return {"error": "Unauthorized: Invalid token data"}, 401

            query = """
                SELECT 
                    COALESCE((
                        SELECT COUNT(*) 
                        FROM tasks t 
                        WHERE t.project_id = p.id 
                        AND t.customer_id = :customer_id
                    ), 0) AS total_tasks,
                    COALESCE((
                        SELECT COUNT(*) 
                        FROM subtasks s 
                        JOIN tasks t ON s.task_id = t.id 
                        WHERE t.project_id = p.id 
                        AND t.customer_id = :customer_id
                    ), 0) AS total_subtasks,
                    COALESCE((
                        SELECT COUNT(*) 
                        FROM subtasks s 
                        JOIN tasks t ON s.task_id = t.id 
                        WHERE t.project_id = p.id 
                        AND t.customer_id = :customer_id 
                        AND s.status = 'Completed'
                    ), 0) AS completed_subtasks
                FROM projects p
                WHERE p.id = :project_id 
                AND p.customer_id = :customer_id
            """
            params = {"project_id": project_id, "customer_id": customer_id}

            result = db.session.execute(text(query), params).fetchone()
            if not result:
                return {"error": "Project not found or unauthorized"}, 404

            total_tasks = result.total_tasks
            total_subtasks = result.total_subtasks
            completed_subtasks = result.completed_subtasks
            completion_rate = round((completed_subtasks / total_subtasks * 100) if total_subtasks > 0 else 0)

            return {
                "total_tasks": total_tasks,
                "total_subtasks": total_subtasks,
                "completed_subtasks": completed_subtasks,
                "completion_rate": completion_rate
            }, 200

        except Exception as e:
            from ..utils.logger import app_logger
            import traceback
            app_logger.error({
                "function": "ProjectsDao.fetch_project_stats",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            return {"error": f"Failed to fetch project stats: {str(e)}"}, 500
        