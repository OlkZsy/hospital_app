from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_required, current_user
from app.models.ordynator import Ordynator
from app.models.administrator import Administrator
from app.models.lekarz import Lekarz
from app.models.recepcjonista import Recepcjonista
from app.models.pacjent import Pacjent
from app.models.wizyta import Wizyta
from app.extensions import db
from datetime import datetime, date, timedelta
import csv
import io


ordynator_bp = Blueprint('ordynator_bp', __name__, url_prefix='/ordynator')

def is_ordynator():
    """Sprawdza czy użytkownik jest ordynatorem"""
    return isinstance(current_user, Ordynator)

@ordynator_bp.route('/dashboard')
@login_required
def dashboard():
    if not is_ordynator():
        flash('Brak dostępu. Ta strona jest tylko dla ordynatorów.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    total_users = (Administrator.query.count() + Lekarz.query.count() + 
                   Recepcjonista.query.count() + Ordynator.query.count() + 
                   Pacjent.query.count())
    total_doctors = Lekarz.query.count()
    total_visits = Wizyta.query.count()
    total_patients = Pacjent.query.count()
    
    today = date.today()
    today_visits = Wizyta.query.filter(db.func.date(Wizyta.data_wizyty) == today).count()



    recent_activities = Wizyta.query.join(Pacjent).join(Lekarz)\
        .order_by(Wizyta.data_wizyty.desc())\
        .limit(5)\
        .all()

    return render_template('dashboards/ordynator.html', 
                         user=current_user,
                         total_users=total_users,
                         total_doctors=total_doctors,
                         total_visits=total_visits,
                         total_patients=total_patients,
                         today_visits=today_visits,
                         recent_activities=recent_activities)
    
    #return render_template('dashboards/ordynator.html', user=current_user)

