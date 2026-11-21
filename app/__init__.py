from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    })


db = SQLAlchemy(model_class=Base)
migrate = Migrate()

app = Flask(__name__)
app.config.from_pyfile("../config.py")
app.config.setdefault("MAX_CONTENT_LENGTH", 5 * 1024 * 1024)
app.config.setdefault("UPLOAD_FOLDER", "")
csrf = CSRFProtect(app)
db.init_app(app)
migrate.init_app(app, db)

from . import views
from .users import users_bp
from .products import products_bp
from .products import models  # noqa: F401

app.register_blueprint(users_bp)
app.register_blueprint(products_bp)
