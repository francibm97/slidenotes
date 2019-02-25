from flask import Blueprint, current_app, request, render_template, send_file, abort
from werkzeug.utils import secure_filename
import os

from slidenotes.utils.clientinfo import client_wants_json
from slidenotes.utils.responses import jsonify_success
from slidenotes.utils.file import is_pdf, sha256
from slidenotes.tasks import generate_pdf
from slidenotes import limiter

backend = Blueprint("backend", __name__)

def has_already_been_uploaded(client_filename):
    return os.path.isfile(os.path.join(current_app.config["UPLOAD_FOLDER"], secure_filename(client_filename)))

@backend.route("/cache/<file_id>", methods=["GET"])
def task_has_cached_file(file_id):
    if has_already_been_uploaded(file_id):
        return jsonify_success({"cached": True})
    else:
        return jsonify_success({"cached": False})

@backend.route("/download/<task_id>", methods=["GET"])
@limiter.limit("30 per hour")
def task_download(task_id):
    task = generate_pdf.AsyncResult(task_id)
    if task.state == "SUCCESS":
        filename = os.path.join(current_app.config["UPLOAD_FOLDER"], task.info.get("filename", ""))
        if not os.path.isfile(filename):
            abort(410, "Il file richiesto non è più presente")
        response = send_file(filename)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = "attachment; filename={filename}.pdf".format(filename=task_id)
        return response
    else:
        abort(400, "Il file richiesto non è ancora stato generato o non esiste")

@backend.route("/status/<task_id>", methods=["GET"])
def task_status(task_id):
    task = generate_pdf.AsyncResult(task_id)
    response = { "status": task.state }
    try:
        response["progress"] = task.info.get("progress", 0)
    except:
        response["progress"] = 0
    if client_wants_json():
        return jsonify_success(response)
    return render_template("job.html", task_id=task_id, **response)

@backend.route("/upload", methods=["POST"])
@limiter.limit("5 per minute")
@limiter.limit("20 per hour")
def task_upload():
    form_file = "file"
    form_sha256 = "sha256"
    form_trim = "trim"
    form_percentage = "percentage"
    form_npage = "npage"
    form_layout = "layout"
    form_privacy = "privacy"

    if request.form.get(form_privacy) == None:
        abort(400, "Senza aver accettato l'informativa sulla privacy non è possibile proseguire")

    if (form_file not in request.files or request.files[form_file].filename == "") \
       and form_sha256 not in request.form:
        abort(400, "Manca sia il file sia il suo sha256. Inviare almeno uno dei due")

    if (form_file not in request.files or request.files[form_file].filename == "")  \
       and form_sha256 in request.form \
       and not has_already_been_uploaded(request.form[form_sha256]):
        abort(400, "Questo sha256 non corrisponde a nessun file sul server")

    if form_file in request.files and request.files[form_file].filename != "":
        file = request.files[form_file]
        if file and is_pdf(file):
            filename = sha256(file)
            file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
        else :
            abort(400, "PDF è il solo formato accettato")
    else :
        filename = request.form[form_sha256]

    trim = (request.form.get(form_trim) != None)

    try:
        npage = int(request.form[form_npage])
        if npage != 1 and npage != 2 and npage != 3:
            raise ValueError
    except KeyError:
        npage = 3
    except ValueError:
        npage = 3

    try:
        percentage = int(request.form[form_percentage])
        if percentage < 45 or percentage > 55:
            raise ValueError
    except KeyError:
        percentage = 50
    except ValueError:
        percentage = 50

    percentage = float(percentage) / 100

    try:
        layout = abs(int(request.form[form_layout]))
        if layout != 1 and layout != 2:
            raise ValueError
    except KeyError:
        layout = 1
    except ValueError:
        layout = 1

    task = generate_pdf.delay(filename=filename, layout_id=layout, options={"trim": trim, "npage": npage, "percentage": percentage})
    if client_wants_json():
        return jsonify_success({"task_id": task.id}), 202
    return render_template("job.html", task_id=task.id, status="PENDING", progress=0), 202
