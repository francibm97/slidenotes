from flask import Flask
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

# get_ipaddr -> guarda X-Forwarded-for e se non c'è guarda l'ip
# get_remote_address -> guarda solo l'ip
limiter = Limiter(app, key_func=get_ipaddr)

cache = Cache(app,config={"CACHE_TYPE": "simple"})
celery = make_celery(app)

from slidenotes import routes

from slidenotes import routes_errors

from slidenotes.routes_backend import backend
app.register_blueprint(backend, url_prefix="/file/")
