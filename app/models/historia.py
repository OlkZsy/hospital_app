from app.extensions import db

class HistoriaMedyczna(db.Model):
    __tablename__ = 'historia_medyczna'
    id_wpisu = db.Column(db.Integer, primary_key=True)
    id_pacjenta = db.Column(db.Integer, db.ForeignKey('pacjenci.id_pacjenta'), nullable=False)
    id_lekarza = db.Column(db.Integer, db.ForeignKey('lekarze.id_lekarza'), nullable=False)
    data_wpisu = db.Column(db.Date, nullable=False)
    diagnoza = db.Column(db.Text)
    notatki = db.Column(db.Text)
