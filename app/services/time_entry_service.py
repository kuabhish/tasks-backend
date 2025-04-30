import dateutil.parser
from flask import request
from ..models.task import Task
from ..models.subtask import Subtask
from ..models.time_entry import TimeEntry
from ..utils.logger import app_logger
import traceback
from typing import Tuple, List
from datetime import datetime
from uuid import uuid4
from .. import db
from dateutil import tz
from sqlalchemy.sql import text

class TimeEntryService:
    @staticmethod
    def list_time_entries(project_id: str = None, start_date: str = None, end_date: str = None) -> Tuple[List[dict], int]:
        try:
            user_id = request.decoded.get("user_id")
            customer_id = request.decoded.get("customer_id")
            role = request.decoded.get("role")

            if not user_id or not customer_id:
                return [{"error": "Unauthorized: Invalid token data"}], 401

            # Set session timezone to UTC
            db.session.execute(text("SET TIME ZONE 'UTC'"))
            print("debug --- session timezone:", db.session.execute(text("SHOW timezone")).scalar())

            print("debug --- list:", user_id, customer_id, role, start_date, end_date)

            query = TimeEntry.query.filter_by(customer_id=customer_id)
            if role == "Team Member":
                query = query.filter_by(user_id=user_id)

            if project_id:
                query = query.join(Subtask, TimeEntry.subtask_id == Subtask.id)\
                            .join(Task, Subtask.task_id == Task.id)\
                            .filter(Task.project_id == project_id)

            if start_date:
                try:
                    start = dateutil.parser.isoparse(start_date).astimezone(tz.UTC)
                    print("debug --- parsed start_date:", start_date, "->", start.isoformat())
                    query = query.filter(TimeEntry.start_time >= start)
                except ValueError:
                    return [{"error": "Invalid start_date format"}], 400

            if end_date:
                try:
                    end = dateutil.parser.isoparse(end_date).astimezone(tz.UTC)
                    print("debug --- parsed end_date:", end_date, "->", end.isoformat())
                    query = query.filter(TimeEntry.end_time <= end)
                except ValueError:
                    return [{"error": "Invalid end_date format"}], 400

            time_entries = query.all()

            result = [entry.to_dict() for entry in time_entries]
            print("debug --- time_entries:", result)
            return result, 200

        except Exception as e:
            app_logger.error({
                "function": "TimeEntryService.list_time_entries",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            return [{"error": f"Failed to fetch time entries: {str(e)}"}], 500

    @staticmethod
    def create_time_entry(data: dict) -> Tuple[dict, int]:
        try:
            required_fields = ["subtask_id", "start_time", "end_time", "duration"]
            if not all(field in data for field in required_fields):
                return {"error": "Missing required fields"}, 400

            user_id = request.decoded.get("user_id")
            customer_id = request.decoded.get("customer_id")
            role = request.decoded.get("role")

            if not user_id or not customer_id:
                return {"error": "Unauthorized: Invalid token data"}, 401

            # Verify subtask exists and belongs to customer
            subtask = Subtask.query.join(Task, Subtask.task_id == Task.id)\
                                  .filter(Subtask.id == data["subtask_id"], Task.customer_id == customer_id)\
                                  .first()
            if not subtask:
                return {"error": "Subtask not found or unauthorized"}, 404

            # Parse start_time and end_time, ensure UTC timezone-aware
            try:
                start_time = dateutil.parser.isoparse(data["start_time"]).astimezone(tz.UTC)
                end_time = dateutil.parser.isoparse(data["end_time"]).astimezone(tz.UTC)
                print("debug --- parsed start_time:", start_time, "end_time:", end_time)
            except ValueError:
                return {"error": "Invalid start_time or end_time format"}, 400

            # Validate duration
            calculated_duration = int((end_time - start_time).total_seconds() / 60)
            if calculated_duration != data["duration"]:
                return {"error": "Duration does not match start and end times"}, 400

            # Force UTC timezone for session (optional)
            db.session.execute(text("SET TIME ZONE 'UTC'"))
            print("debug --- session timezone:", db.session.execute(text("SHOW timezone")).scalar())

            time_entry = TimeEntry(
                id=str(uuid4()),
                customer_id=customer_id,
                user_id=user_id,
                subtask_id=data["subtask_id"],
                start_time=start_time,
                end_time=end_time,
                duration=data["duration"],
                notes=data.get("notes"),
                created_at=datetime.now(tz.UTC)
            )
            db.session.add(time_entry)
            db.session.commit()

            result = time_entry.to_dict()
            print("debug --- created time_entry:", result)
            return {"message": "Time entry created successfully", "timeEntry": result}, 201

        except Exception as e:
            app_logger.error({
                "function": "TimeEntryService.create_time_entry",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            # db.session.rollback()
            return {"error": f"Failed to create time entry: {str(e)}"}, 500

    
    @staticmethod
    def update_time_entry(time_entry_id: str, data: dict) -> Tuple[dict, int]:
        try:
            required_fields = ["subtask_id", "start_time", "end_time", "duration"]
            if not all(field in data for field in required_fields):
                return {"error": "Missing required fields"}, 400

            user_id = request.decoded.get("user_id")
            customer_id = request.decoded.get("customer_id")
            role = request.decoded.get("role")

            if not user_id or not customer_id:
                return {"error": "Unauthorized: Invalid token data"}, 401

            # Verify time entry exists and belongs to customer
            time_entry = TimeEntry.query.filter_by(id=time_entry_id, customer_id=customer_id).first()
            if not time_entry:
                return {"error": "Time entry not found or unauthorized"}, 404

            # Restrict updates to Admin/Project Manager or the entry's owner
            if role == "Team Member" and time_entry.user_id != user_id:
                return {"error": "Unauthorized: You can only update your own time entries"}, 403

            # Verify subtask exists and belongs to customer
            subtask = Subtask.query.join(Task, Subtask.task_id == Task.id)\
                                  .filter(Subtask.id == data["subtask_id"], Task.customer_id == customer_id)\
                                  .first()
            if not subtask:
                return {"error": "Subtask not found or unauthorized"}, 404

            # Parse start_time and end_time, convert to UTC
            try:
                parsed_start = dateutil.parser.isoparse(data["start_time"])
                parsed_end = dateutil.parser.isoparse(data["end_time"])

                # Convert to UTC using timezone offset
                start_time = parsed_start.astimezone(tz.UTC)
                end_time = parsed_end.astimezone(tz.UTC)

                print("debug --- raw start_time:", data["start_time"], "parsed:", parsed_start.isoformat(), "utc:", start_time.isoformat())
                print("debug --- raw end_time:", data["end_time"], "parsed:", parsed_end.isoformat(), "utc:", end_time.isoformat())
            except ValueError:
                return {"error": "Invalid start_time or end_time format"}, 400

            # Validate duration
            calculated_duration = int((end_time - start_time).total_seconds() / 60)
            if calculated_duration != data["duration"]:
                return {"error": f"Duration ({data['duration']}) does not match start and end times ({calculated_duration})"}, 400

            db.session.execute(text("SET TIME ZONE 'UTC'"))
            print("debug --- session timezone:", db.session.execute(text("SHOW timezone")).scalar())


            # Update fields
            time_entry.subtask_id = data["subtask_id"]
            time_entry.start_time = start_time
            time_entry.end_time = end_time
            time_entry.duration = data["duration"]
            time_entry.notes = data.get("notes")

            db.session.commit()

            result = time_entry.to_dict()
            print("debug --- updated time_entry:", result)
            return {"message": "Time entry updated successfully", "timeEntry": result}, 200

        except Exception as e:
            app_logger.error({
                "function": "TimeEntryService.update_time_entry",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            db.session.rollback()
            return {"error": f"Failed to update time entry: {str(e)}"}, 500