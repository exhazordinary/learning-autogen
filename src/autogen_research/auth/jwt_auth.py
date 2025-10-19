"""JWT authentication utilities."""

import os
from datetime import timedelta
from functools import wraps

from flask import jsonify, request
from flask_jwt_extended import (
    JWTManager,
    get_jwt_identity,
    verify_jwt_in_request,
)
from flask_jwt_extended import (
    create_access_token as jwt_create_access_token,
)
from werkzeug.security import check_password_hash, generate_password_hash

from ..utils.logger import get_logger

logger = get_logger(__name__)

# Simple in-memory user store (replace with database in production)
USERS = {}


def init_jwt(app) -> JWTManager:
    """
    Initialize JWT for Flask app.

    Args:
        app: Flask application

    Returns:
        JWTManager instance
    """
    # Configure JWT
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
        hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS", "24"))
    )

    jwt = JWTManager(app)
    logger.info("JWT authentication initialized")

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Invalid token"}), 401

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({"error": "Missing authorization token"}), 401

    return jwt


def create_access_token(username: str, additional_claims: dict = None) -> str:
    """
    Create a JWT access token for a user.

    Args:
        username: Username
        additional_claims: Additional claims to include in token

    Returns:
        JWT access token string
    """
    claims = additional_claims or {}
    return jwt_create_access_token(identity=username, additional_claims=claims)


def create_user(username: str, password: str) -> bool:
    """
    Create a new user (in-memory storage).

    Args:
        username: Username
        password: Plain text password (will be hashed)

    Returns:
        True if user created, False if user already exists
    """
    if username in USERS:
        return False

    USERS[username] = {
        "username": username,
        "password_hash": generate_password_hash(password),
    }

    logger.info(f"User created: {username}")
    return True


def verify_user(username: str, password: str) -> bool:
    """
    Verify user credentials.

    Args:
        username: Username
        password: Plain text password

    Returns:
        True if credentials are valid, False otherwise
    """
    user = USERS.get(username)
    if not user:
        return False

    return check_password_hash(user["password_hash"], password)


def jwt_required_optional(fn):
    """
    Decorator that makes JWT optional but extracts identity if present.

    If token is present and valid, sets g.user_id.
    If token is missing or invalid, allows request to proceed without user_id.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
            # Token is valid, get identity
            identity = get_jwt_identity()
            request.user_id = identity if identity else None
        except Exception:
            # Token is invalid or missing, proceed without user
            request.user_id = None

        return fn(*args, **kwargs)

    return wrapper


def get_current_user() -> str | None:
    """
    Get current authenticated user from request.

    Returns:
        Username if authenticated, None otherwise
    """
    return getattr(request, "user_id", None)