@ordynator_bp.route('/users')
@login_required
def users():
    if not is_ordynator():
        flash('Brak dostępu. Ta strona jest tylko dla ordynatorów.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    # Parametry wyszukiwania
    search_query = request.args.get('search', '').strip()
    role_filter = request.args.get('rola', '').strip()
    
    #wszystkich użytkowników
    all_users = []
    
    # administratorzy 
    administrators = Administrator.query.all()
    for admin in administrators:
        all_users.append({
            'id': admin.id,
            'imie': admin.imie,
            'nazwisko': admin.nazwisko,
            'email': admin.email,
            'telefon': '***',  # Ukryte
            'role': 'administrator',
            'specjalizacja': None,
            'status': 'Aktywny'
        })
    
    # lekarze 
    lekarze = Lekarz.query.all()
    for lekarz in lekarze:
        all_users.append({
            'id': lekarz.id_lekarza,
            'imie': lekarz.imie,
            'nazwisko': lekarz.nazwisko,
            'email': lekarz.email,
            'telefon': '***',  # Ukryte
            'role': 'lekarz',
            'specjalizacja': lekarz.specjalizacja,
            'status': 'Aktywny'
        })
    
    # recepcjoniści
    recepcjonisci = Recepcjonista.query.all()
    for rec in recepcjonisci:
        all_users.append({
            'id': rec.id_recepcjonisty,
            'imie': rec.imie,
            'nazwisko': rec.nazwisko,
            'email': rec.email,
            'telefon': '***',  # Ukryte
            'role': 'recepcjonista',
            'specjalizacja': None,
            'status': 'Aktywny'
        })
    
    # ordynatorzy
    ordynatorzy = Ordynator.query.all()
    for ord in ordynatorzy:
        all_users.append({
            'id': ord.id_ordynatora,
            'imie': ord.imie,
            'nazwisko': ord.nazwisko,
            'email': ord.email,
            'telefon': '***',  # Ukryte
            'role': 'ordynator',
            'specjalizacja': ord.dzial,
            'status': 'Aktywny'
        })
    
    # pacjenci 
    pacjenci = Pacjent.query.all()
    for pacjent in pacjenci:
        all_users.append({
            'id': pacjent.id_pacjenta,
            'imie': pacjent.imie,
            'nazwisko': pacjent.nazwisko,
            'email': pacjent.email,
            'telefon': '***',  # Ukryte
            'role': 'pacjent',
            'specjalizacja': None,
            'status': 'Aktywny'
        })
    
    # filtrowanie
    filtered_users = all_users
    
    if role_filter:
        filtered_users = [u for u in filtered_users if u['role'] == role_filter]
    
    if search_query:
        search_lower = search_query.lower()
        filtered_users = [u for u in filtered_users if 
            search_lower in u['imie'].lower() or
            search_lower in u['nazwisko'].lower() or
            search_lower in u['email'].lower()
        ]
    
    # sortowanie
    filtered_users.sort(key=lambda x: (x['nazwisko'], x['imie']))
    
    # statystyki
    total_count = len(all_users)
    doctors_count = len([u for u in all_users if u['role'] == 'lekarz'])
    patients_count = len([u for u in all_users if u['role'] == 'pacjent'])
    staff_count = len([u for u in all_users if u['role'] in ['administrator', 'recepcjonista', 'ordynator']])
    
    return render_template('ordynator/users.html',
                         users=filtered_users,
                         total_count=total_count,
                         doctors_count=doctors_count,
                         patients_count=patients_count,
                         staff_count=staff_count,
                         search_query=search_query,
                         role_filter=role_filter)

@ordynator_bp.route('/wizyty')
@login_required
def wizyty():
    if not is_ordynator():
        flash('Brak dostępu. Ta strona jest tylko dla ordynatorów.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    # parametry filtrowania 
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()
    doctor_filter = request.args.get('doctor', '').strip()
    export_format = request.args.get('export', '').strip()
    
    # bazowe zapytanie
    query = Wizyta.query.join(Pacjent).join(Lekarz)
    
    # filtrowanie 
    if search_query:
        search_filter = db.or_(
            Pacjent.imie.ilike(f'%{search_query}%'),
            Pacjent.nazwisko.ilike(f'%{search_query}%'),
            Lekarz.imie.ilike(f'%{search_query}%'),
            Lekarz.nazwisko.ilike(f'%{search_query}%')
        )
        query = query.filter(search_filter)
    
    if status_filter:
        query = query.filter(Wizyta.status == status_filter)
    
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
    
    if doctor_filter:
        try:
            doctor_id = int(doctor_filter)
            query = query.filter(Wizyta.id_lekarza == doctor_id)
        except ValueError:
            pass
    
    # pobierz wyniki
    wizyty = query.order_by(Wizyta.data_wizyty.desc()).all()
    
    # eksport do CSV
    if export_format == 'csv':
        return export_visits_csv(wizyty)
    
    # Statystyki
    all_visits = Wizyta.query.all()
    total_visits = len(all_visits)
    planned_visits = len([w for w in all_visits if w.status == 'zaplanowana'])
    completed_visits = len([w for w in all_visits if w.status == 'zakonczona'])
    cancelled_visits = len([w for w in all_visits if w.status == 'anulowana'])
    
   
    doctors = Lekarz.query.order_by(Lekarz.nazwisko).all()
    
   
    today = date.today()
    tomorrow = today + timedelta(days=1)
    now = datetime.now()
    
    filter_active = bool(search_query or status_filter or date_from or date_to or doctor_filter)
    
    return render_template('ordynator/wizyty.html',
                         wizyty=wizyty,
                         total_visits=total_visits,
                         planned_visits=planned_visits,
                         completed_visits=completed_visits,
                         cancelled_visits=cancelled_visits,
                         doctors=doctors,
                         search_query=search_query,
                         status_filter=status_filter,
                         filter_active=filter_active,
                         today=today,
                         tomorrow=tomorrow,
                         now=now)

def export_visits_csv(wizyty):
    """Eksportuje wizyty do pliku CSV"""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    
    # nagłówki
    writer.writerow([
        'Data i godzina',
        'Pacjent',
        'Lekarz',
        'Status',
        'Notatki',
        'Utworzona przez'
    ])
    
    # dane
    for wizyta in wizyty:
        utworzona_przez = ''
        if wizyta.autor:
            utworzona_przez = f"{wizyta.autor.imie} {wizyta.autor.nazwisko} (Recepcjonista)"
        else:
            utworzona_przez = "System/Pacjent"
        
        writer.writerow([
            wizyta.data_wizyty.strftime('%d.%m.%Y %H:%M'),
            f"{wizyta.pacjent.imie} {wizyta.pacjent.nazwisko}",
            f"Dr {wizyta.lekarz.imie} {wizyta.lekarz.nazwisko}",
            wizyta.status,
            wizyta.notatki or '',
            utworzona_przez
        ])
    
    output.seek(0)
    
    # tworzenie odpowiedzi plikiem CSV
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=wizyty_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response