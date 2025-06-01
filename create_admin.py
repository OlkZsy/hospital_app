# create_admin.py
from app import create_app
from app.extensions import db
from app.models.administrator import Administrator
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    email = "admin@example.com"
    password = "adminadmin"
    imie = "Admin"
    nazwisko = "Admin"
    telefon = "555444333"

    if Administrator.query.filter_by(email=email).first():
        print("Administrator already exists.")
    else:
        admin = Administrator(
            imie=imie,
            nazwisko=nazwisko,
            email=email,
            telefon=telefon,
            haslo_hash=generate_password_hash(password)
        )
        db.session.add(admin)
        db.session.commit()
        print("Administrator created successfully.")
