
import os


class Config:
    # Secret key used for session security and CSRF protection
    SECRET_KEY = os.environ.get(
        "EMP_SECRET_KEY",
        "dev-only-change-this-key"
    )

    # SQLite database configuration
    SQLALCHEMY_DATABASE_URI = "sqlite:///emp.db"

    # Disable unnecessary SQLAlchemy event tracking
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ADMIN_EMAIL = os.environ.get(
        "EMP_ADMIN_EMAIL",
        "admin@emp.local"
    )
    ADMIN_PASSWORD = os.environ.get(
        "EMP_ADMIN_PASSWORD",
        "admin12345"
    )
