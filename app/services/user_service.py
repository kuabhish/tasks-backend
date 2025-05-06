from flask import request
from ..utils.logger import app_logger
import traceback
from typing import Tuple, List
from ..dao import UsersDao  # Import the new DAO

class UserService:
    @staticmethod
    def get_user(user_id: str) -> Tuple[dict, int]:
        try:
            customer_id = request.decoded.get("customer_id")
            role = request.decoded.get("role")
            request_user_id = request.decoded.get("user_id")

            return UsersDao.fetch_user(user_id, customer_id, role, request_user_id)

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

            result, status = UsersDao.fetch_users(customer_id, role)
            # Adjust response format to match original
            if status == 200:
                return result["data"], 200
            return [result], status

        except Exception as e:
            app_logger.error({
                "function": "UserService.list_users",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            return [{"error": f"Failed to fetch users: {str(e)}"}], 500
        