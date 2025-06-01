from app import db

class HarmonogramLekarza(db.Model):
    __tablename__ = 'harmonogramy_lekarzy'

    id_harmonogramu = db.Column(db.Integer, primary_key=True)
    id_lekarza = db.Column(db.Integer, db.ForeignKey('lekarze.id_lekarza'), nullable=False)
    dzien_tygodnia = db.Column(db.String(20), nullable=False)
    godzina_start = db.Column(db.Time, nullable=False)
    godzina_koniec = db.Column(db.Time, nullable=False)