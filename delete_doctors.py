# delete_doctors.py
from app import create_app
from app.extensions import db
from app.models.lekarz import Lekarz
from app.models.wizyta import Wizyta
from app.models.recepta import Recepta
from app.models.historia import HistoriaMedyczna
from app.models.harmonogram import HarmonogramLekarza

app = create_app()

with app.app_context():
    print("Sprawdzanie liczby lekarzy w bazie...")
    doctors_count = Lekarz.query.count()
    print(f"Znaleziono {doctors_count} lekarzy.")
    
    if doctors_count == 0:
        print("Brak lekarzy do usunięcia.")
        exit()
    
    # Wyświetlamy wszystех врачей
    doctors = Lekarz.query.all()
    print("\nLista lekarzy do usunięcia:")
    for doctor in doctors:
        print(f"- {doctor.imie} {doctor.nazwisko} ({doctor.email})")
    
    # Подтверждение
    confirm = input(f"\nCzy na pewno chcesz usunąć wszystkich {doctors_count} lekarzy? [tak/nie]: ")
    if confirm.lower() not in ['tak', 'yes', 'y', 't']:
        print("Anulowano.")
        exit()
    
    try:
        # Удаляем связанные записи
        print("\nUsuwanie powiązanych danych...")
        
        # 1. Удаляем расписания
        harmonogramy_count = HarmonogramLekarza.query.filter(
            HarmonogramLekarza.id_lekarza.in_([d.id_lekarza for d in doctors])
        ).count()
        if harmonogramy_count > 0:
            HarmonogramLekarza.query.filter(
                HarmonogramLekarza.id_lekarza.in_([d.id_lekarza for d in doctors])
            ).delete(synchronize_session=False)
            print(f"- Usunięto {harmonogramy_count} harmonogramów")
        
        # 2. Удаляем рецепты
        recepty_count = Recepta.query.filter(
            Recepta.id_lekarza.in_([d.id_lekarza for d in doctors])
        ).count()
        if recepty_count > 0:
            Recepta.query.filter(
                Recepta.id_lekarza.in_([d.id_lekarza for d in doctors])
            ).delete(synchronize_session=False)
            print(f"- Usunięto {recepty_count} recept")
        
        # 3. Удаляем историю медицинскую
        historia_count = HistoriaMedyczna.query.filter(
            HistoriaMedyczna.id_lekarza.in_([d.id_lekarza for d in doctors])
        ).count()
        if historia_count > 0:
            HistoriaMedyczna.query.filter(
                HistoriaMedyczna.id_lekarza.in_([d.id_lekarza for d in doctors])
            ).delete(synchronize_session=False)
            print(f"- Usunięto {historia_count} wpisów historii medycznej")
        
        # 4. Удаляем визиты
        wizyty_count = Wizyta.query.filter(
            Wizyta.id_lekarza.in_([d.id_lekarza for d in doctors])
        ).count()
        if wizyty_count > 0:
            Wizyta.query.filter(
                Wizyta.id_lekarza.in_([d.id_lekarza for d in doctors])
            ).delete(synchronize_session=False)
            print(f"- Usunięto {wizyty_count} wizyt")
        
        # 5. Наконец удаляем врачей
        Lekarz.query.delete()
        print(f"- Usunięto {doctors_count} lekarzy")
        
        # Сохраняем изменения
        db.session.commit()
        print(f"\n✅ Pomyślnie usunięto wszystkich lekarzy i powiązane dane!")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Błąd podczas usuwania: {str(e)}")
        print("Rollback wykonany - żadne dane nie zostały usunięte.")