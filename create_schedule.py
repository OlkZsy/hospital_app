# create_schedule.py
from app import create_app
from app.extensions import db
from app.models.lekarz import Lekarz
from app.models.harmonogram import HarmonogramLekarza
from datetime import time

app = create_app()

with app.app_context():
    # Находим первого врача
    doctor = Lekarz.query.first()
    if not doctor:
        print("Nie znaleziono lekarza. Najpierw utwórz lekarza.")
        exit()
    
    # Создаем расписание на всю неделю
    schedule_data = [
        ('Poniedziałek', time(9, 0), time(17, 0)),
        ('Wtorek', time(9, 0), time(17, 0)),
        ('Środa', time(9, 0), time(17, 0)),
        ('Czwartek', time(9, 0), time(17, 0)),
        ('Piątek', time(9, 0), time(16, 0)),
    ]
    
    for day, start, end in schedule_data:
        existing = HarmonogramLekarza.query.filter_by(
            id_lekarza=doctor.id_lekarza,
            dzien_tygodnia=day
        ).first()
        
        if not existing:
            harmonogram = HarmonogramLekarza(
                id_lekarza=doctor.id_lekarza,
                dzien_tygodnia=day,
                godzina_start=start,
                godzina_koniec=end
            )
            db.session.add(harmonogram)
            print(f"Dodano harmonogram: {day} {start}-{end}")
    
    db.session.commit()
    print(f"Harmonogram utworzony dla {doctor.imie} {doctor.nazwisko}")