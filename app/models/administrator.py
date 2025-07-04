from app.extensions import db
from flask_login import UserMixin

class Administrator(db.Model, UserMixin):
    __tablename__ = 'administratorzy'

    id = db.Column('id_administratora', db.Integer, primary_key=True)
    imie = db.Column(db.String(50), nullable=False)
    nazwisko = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True)
    telefon = db.Column(db.String(15))
    haslo_hash = db.Column(db.String(255), nullable=False)

    def get_id(self):
        return f"admin_{self.id}"  # admin_1, admin_2, etc.