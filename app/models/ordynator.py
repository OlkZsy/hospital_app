from app.extensions import db
from flask_login import UserMixin

class Ordynator(db.Model, UserMixin):
    __tablename__ = 'ordynatorzy'

    id_ordynatora = db.Column(db.Integer, primary_key=True)
    imie = db.Column(db.String(50), nullable=False)
    nazwisko = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True)
    telefon = db.Column(db.String(15))
    haslo_hash = db.Column(db.String(255), nullable=False)
    dzial = db.Column(db.String(100))  # Dział/specjalizacja ordynatora
    uprawnienia = db.Column(db.String(100), default='ordynator')  # Dodatkowe uprawnienia

    def get_id(self):
        return f"ordynator_{self.id_ordynatora}"  # ordynator_1, ordynator_2, etc.