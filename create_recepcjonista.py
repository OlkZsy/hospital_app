from app import create_app
from app.extensions import db
from app.models.recepcjonista import Recepcjonista
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    email = "recepcja@test.com"
    password = "recepcja123"
    
    # Удали если существует
    existing = Recepcjonista.query.filter_by(email=email).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
    
    # Создай нового
    recepcjonista = Recepcjonista(
        imie="Test",
        nazwisko="Recepcjonista", 
        email=email,
        telefon="123456789",
        haslo_hash=generate_password_hash(password)
    )
    
    db.session.add(recepcjonista)
    db.session.commit()
    print(f"✅ Recepcjonista utworzony: {email} / {password}")