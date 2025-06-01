from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class Pacjent(db.Model):
    __tablename__ = 'pacjenci'
    id_pacjenta = db.Column(db.Integer, primary_key=True)
    imie = db.Column(db.String(50), nullable=False)
    nazwisko = db.Column(db.String(50), nullable=False)
    pesel = db.Column(db.String(11), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    telefon = db.Column(db.String(15))
    adres = db.Column(db.Text)
    data_urodzenia = db.Column(db.Date)
    haslo_hash = db.Column(db.String(255), nullable=False)

    wizyty = db.relationship('Wizyta', backref='pacjent', lazy=True)
    recepty = db.relationship('Recepta', backref='pacjent', lazy=True)
    historia = db.relationship('HistoriaMedyczna', backref='pacjent', lazy=True)

    def set_password(self, password):
        self.haslo_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.haslo_hash, password)