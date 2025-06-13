from app.extensions import db
from flask_login import UserMixin

class Lekarz(UserMixin, db.Model):
    __tablename__ = 'lekarze'

    id_lekarza = db.Column(db.Integer, primary_key=True)
    imie = db.Column(db.String(50), nullable=False)
    nazwisko = db.Column(db.String(50), nullable=False)
    specjalizacja = db.Column(db.String(100))
    numer_licencji = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    telefon = db.Column(db.String(15))
    haslo_hash = db.Column(db.String(255), nullable=False)

    def get_id(self):
        return f"lekarz_{self.id_lekarza}"  # lekarz_1, lekarz_2, etc.
    
    wizyty = db.relationship('Wizyta', backref='lekarz', lazy=True)
    recepty = db.relationship('Recepta', backref='lekarz', lazy=True)
    historia = db.relationship('HistoriaMedyczna', backref='lekarz', lazy=True)
    harmonogram = db.relationship('HarmonogramLekarza', backref='lekarz', lazy=True)
