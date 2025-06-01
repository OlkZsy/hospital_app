from app.extensions import db

class HarmonogramLekarza(db.Model):
    __tablename__ = 'harmonogramy_lekarzy'
    id_harmonogramu = db.Column(db.Integer, primary_key=True)
    id_lekarza = db.Column(db.Integer, db.ForeignKey('lekarze.id_lekarza'), nullable=False)
    dzien_tygodnia = db.Column(db.String(20))
    godzina_start = db.Column(db.Time)
    godzina_koniec = db.Column(db.Time)
