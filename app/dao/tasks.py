from ..sources import db
from sqlalchemy import text
from typing import Tuple, List

class TasksDao:
    @staticmethod
    def list_tasks(project_id: str = None, user_id: str = None, customer_id: str = None, role: str = None) -> Tuple[List[dict], int]:
        """
        Stuart: Fetch tasks and their subtasks in a single query, including completion percentage.
        """
        try:
            if not user_id or not customer_id:
                return [{"error": "Unauthorized: Invalid token data"}], 401

            base_query = """
                SELECT 
                    t.id, t.customer_id, t.project_id, t.category_id, t.title, 
                    t.description, t.status, t.priority, 
                    t.due_date, t.tags, t.estimated_duration, t.actual_duration,
                    t.start_date, t.end_date, t.created_at, t.updated_at,
                    COALESCE((
                        SELECT json_agg(json_build_object(
                            'id', s.id,
                            'task_id', s.task_id,
                            'title', s.title,
                            'description', s.description,
                            'status', s.status,
                            'assigned_user_id', s.assigned_user_id,
                            'assigned_team_id', s.assigned_team_id,
                            'due_date', s.due_date,
                            'tags', s.tags,
                            'estimated_duration', s.estimated_duration,
                            'created_at', s.created_at,
                            'updated_at', s.updated_at
                        ))
                        FROM subtasks s
                        WHERE s.task_id = t.id
                    ), '[]'::json) AS subtasks,
                    COALESCE((
                        SELECT COUNT(*) 
                        FROM subtasks s 
                        WHERE s.task_id = t.id 
                        AND s.status = 'Completed'
                    ), 0) AS completed_subtasks_count,
                    COALESCE((
                        SELECT COUNT(*) 
                        FROM subtasks s 
                        WHERE s.task_id = t.id
                    ), 0) AS total_subtasks_count
                FROM tasks t
                WHERE t.customer_id = :customer_id
            """
            params = {"customer_id": customer_id}

            if project_id:
                base_query += " AND t.project_id = :project_id"
                params["project_id"] = project_id

            if role == "Team Member":
                base_query += """
                    AND t.id IN (
                        SELECT s.task_id 
                        FROM subtasks s 
                        WHERE s.assigned_user_id = :user_id
                    )
                """
                params["user_id"] = user_id

            result = db.session.execute(text(base_query), params).fetchall()
            task_dicts = []
            for row in result:
                task_dict = {
                    'id': row.id,
                    'customer_id': row.customer_id,
                    'project_id': row.project_id,
                    'category_id': row.category_id,
                    'title': row.title,
                    'description': row.description,
                    'status': row.status,
                    'priority': row.priority,
                    'due_date': row.due_date.isoformat() if row.due_date else None,
                    'tags': row.tags,
                    'estimated_duration': row.estimated_duration,
                    'actual_duration': row.actual_duration,
                    'start_date': row.start_date.isoformat() if row.start_date else None,
                    'end_date': row.end_date.isoformat() if row.end_date else None,
                    'created_at': row.created_at.isoformat(),
                    'updated_at': row.updated_at.isoformat(),
                    'subtasks': row.subtasks,
                    'completion_percentage': round(
                        (row.completed_subtasks_count / row.total_subtasks_count * 100)
                        if row.total_subtasks_count > 0 else 0
                    )
                }
                task_dicts.append(task_dict)

            return task_dicts, 200

        except Exception as e:
            from ..utils.logger import app_logger
            import traceback
            app_logger.error({
                "function": "TasksDao.list_tasks",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            return [{"error": f"Failed to fetch tasks: {str(e)}"}], 500