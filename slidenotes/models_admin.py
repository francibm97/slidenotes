from slidenotes import admin_db, admin_login_manager
from flask_login import UserMixin

@admin_login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(admin_db.Model, UserMixin):
    id = admin_db.Column(admin_db.Integer, primary_key=True)
    username = admin_db.Column(admin_db.String(20), unique=True, nullable=False)
    password = admin_db.Column(admin_db.String(60), nullable=False)

    def __repr__(self):
        return "User('" + self.username + "')"
