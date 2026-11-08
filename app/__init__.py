
import os

from flask import Flask

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

    # Register application routes
    from app.routes import main
    app.register_blueprint(main)

    return app
