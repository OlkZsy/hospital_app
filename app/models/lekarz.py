from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class Lekarz(db.Model):
    __tablename__ = 'lekarze'
    id_lekarza = db.Column(db.Integer, primary_key=True)
    imie = db.Column(db.String(50), nullable=False)
    nazwisko = db.Column(db.String(50), nullable=False)
    specjalizacja = db.Column(db.String(100))
    numer_licencji = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    telefon = db.Column(db.String(15))
    haslo_hash = db.Column(db.String(255), nullable=False)

    wizyty = db.relationship('Wizyta', backref='lekarz', lazy=True)
    recepty = db.relationship('Recepta', backref='lekarz', lazy=True)
    historia = db.relationship('HistoriaMedyczna', backref='lekarz', lazy=True)
    harmonogram = db.relationship('HarmonogramLekarza', backref='lekarz', lazy=True)

    def set_password(self, password):
        self.haslo_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.haslo_hash, password)
