from flask import Blueprint, current_app, request, render_template, redirect, send_file, url_for, flash, abort
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from slidenotes import admin_db, bcrypt
from slidenotes.models_admin import User, Conversion
from slidenotes.utils.responses import jsonify_success
from slidenotes.gs.slide_preview import generate_slide_preview
import datetime, os, sqlalchemy, string

admin = Blueprint("admin", __name__)

@admin.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.index"))
    if not User.query.filter_by(username="root").first():
        return redirect(url_for("admin.register"))

    if request.form.get("password") :
        user = User.query.filter_by(username="root").first()
        if user and bcrypt.check_password_hash(user.password, request.form.get("password")):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("admin.index"))
        else:
            flash("Password errata", "danger")
    return render_template("admin_login.html")
    #return '<form method="POST" action="/admin/login"><input type="password" name="password"><input type="submit" value="Invia">'

@admin.route("/register", methods=['GET', 'POST'])
def register():
    if User.query.filter_by(username="root").first():
        return redirect(url_for("admin.login"))
    if request.form.get("password") :
        hashed_password = bcrypt.generate_password_hash(request.form.get("password")).decode("utf-8")
        user = User(username="root", password=hashed_password)
        admin_db.session.add(user)
        admin_db.session.commit()
        flash("L'account è stato creato, ora puoi effettuare il login", "success")
        return redirect(url_for("admin.login"))
    return render_template("admin_register.html")

@admin.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@admin.route("/")
@login_required
def index():
    return render_template("admin_index.html")

@admin.route("/conversions")
@login_required
def conversions():
    conversions = Conversion.query.order_by(Conversion.timestamp_uploaded.desc()).all()
    return render_template("admin_conversions.html", conversions=conversions)

@admin.route("/file_preview/<client_filename>")
@login_required
def file_preview(client_filename):
    file_id = secure_filename(client_filename)
    if not os.path.isfile(os.path.join(current_app.config["UPLOAD_FOLDER"], file_id)):
        abort(404, "Il file richiesto non è presente")
    file_preview_path = generate_slide_preview(os.path.join(current_app.config["UPLOAD_FOLDER"], file_id))
    response = send_file(file_preview_path)
    response.headers["Content-Type"] = "image/jpeg"
    return response

@admin.route("/file_download/<client_filename>")
@login_required
def file_download(client_filename):
    file_id = secure_filename(client_filename)
    filename = os.path.join(current_app.config["UPLOAD_FOLDER"], file_id)
    if not os.path.isfile(filename):
        abort(404, "Il file richiesto non è presente")
    response = send_file(filename)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename={filename}.pdf".format(filename=file_id)
    return response

@admin.route("/conversions_per_file")
@login_required
def conversions_per_file():
    conversions = \
        admin_db.session.query( \
            Conversion.file_id, \
            sqlalchemy.func.count(Conversion.file_id), \
            sqlalchemy.func.max(Conversion.duration), \
            sqlalchemy.func.avg(Conversion.duration), \
            sqlalchemy.func.min(Conversion.duration) \
        ) \
        .filter(Conversion.timestamp_uploaded >= (datetime.datetime.utcnow() - datetime.timedelta(days=60))) \
        .group_by(Conversion.file_id) \
        .order_by( sqlalchemy.func.count(Conversion.file_id).desc()).all()
    conversions = [{"file_id": str(el[0]), "count": str(el[1]), "max_duration": float(el[2]), "avg_duration": float(el[3]), "min_duration": float(el[4])} for el in conversions]

    return render_template("admin_conversions_per_file.html", conversions=conversions)

@admin.route("/conversions_per_file/<client_filename>")
@login_required
def conversions_per_file_details(client_filename):
    conversions = Conversion.query.filter_by(file_id=client_filename).order_by(Conversion.timestamp_uploaded.desc()).all()
    return render_template("admin_conversions.html", conversions=conversions)

@admin.route("/conversions_per_dates")
@login_required
def conversions_per_dates():
    conversions_dates = dict(admin_db.session.query(sqlalchemy.func.strftime("%Y-%m-%d", Conversion.timestamp_uploaded), sqlalchemy.func.count(sqlalchemy.func.strftime("%Y-%m-%d", Conversion.timestamp_uploaded))).filter(Conversion.timestamp_uploaded >= (datetime.datetime.today() - datetime.timedelta(days=60))).group_by(sqlalchemy.func.strftime("%Y-%m-%d", Conversion.timestamp_uploaded)).all())
    dates = list(reversed([(datetime.datetime.today() - datetime.timedelta(days=days)).strftime("%Y-%m-%d") for days in range(0,60)]))
    return jsonify_success({"dates": dates, "counts": [conversions_dates.get(date, 0) for date in dates]})
