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

class ConversionOptions(admin_db.Model):
    id = admin_db.Column(admin_db.Integer, primary_key=True, autoincrement=True)
    slides = admin_db.Column(admin_db.Integer, nullable=False)
    trimlayout = admin_db.Column(admin_db.Boolean, nullable=False)
    trim = admin_db.Column(admin_db.Boolean, nullable=False)
    npage = admin_db.Column(admin_db.Integer, nullable=False)
    percentage = admin_db.Column(admin_db.Float, nullable=False)
    showlogo = admin_db.Column(admin_db.Boolean, nullable=False)
    conversions = admin_db.relationship('Conversion', backref='ConversionOptions', lazy=True)

    @staticmethod
    def get_option_id(original_layout, options):
        ids = ConversionOptions.query.filter_by(\
            slides=original_layout["slides"], trimlayout=original_layout["trim"], \
            trim=options["trim"], npage=options["npage"], percentage=options["percentage"], \
            showlogo=options["showlogo"] \
        ).all()

        if(len(ids) == 0):
            co = ConversionOptions( \
            slides=original_layout["slides"], trimlayout=original_layout["trim"], \
            trim=options["trim"], npage=options["npage"], percentage=options["percentage"], \
            showlogo=options["showlogo"])
            admin_db.session.add(co)
            admin_db.session.commit()
            return co.id
        else:
            return ids[0].id

class Conversion(admin_db.Model):
    task_id = admin_db.Column(admin_db.String(256), primary_key=True, nullable=False)
    file_id = admin_db.Column(admin_db.String(64), index=True, nullable=False)
    timestamp_uploaded = admin_db.Column(admin_db.DateTime, index=True, default=datetime.utcnow)
    duration = admin_db.Column(admin_db.Float, nullable=True)
    client_ua = admin_db.Column(admin_db.String(256), nullable=True)
    client_ip = admin_db.Column(admin_db.String(64), nullable=False)
    options_id = admin_db.Column(admin_db.Integer, admin_db.ForeignKey(ConversionOptions.id), nullable=False)
