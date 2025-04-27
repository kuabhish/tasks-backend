from flask import jsonify
from typing import Any, Tuple

def success_response(data: Any = None, message: str = "Success", status_code: int = 200) -> Tuple[dict, int]:
    response = {"status": "success", "message": message}
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code

def error_response(message: str, status_code: int = 400, details: Any = None) -> Tuple[dict, int]:
    response = {"status": "error", "message": message}
    if details is not None:
        response["details"] = details
    return jsonify(response), status_code