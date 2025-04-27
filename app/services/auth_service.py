from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from ..models.user import User
from ..models.customer import Customer
from ..utils.logger import app_logger
from ..middleware.auth_and_log import AuthAndLogMiddleware
from .. import db
import traceback
from typing import Tuple, Optional
from uuid import uuid4
from datetime import datetime

class AuthService:
    @staticmethod
    def register(data: dict) -> Tuple[dict, int]:
        try:
            required_fields = ["username", "email", "password", "role"]
            if not all(field in data for field in required_fields):
                return {"error": "Missing required fields"}, 400

            # Validate email format (basic check)
            if "@" not in data["email"] or "." not in data["email"]:
                return {"error": "Invalid email format"}, 400

            # Check for existing user
            if User.query.filter_by(email=data["email"]).first() or User.query.filter_by(username=data["username"]).first():
                return {"error": "User with this email or username already exists"}, 409

            # Create or find customer
            company_name = data.get("company_name", "Personal")
            email_domain = data["email"].split("@")[1]
            customer = Customer.query.filter_by(domain=email_domain).first()

            if not customer:
                customer = Customer(
                    id=str(uuid4()),
                    name=company_name,
                    contact_email=data["email"],
                    domain=email_domain,
                    plan="Basic",
                    time_zone="UTC",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(customer)
                db.session.commit()

            # Create new user
            user = User(
                customer_id=customer.id,
                username=data["username"],
                email=data["email"],
                password_hash=generate_password_hash(data["password"]),
                role=data["role"]
            )
            db.session.add(user)
            db.session.commit()

            return {"message": "User registered successfully", "user": user.to_dict()}, 201

        except Exception as e:
            app_logger.error({
                "function": "AuthService.register",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            db.session.rollback()
            return {"error": f"Failed to register user: {str(e)}"}, 500

    @staticmethod
    def login(data: dict) -> Tuple[dict, int]:
        try:
            if not data or not data.get("email") or not data.get("password"):
                return {"error": "Email and password are required"}, 400

            user = User.query.filter_by(email=data["email"]).first()
            if not user or not check_password_hash(user.password_hash, data["password"]):
                return {"error": "Invalid email or password"}, 401

            # Generate JWT token
            token = AuthAndLogMiddleware.generate_token(user.id, user.role, user.customer_id)
            return {
                "message": "Login successful",
                "token": token,
                "user": user.to_dict()
            }, 200

        except Exception as e:
            app_logger.error({
                "function": "AuthService.login",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            return {"error": f"Failed to login: {str(e)}"}, 500