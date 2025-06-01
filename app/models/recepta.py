from app import db

class Recepta(db.Model):
    __tablename__ = 'recepty'

    id_recepty = db.Column(db.Integer, primary_key=True)
    id_pacjenta = db.Column(db.Integer, db.ForeignKey('pacjenci.id_pacjenta'), nullable=False)
    id_lekarza = db.Column(db.Integer, db.ForeignKey('lekarze.id_lekarza'), nullable=False)
    id_wizyty = db.Column(db.Integer, db.ForeignKey('wizyty.id_wizyty'), nullable=False)
    data_wystawienia = db.Column(db.Date, nullable=False)
    leki = db.Column(db.Text, nullable=False)
    instrukcje = db.Column(db.Text)