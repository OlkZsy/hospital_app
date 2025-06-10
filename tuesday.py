# add_tuesday.py
from app import create_app
from app.extensions import db
from app.models.lekarz import Lekarz
from app.models.harmonogram import HarmonogramLekarza
from datetime import time

app = create_app()

with app.app_context():
    doctor = Lekarz.query.first()
    if not doctor:
        print("Brak lekarza")
        exit()
    
    # Добавляем расписание на вторник
    existing = HarmonogramLekarza.query.filter_by(
        id_lekarza=doctor.id_lekarza,
        dzien_tygodnia='Wtorek'
    ).first()
    
    if not existing:
        harmonogram = HarmonogramLekarza(
            id_lekarza=doctor.id_lekarza,
            dzien_tygodnia='Wtorek',
            godzina_start=time(9, 0),
            godzina_koniec=time(17, 0)
        )
        db.session.add(harmonogram)
        db.session.commit()
        print("Dodano harmonogram na wtorek 9:00-17:00")
    else:
        print("Harmonogram na wtorek już istnieje")