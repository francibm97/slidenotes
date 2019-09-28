from flask import Blueprint, current_app, request, render_template, redirect, send_file, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from slidenotes import admin_db, bcrypt
from slidenotes.models_admin import User, Conversion
from slidenotes.utils.responses import jsonify_success
import os, sqlalchemy

admin = Blueprint("admin", __name__)

@admin.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.home"))
    if not User.query.filter_by(username="root").first():
        return redirect(url_for("admin.register"))

    if request.form.get("password") :
        user = User.query.filter_by(username="root").first()
        if user and bcrypt.check_password_hash(user.password, request.form.get("password")):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("admin.home"))
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
def home():
    conversions = Conversion.query.order_by(Conversion.timestamp_uploaded.desc()).all()
    for i in range(0, len(conversions)):
        try:
            conversions[i].duration = (conversions[i].timestamp_processed - conversions[i].timestamp_uploaded).total_seconds()
        except Exception:
            conversions[i].duration = -1
    return render_template("admin_conversions.html", conversions=conversions)

@admin.route("/conversions_per_dates")
@login_required
def conversions_per_dates():
    conversions = admin_db.session.query(sqlalchemy.func.strftime("%Y-%m-%d", Conversion.timestamp_uploaded), sqlalchemy.func.count(sqlalchemy.func.strftime("%Y-%m-%d", Conversion.timestamp_uploaded))).group_by(sqlalchemy.func.strftime("%Y-%m-%d", Conversion.timestamp_uploaded)).all()
    return jsonify_success({"dates": [str(el[0]) for el in conversions], "counts": [str(el[1]) for el in conversions]})
