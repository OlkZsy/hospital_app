from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class Administrator(db.Model):
    __tablename__ = 'administratorzy'
    id_administratora = db.Column(db.Integer, primary_key=True)
    imie = db.Column(db.String(50), nullable=False)
    nazwisko = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True)
    telefon = db.Column(db.String(15))
    haslo_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.haslo_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.haslo_hash, password)