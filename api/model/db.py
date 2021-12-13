from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class PackageInfoWithImage(db.Model):
    __tablename__ = 'picture'

    id = db.Column(db.Integer, primary_key = True)
    image_name = db.Column(db.String(128))
    image_time = db.Column(db.DateTime, default=datetime.datetime.now())
    image_msg = db.Column(db.Integer)

class PackageInfoWithLog(db.Model):
    __tablename__ = 'log'

    int = db.Column(db.Integer, primary_key = True)
    log_msg = db.Column(db.String(128))
    log_time = db.Column(db.DateTime, default=datetime.datetime.now())