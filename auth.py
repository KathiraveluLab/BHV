import os
import logging
import hmac
from flask import session, request
from models import User
from logging.handlers import RotatingFileHandler


SECURITY_LOG_PATH = os.path.join(os.getcwd(), "security.log")

security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)

if not security_logger.handlers:
    handler = RotatingFileHandler(
        SECURITY_LOG_PATH,
        maxBytes=5 * 1024 * 1024, 
        backupCount=3
    )
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
    handler.setFormatter(formatter)
    security_logger.addHandler(handler)
    security_logger.propagate = False


def log_event(event, user_id=None, username=None, role=None, details=None):
    ip = request.remote_addr if request else "N/A"
    ua = request.headers.get("User-Agent") if request else "N/A"

    message = (
        f"event={event} | "
        f"user_id={user_id} | "
        f"username={username} | "
        f"role={role} | "
        f"ip={ip} | "
        f"user_agent={ua} | "
        f"details={details}"
    )

    security_logger.info(message)


class AuthService:

    @staticmethod
    def authenticate(email, password):
        email_clean = email.strip().lower()

        admin_email = os.getenv("ADMIN_EMAIL")
        admin_pass = os.getenv("ADMIN_PASSWORD")

        if admin_email and email_clean == admin_email.strip().lower():
            if admin_pass and hmac.compare_digest(password.encode('utf-8'), admin_pass.encode('utf-8')):
                log_event(
                    event="ADMIN_LOGIN_SUCCESS",
                    user_id="SYSTEM_ADMIN_001",
                    username="System Admin",
                    role="admin"
                )
                return {
                    "id": "SYSTEM_ADMIN_001",
                    "name": "System Admin",
                    "role": "admin"
                }

            log_event(
                event="ADMIN_LOGIN_FAILED",
                username=email_clean,
                role="admin",
                details="Invalid admin password"
            )
            return None

        user = User.find_by_email(email_clean)

        if not user:
            log_event(
                event="LOGIN_FAILED",
                username=email_clean,
                role="user",
                details="User not found"
            )
            return None

        if user.get("password") is None and user.get("google_id"):
            log_event(
                event="LOGIN_BLOCKED",
                user_id=user["user_id"],
                username=user["name"],
                role=user["role"],
                details="Google account without password"
            )
            return {"error": "set_password_required"}

        if User.verify_password(user["password"], password):
            log_event(
                event="LOGIN_SUCCESS",
                user_id=user["user_id"],
                username=user["name"],
                role=user["role"]
            )
            return {
                "id": user["user_id"],
                "name": user["name"],
                "role": user["role"]
            }

        log_event(
            event="LOGIN_FAILED",
            user_id=user["user_id"],
            username=user["name"],
            role=user["role"],
            details="Invalid password"
        )
        return None

    @staticmethod
    def login_user(user_data):
        session.clear()
        session.permanent = True

        session["user_id"] = user_data["id"]
        session["name"] = user_data["name"]
        session["role"] = user_data["role"]

        log_event(
            event="SESSION_CREATED",
            user_id=user_data["id"],
            username=user_data["name"],
            role=user_data["role"]
        )

    @staticmethod
    def logout_user():
        log_event(
            event="LOGOUT",
            user_id=session.get("user_id"),
            username=session.get("name"),
            role=session.get("role")
        )
        session.clear()

    @staticmethod
    def is_system_admin(email):
        admin_email = os.getenv("ADMIN_EMAIL")
        if not admin_email or not email:
            return False
        return email.strip().lower() == admin_email.strip().lower()
