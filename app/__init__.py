
import os

from flask import Flask
from werkzeug.security import generate_password_hash

from config import Config
from app.extensions import db, login_manager, csrf


def create_app(config_class=Config):

    # Create Flask application
    app = Flask(
        __name__,
        instance_relative_config=True
    )

    # Load configuration
    app.config.from_object(config_class)

    # Create instance folder if it does not exist
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "auth.login"

    with app.app_context():
        from app.models import User

        db.create_all()
        admin_user = db.session.query(User).filter_by(
            email=app.config["ADMIN_EMAIL"]
        ).first()
        if admin_user is None:
            db.session.add(User(
                full_name="System Administrator",
                email=app.config["ADMIN_EMAIL"],
                password_hash=generate_password_hash(
                    app.config["ADMIN_PASSWORD"]
                ),
                role="admin"
            ))
            db.session.commit()

    # Register application routes
    from app.routes import main
    from app.auth import auth
    from app.admin import admin
    from app.examiner import examiner
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(examiner)

    return app
