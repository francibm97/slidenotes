from slidenotes import admin_db, admin_login_manager
from flask_login import UserMixin
from datetime import datetime

@admin_login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(admin_db.Model, UserMixin):
    id = admin_db.Column(admin_db.Integer, primary_key=True)
    username = admin_db.Column(admin_db.String(20), unique=True, nullable=False)
    password = admin_db.Column(admin_db.String(60), nullable=False)

    def __repr__(self):
        return "User('" + self.username + "')"

class Conversion(admin_db.Model):
    task_id = admin_db.Column(admin_db.String(256), primary_key=True, nullable=False)
    file_id = admin_db.Column(admin_db.String(64), index=True, nullable=False)
    timestamp_uploaded = admin_db.Column(admin_db.DateTime, index=True, default=datetime.utcnow)
    timestamp_processed = admin_db.Column(admin_db.DateTime, nullable=True)
    client_ua = admin_db.Column(admin_db.String(256), nullable=True)
    client_ip = admin_db.Column(admin_db.String(64), nullable=False)
