from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.forms import RegisterUserForm
from app.models.lekarz import Lekarz
from app.models.recepcjonista import Recepcjonista
from app.models.administrator import Administrator
from app.models.pacjent import Pacjent
from app.models.wizyta import Wizyta
from app.extensions import db
from datetime import datetime, date, timedelta
from app.models.ordynator import Ordynator



administrator_bp = Blueprint('administrator_bp', __name__, url_prefix='/administrator')

@administrator_bp.route('/dashboard')
@login_required
def dashboard():
    if not isinstance(current_user, Administrator):
        return "Access Denied", 403
    return render_template('dashboards/administrator.html', user=current_user)

@administrator_bp.route('/wizyty')
@login_required
def wizyty():
    if not isinstance(current_user, Administrator):
        return "Access Denied", 403
    
    # Parametry filtrowania
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()
    doctor_filter = request.args.get('doctor', '').strip()
    
    # Bazowe zapytanie
    query = Wizyta.query.join(Pacjent).join(Lekarz)
    
    # Filtrowanie po wyszukiwaniu
    if search_query:
        search_filter = db.or_(
            Pacjent.imie.ilike(f'%{search_query}%'),
            Pacjent.nazwisko.ilike(f'%{search_query}%'),
            Pacjent.email.ilike(f'%{search_query}%'),
            Lekarz.imie.ilike(f'%{search_query}%'),
            Lekarz.nazwisko.ilike(f'%{search_query}%'),
            Lekarz.email.ilike(f'%{search_query}%')
        )
        query = query.filter(search_filter)
    
    # Filtrowanie po statusie
    if status_filter:
        query = query.filter(Wizyta.status == status_filter)
    
    # Filtrowanie po dacie
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Wizyta.data_wizyty) >= date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Wizyta.data_wizyty) <= date_to_obj)
        except ValueError:
            pass
    
    # Filtrowanie po lekarzu
    if doctor_filter:
        try:
            doctor_id = int(doctor_filter)
            query = query.filter(Wizyta.id_lekarza == doctor_id)
        except ValueError:
            pass
    
    # Pobierz wyniki
    wizyty = query.order_by(Wizyta.data_wizyty.desc()).all()
    
    # Statystyki
    all_visits = Wizyta.query.all()
    total_visits = len(all_visits)
    planned_visits = len([w for w in all_visits if w.status == 'zaplanowana'])
    completed_visits = len([w for w in all_visits if w.status == 'zakonczona'])
    cancelled_visits = len([w for w in all_visits if w.status == 'anulowana'])
    
    # Lista lekarzy dla filtra
    doctors = Lekarz.query.order_by(Lekarz.nazwisko).all()
    
    # Pomocnicze zmienne dla template
    from datetime import date, timedelta
    today = date.today()
    tomorrow = today + timedelta(days=1)
    now = datetime.now()
    
    # Czy filtry są aktywne
    filter_active = bool(search_query or status_filter or date_from or date_to or doctor_filter)
    
    # Formatowanie zakresu dat
    date_range = ""
    if date_from and date_to:
        date_range = f"{date_from} - {date_to}"
    elif date_from:
        date_range = f"od {date_from}"
    elif date_to:
        date_range = f"do {date_to}"
    
    return render_template('administrator/wizyty.html',
                         wizyty=wizyty,
                         total_visits=total_visits,
                         planned_visits=planned_visits,
                         completed_visits=completed_visits,
                         cancelled_visits=cancelled_visits,
                         doctors=doctors,
                         search_query=search_query,
                         status_filter=status_filter,
                         date_range=date_range,
                         filter_active=filter_active,
                         today=today,
                         tomorrow=tomorrow,
                         now=now)

@administrator_bp.route('/register_user', methods=['GET', 'POST'])
@login_required
def register_user():
    if not isinstance(current_user, Administrator):
        return "Access Denied", 403

    form = RegisterUserForm()

    if form.validate_on_submit():
        imie = form.imie.data
        nazwisko = form.nazwisko.data
        email = form.email.data
        telefon = form.telefon.data
        haslo = form.haslo.data
        rola = form.rola.data

        hashed_password = generate_password_hash(haslo)

        if rola == 'lekarz':
            specjalizacja = form.specjalizacja.data
            # Генерируем уникальный номер лицензии
            import random
            while True:
                numer_licencji = 'LIC' + str(random.randint(100000, 999999))
                existing = Lekarz.query.filter_by(numer_licencji=numer_licencji).first()
                if not existing:
                    break
            

            specjalizacja = form.specjalizacja.data if form.specjalizacja.data else 'Medycyna Ogólna'
            user = Lekarz(imie=imie, nazwisko=nazwisko, email=email, telefon=telefon,
                          haslo_hash=hashed_password, specjalizacja=specjalizacja, 
                          numer_licencji=numer_licencji)
        elif rola == 'recepcjonista':
            user = Recepcjonista(imie=imie, nazwisko=nazwisko, email=email, telefon=telefon,
                                 haslo_hash=hashed_password)
        elif rola == 'administrator':
            user = Administrator(imie=imie, nazwisko=nazwisko, email=email, telefon=telefon,
                                 haslo_hash=hashed_password)
        elif rola == 'ordynator':  # DODAĆ TĄ SEKCJĘ
            dzial = form.dzial.data if form.dzial.data else 'Zarządzanie'
            user = Ordynator(imie=imie, nazwisko=nazwisko, email=email, telefon=telefon,
                           haslo_hash=hashed_password, dzial=dzial)
        else:
            flash('Nieznana rola.', 'danger')
            return redirect(url_for('administrator_bp.register_user'))

        try:
            db.session.add(user)
            db.session.commit()
            flash(f'Użytkownik {rola} został zarejestrowany.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Błąd przy zapisie: {str(e)}', 'danger')

        return redirect(url_for('administrator_bp.dashboard'))

    return render_template('administrator/register_user.html', form=form)



