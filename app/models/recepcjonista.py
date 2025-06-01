from app.extensions import db
from flask_login import UserMixin

class Recepcjonista(db.Model, UserMixin):
    __tablename__ = 'recepcjonisci'
    id_recepcjonisty = db.Column(db.Integer, primary_key=True)
    imie = db.Column(db.String(50), nullable=False)
    nazwisko = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True)
    telefon = db.Column(db.String(15))
    haslo_hash = db.Column(db.String(255), nullable=False)

    wizyty_utworzone = db.relationship('Wizyta', backref='autor', lazy=True, foreign_keys='Wizyta.utworzona_przez')
