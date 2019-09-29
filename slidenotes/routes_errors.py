from werkzeug.exceptions import HTTPException
from flask import render_template, redirect

from slidenotes import app
from slidenotes.utils.clientinfo import client_wants_json
from slidenotes.utils.responses import jsonify_error

@app.errorhandler(Exception)
def error(error):
    if not isinstance(error, HTTPException):
        app.logger.exception(error)
        error.code = 500
        error.description = "A causa di un errore interno dell'applicazione, la richiesta non può essere portata a termine"

    if error.code == 301:
        return redirect(error.new_url, code=301)

    if error.code == 404:
        error.description = "Ops, la pagina richiesta non è stata trovata"

    if error.code == 429:
        error.description = "Forse è il caso di darsi una calmata"

    if client_wants_json():
        return jsonify_error(error.code, error.description), error.code

    return render_template("error.html", error_code=error.code, error_description=error.description), error.code
