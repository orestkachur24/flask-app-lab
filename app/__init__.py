import os

from flask import Flask, render_template
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
csrf = CSRFProtect()
bcrypt = Bcrypt()
login_manager = LoginManager()
CONFIGS = {
    "development": "app.config.DevelopmentConfig",
    "testing": "app.config.TestingConfig",
    "production": "app.config.ProductionConfig",
}


def create_app(config_name=None):
    app = Flask(__name__, instance_relative_config=True)
    selected = (config_name or os.getenv("FLASK_CONFIG", "development")).lower()
    app.config.from_object(CONFIGS.get(selected, CONFIGS["development"]))
    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "users.login"
    login_manager.login_message = "Увійдіть, щоб отримати доступ до цієї сторінки."
    login_manager.login_message_category = "warning"
    from . import models  # noqa: F401
    from .views import site_bp
    from .users import users_bp
    from .products import products_bp
    from .posts import posts_bp
    app.register_blueprint(site_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(posts_bp)

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    return app


app = create_app(os.getenv("FLASK_CONFIG", "development"))
