from flask import Flask
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_pyfile("../config.py")
app.config.setdefault("MAX_CONTENT_LENGTH", 5 * 1024 * 1024)
app.config.setdefault("UPLOAD_FOLDER", "")
csrf = CSRFProtect(app)

from . import views
from .users import users_bp
from .products import products_bp

app.register_blueprint(users_bp)
app.register_blueprint(products_bp)