@administrator_bp.route('/users')
@login_required
def users():
    if not isinstance(current_user, Administrator):
        return "Access Denied", 403
    
    # Parametry wyszukiwania
    search_query = request.args.get('search', '').strip()
    role_filter = request.args.get('rola', '').strip()
    spec_filter = request.args.get('specjalizacja', '').strip()
    
    # Pobieramy wszystkich użytkowników z różnych tabel
    all_users = []
    
    # Administratorzy
    administrators = Administrator.query.all()
    for admin in administrators:
        all_users.append({
            'id': admin.id,
            'imie': admin.imie,
            'nazwisko': admin.nazwisko,
            'email': admin.email,
            'telefon': admin.telefon,
            'role': 'administrator',
            'specjalizacja': None,
            'numer_licencji': None,
            'pesel': None,
            'data_urodzenia': None
        })

    # Ordynatorzy 
    ordynatorzy = Ordynator.query.all()
    for ordynator in ordynatorzy:
        all_users.append({
            'id': ordynator.id_ordynatora,
            'imie': ordynator.imie,
            'nazwisko': ordynator.nazwisko,
            'email': ordynator.email,
            'telefon': ordynator.telefon,
            'role': 'ordynator',
            'specjalizacja': ordynator.dzial,
            'numer_licencji': None,
            'pesel': None,
            'data_urodzenia': None
        })
    
    # Lekarze
    lekarze = Lekarz.query.all()
    for lekarz in lekarze:
        all_users.append({
            'id': lekarz.id_lekarza,
            'imie': lekarz.imie,
            'nazwisko': lekarz.nazwisko,
            'email': lekarz.email,
            'telefon': lekarz.telefon,
            'role': 'lekarz',
            'specjalizacja': lekarz.specjalizacja,
            'numer_licencji': lekarz.numer_licencji,
            'pesel': None,
            'data_urodzenia': None
        })
    
    # Recepcjoniści
    recepcjonisci = Recepcjonista.query.all()
    for rec in recepcjonisci:
        all_users.append({
            'id': rec.id_recepcjonisty,
            'imie': rec.imie,
            'nazwisko': rec.nazwisko,
            'email': rec.email,
            'telefon': rec.telefon,
            'role': 'recepcjonista',
            'specjalizacja': None,
            'numer_licencji': None,
            'pesel': None,
            'data_urodzenia': None
        })
    
    # Pacjenci
    pacjenci = Pacjent.query.all()
    for pacjent in pacjenci:
        all_users.append({
            'id': pacjent.id_pacjenta,
            'imie': pacjent.imie,
            'nazwisko': pacjent.nazwisko,
            'email': pacjent.email,
            'telefon': pacjent.telefon,
            'role': 'pacjent',
            'specjalizacja': None,
            'numer_licencji': None,
            'pesel': pacjent.pesel,
            'data_urodzenia': pacjent.data_urodzenia
        })
    
    # Filtrowanie
    filtered_users = all_users
    
    # Filtr po roli
    if role_filter:
        filtered_users = [u for u in filtered_users if u['role'] == role_filter]
    
    # Filtr po specjalizacji (tylko lekarze)
    if spec_filter:
        filtered_users = [u for u in filtered_users if u['role'] == 'lekarz' and u['specjalizacja'] == spec_filter]
    
    # Wyszukiwanie po tekście
    if search_query:
        search_lower = search_query.lower()
        filtered_users = [u for u in filtered_users if 
            search_lower in u['imie'].lower() or
            search_lower in u['nazwisko'].lower() or
            search_lower in u['email'].lower() or
            (u['pesel'] and search_lower in u['pesel'])
        ]
    
    # Sortowanie alfabetyczne
    filtered_users.sort(key=lambda x: (x['nazwisko'], x['imie']))
    
    # Statystyki
    total_count = len(all_users)
    doctors_count = len([u for u in all_users if u['role'] == 'lekarz'])
    patients_count = len([u for u in all_users if u['role'] == 'pacjent'])
    staff_count = len([u for u in all_users if u['role'] in ['administrator', 'recepcjonista']])
    administrators_count = len([u for u in all_users if u['role'] == 'administrator'])
    
    # Konwertujemy słowniki na obiekty dla łatwiejszego dostępu w template
    class UserObject:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
    
    user_objects = [UserObject(user) for user in filtered_users]
    
    return render_template('administrator/users.html',
                         users=user_objects,
                         total_count=total_count,
                         doctors_count=doctors_count,
                         patients_count=patients_count,
                         staff_count=staff_count,
                         administrators_count=administrators_count,
                         search_query=search_query,
                         role_filter=role_filter,
                         spec_filter=spec_filter)