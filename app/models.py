from app.extensions import db
from flask_login import UserMixin

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    users = db.relationship('User', backref='role', lazy=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    doctor_visits = db.relationship('Visit', foreign_keys='Visit.doctor_id', backref='doctor', lazy=True)
    patient_visits = db.relationship('Visit', foreign_keys='Visit.patient_id', backref='patient', lazy=True)

    treatments = db.relationship('Treatment', backref='patient_user', lazy=True, foreign_keys='Treatment.patient_id')

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)

class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_assigned = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)
    medications = db.Column(db.Text)
    plan = db.Column(db.Text)
