from flask import render_template
from slidenotes.utils import decorators
import os

from slidenotes import app, cache

def include_file(filename):
    filename = os.path.join(app.root_path, app.static_folder, filename)
    with open(filename, "rb") as f:
        content = f.read().decode("utf-8")
    return content

app.jinja_env.globals.update(include_file=include_file)

@app.route("/", methods=["GET"])
@decorators.onlyproduction(cache.cached(timeout=3600))
def index():
    return render_template("index.html")

@app.route("/privacy", methods=["GET"])
def privacy():
    return render_template("privacy.html")
