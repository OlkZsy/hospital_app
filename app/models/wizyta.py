from app.extensions import db

class Wizyta(db.Model):
    __tablename__ = 'wizyty'
    id_wizyty = db.Column(db.Integer, primary_key=True)
    id_pacjenta = db.Column(db.Integer, db.ForeignKey('pacjenci.id_pacjenta'), nullable=False)
    id_lekarza = db.Column(db.Integer, db.ForeignKey('lekarze.id_lekarza'), nullable=False)
    data_wizyty = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    notatki = db.Column(db.Text)
    utworzona_przez = db.Column(db.Integer, db.ForeignKey('recepcjonisci.id_recepcjonisty'), nullable=True)
