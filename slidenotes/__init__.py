from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address, get_ipaddr
import os

from slidenotes.celery import make_celery

app = Flask(__name__, static_url_path="", static_folder="static")
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../uploaded_files")
app.config['CELERY_BROKER_URL'] = "amqp://localhost"
app.config['CELERY_RESULT_BACKEND'] = "db+sqlite:///result.sqlite"
#app.config['CELERY_RESULT_BACKEND'] = "db+mysql+pymysql://pdfgen:pdfgen@127.0.0.1/pdfgen_main"

# >>> import uuid
# >>> uuid.uuid4().hex
app.config['SECRET_KEY'] = 'd20877b0215d4144b58e289cf6c9451b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../admin.sqlite'
admin_db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
admin_login_manager = LoginManager(app)
admin_login_manager.login_view = 'admin.login'
admin_login_manager.login_message = ''
if not os.path.isfile("../admin.sqlite"):
    from slidenotes.models_admin import User, Conversion
    admin_db.create_all()
    admin_db.session.commit()

# get_ipaddr -> guarda X-Forwarded-for e se non c'è guarda l'ip
# get_remote_address -> guarda solo l'ip
limiter = Limiter(app, key_func=get_ipaddr)

cache = Cache(app,config={"CACHE_TYPE": "simple"})
celery = make_celery(app)

from slidenotes import routes

from slidenotes import routes_errors

from slidenotes.routes_backend import backend
app.register_blueprint(backend, url_prefix="/file/")

from slidenotes.routes_admin import admin
app.register_blueprint(admin, url_prefix="/admin/")
