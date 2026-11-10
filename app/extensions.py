
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect


# Database extension
db = SQLAlchemy()

# Authentication extension
login_manager = LoginManager()

# CSRF protection
csrf = CSRFProtect()


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return db.session.get(User, user_id)