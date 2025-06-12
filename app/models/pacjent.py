from app.extensions import db
from flask_login import UserMixin

class Pacjent(UserMixin, db.Model):
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


    def get_id(self):
        return str(self.id_pacjenta)
    

    