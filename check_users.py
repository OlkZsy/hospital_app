from app import create_app
from app.extensions import db
from app.models.recepcjonista import Recepcjonista
from app.models.pacjent import Pacjent
from app.models.administrator import Administrator
from app.models.lekarz import Lekarz

app = create_app()

with app.app_context():
    print("=== WSZYSTKIE UŻYTKOWNICY ===")
    
    admins = Administrator.query.all()
    print(f"\nADMINISTRATORZY ({len(admins)}):")
    for admin in admins:
        print(f"  - {admin.email} | {admin.imie} {admin.nazwisko}")
    
    lekarze = Lekarz.query.all()
    print(f"\nLEKARZE ({len(lekarze)}):")
    for lekarz in lekarze:
        print(f"  - {lekarz.email} | {lekarz.imie} {lekarz.nazwisko}")
    
    pacjenci = Pacjent.query.all()
    print(f"\nPACJENCI ({len(pacjenci)}):")
    for pacjent in pacjenci:
        print(f"  - {pacjent.email} | {pacjent.imie} {pacjent.nazwisko}")
    
    recepcjonisci = Recepcjonista.query.all()
    print(f"\nRECEPCJONIŚCI ({len(recepcjonisci)}):")
    for rec in recepcjonisci:
        print(f"  - {rec.email} | {rec.imie} {rec.nazwisko}")
    
    print("\n=== SPRAWDZENIE KONKRETNEGO EMAIL ===")
    email = "recepcja@test.com"
    
    admin = Administrator.query.filter_by(email=email).first()
    lekarz = Lekarz.query.filter_by(email=email).first()
    pacjent = Pacjent.query.filter_by(email=email).first()
    recepcjonista = Recepcjonista.query.filter_by(email=email).first()
    
    print(f"Email {email} znaleziony jako:")
    print(f"  Administrator: {'TAK' if admin else 'NIE'}")
    print(f"  Lekarz: {'TAK' if lekarz else 'NIE'}")
    print(f"  Pacjent: {'TAK' if pacjent else 'NIE'}")
    print(f"  Recepcjonista: {'TAK' if recepcjonista else 'NIE'}")