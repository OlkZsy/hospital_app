from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.lekarz import Lekarz
from app.models.pacjent import Pacjent
from app.models.wizyta import Wizyta
from app.models.harmonogram import HarmonogramLekarza 
from app.extensions import db
from datetime import datetime

# ИЗМЕНЕНО: Blueprint теперь называется lekarz_bp
lekarz_bp = Blueprint('lekarz_bp', __name__, url_prefix='/lekarz')

def is_lekarz():
    """Проверяет, является ли текущий пользователь врачом"""
    return (hasattr(current_user, 'id_lekarza') or 
            current_user.__class__.__name__ == 'Lekarz' or
            hasattr(current_user, '__tablename__') and current_user.__tablename__ == 'lekarze')

@lekarz_bp.route('/dashboard')
@login_required
def dashboard():
    # Отладочная информация
    print("=== DEBUG INFO ===")
    print(f"current_user: {current_user}")
    print(f"current_user type: {type(current_user)}")
    print(f"current_user.__class__: {current_user.__class__}")
    print(f"current_user.__class__.__name__: {current_user.__class__.__name__}")
    print(f"hasattr id_lekarza: {hasattr(current_user, 'id_lekarza')}")
    if hasattr(current_user, '__tablename__'):
        print(f"tablename: {current_user.__tablename__}")
    print(f"dir(current_user): {[attr for attr in dir(current_user) if not attr.startswith('_')]}")
    print("==================")
    
    if not is_lekarz():
        flash('Brak dostępu. Ta strona jest tylko dla lekarzy.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    return render_template('dashboards/lekarz.html', user=current_user)

@lekarz_bp.route('/wizyty')
@login_required
def wizyty():
    if not is_lekarz():
        flash('Brak dostępu. Ta strona jest tylko dla lekarzy.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    wizyty = Wizyta.query.filter_by(id_lekarza=current_user.id_lekarza).order_by(Wizyta.data_wizyty).all()
    return render_template('lekarz/wizyty.html', wizyty=wizyty)

@lekarz_bp.route('/pacjenci')
@login_required
def pacjenci():
    if not is_lekarz():
        flash('Brak dostępu. Ta strona jest только для lekarzy.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    # Находим всех пациентов, у которых были визиты к этому врачу
    pacjenci_ids = db.session.query(Wizyta.id_pacjenta).filter_by(id_lekarza=current_user.id_lekarza).distinct()
    pacjenci = Pacjent.query.filter(Pacjent.id_pacjenta.in_(pacjenci_ids)).all()
    
    return render_template('lekarz/pacjenci.html', pacjenci=pacjenci)

@lekarz_bp.route('/create_wizyta', methods=['GET', 'POST'])
@login_required
def create_wizyta():
    if not is_lekarz():
        flash('Brak dostępu. Ta strona jest tylko dla lekarzy.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    # Получаем предвыбранного пациента из параметра URL
    preselected_pacjent_id = request.args.get('pacjent', type=int)
    
    if request.method == 'POST':
        id_pacjenta = request.form['id_pacjenta']
        data_wizyty = request.form['data_wizyty']
        notatki = request.form.get('notatki', '')
        
        try:
            # Конвертируем строку в datetime
            data_wizyty_dt = datetime.strptime(data_wizyty, '%Y-%m-%dT%H:%M')
            
            wizyta = Wizyta(
                id_pacjenta=id_pacjenta,
                id_lekarza=current_user.id_lekarza,
                data_wizyty=data_wizyty_dt,
                status='zaplanowana',
                notatki=notatki
            )
            
            db.session.add(wizyta)
            db.session.commit()
            flash('Wizyta została utworzona pomyślnie!', 'success')
            return redirect(url_for('lekarz_bp.wizyty'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Błąd przy tworzeniu wizyty: {str(e)}', 'danger')
    
    # Получаем всех пациентов для выбора
    pacjenci = Pacjent.query.all()
    return render_template('lekarz/create_wizyta.html', 
                         pacjenci=pacjenci, 
                         preselected_pacjent_id=preselected_pacjent_id)

@lekarz_bp.route('/kalendarz')
@login_required
def kalendarz():
    if not is_lekarz():
        flash('Brak dostępu. Ta strona jest только dla lekarzy.', 'danger')
        return redirect(url_for('auth_bp.login'))
    return render_template('partials/calendar_simple.html')

@lekarz_bp.route('/pacjent/<int:id_pacjenta>/leczenie')
@login_required
def pacjent_leczenie(id_pacjenta):
    if not is_lekarz():
        flash('Brak dostępu. Ta strona jest tylko dla lekarzy.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    pacjent = Pacjent.query.get_or_404(id_pacjenta)
    historia = pacjent.historia
    recepty = pacjent.recepty
    
    return render_template('lekarz/pacjent_leczenie.html', 
                         pacjent=pacjent, 
                         historia=historia, 
                         recepty=recepty)



#////////////////////////////////////////////////
from flask import jsonify
from datetime import datetime, timedelta, time

@lekarz_bp.route('/api/my-schedule')
@login_required
def api_my_schedule():
    """API для получения расписания врача с 15-минутными слотами"""
    if not is_lekarz():
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Получаем параметры даты
    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return jsonify({'error': 'Invalid date format'}), 400
    
    # Получаем расписание врача на этот день недели
    weekday_names = {
        0: 'Poniedziałek', 1: 'Wtorek', 2: 'Środa', 3: 'Czwartek',
        4: 'Piątek', 5: 'Sobota', 6: 'Niedziela'
    }
    weekday = weekday_names[target_date.weekday()]
    
    print(f"DEBUG: Looking for schedule on {weekday} for doctor {current_user.id_lekarza}")
    
    harmonogram = HarmonogramLekarza.query.filter_by(
        id_lekarza=current_user.id_lekarza,
        dzien_tygodnia=weekday
    ).first()
    
    if not harmonogram:
        print(f"DEBUG: No schedule found for {weekday}")
        # Проверим, есть ли вообще расписание у врача
        any_schedule = HarmonogramLekarza.query.filter_by(id_lekarza=current_user.id_lekarza).all()
        print(f"DEBUG: Doctor has schedule for: {[s.dzien_tygodnia for s in any_schedule]}")
        
        return jsonify({
            'slots': [], 
            'message': f'Brak harmonogramu na {weekday}',
            'available_days': [s.dzien_tygodnia for s in any_schedule]
        })
    
    print(f"DEBUG: Found schedule: {harmonogram.godzina_start} - {harmonogram.godzina_koniec}")
    
    # Получаем занятые слоты на эту дату
    wizyty = Wizyta.query.filter(
        Wizyta.id_lekarza == current_user.id_lekarza,
        db.func.date(Wizyta.data_wizyty) == target_date,
        Wizyta.status != 'anulowana'
    ).all()
    
    print(f"DEBUG: Found {len(wizyty)} appointments on this date")
    
    occupied_slots = []
    for wizyta in wizyty:
        occupied_slots.append({
            'start': wizyta.data_wizyty.strftime('%H:%M'),
            'end': (wizyta.data_wizyty + timedelta(minutes=15)).strftime('%H:%M'),
            'patient': f"{wizyta.pacjent.imie} {wizyta.pacjent.nazwisko}",
            'id': wizyta.id_wizyty
        })
    
    # Генерируем все возможные 15-минутные слоты
    slots = []
    current_time = datetime.combine(target_date, harmonogram.godzina_start)
    end_time = datetime.combine(target_date, harmonogram.godzina_koniec)
    
    while current_time < end_time:
        slot_end = current_time + timedelta(minutes=15)
        if slot_end <= end_time:
            time_str = current_time.strftime('%H:%M')
            
            # Проверяем, занят ли слот
            is_occupied = any(
                slot['start'] == time_str for slot in occupied_slots
            )
            
            slot_data = {
                'time': time_str,
                'datetime': current_time.isoformat(),
                'available': not is_occupied
            }
            
            if is_occupied:
                occupied_slot = next(s for s in occupied_slots if s['start'] == time_str)
                slot_data.update({
                    'patient': occupied_slot['patient'],
                    'appointment_id': occupied_slot['id']
                })
            
            slots.append(slot_data)
        
        current_time += timedelta(minutes=15)
    
    print(f"DEBUG: Generated {len(slots)} slots")
    
    return jsonify({
        'date': date_str,
        'weekday': weekday,
        'doctor': f"{current_user.imie} {current_user.nazwisko}",
        'slots': slots
    })

@lekarz_bp.route('/api/book-slot', methods=['POST'])
@login_required
def api_book_slot():
    """API для бронирования слота (для пациентов)"""
    data = request.get_json()
    
    try:
        slot_datetime = datetime.fromisoformat(data['datetime'])
        id_pacjenta = data['patient_id']
        id_lekarza = data['doctor_id']
        
        # Проверяем, свободен ли слот
        existing = Wizyta.query.filter(
            Wizyta.id_lekarza == id_lekarza,
            Wizyta.data_wizyty == slot_datetime,
            Wizyta.status != 'anulowana'
        ).first()
        
        if existing:
            return jsonify({'error': 'Slot already booked'}), 400
        
        # Создаем новую визиту
        wizyta = Wizyta(
            id_pacjenta=id_pacjenta,
            id_lekarza=id_lekarza,
            data_wizyty=slot_datetime,
            status='zaplanowana',
            notatki=data.get('notes', '')
        )
        
        db.session.add(wizyta)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'appointment_id': wizyta.id_wizyty
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500




# Добавить в конец файла app/routes/lekarz.py:

@lekarz_bp.route('/api/patients')
@login_required
def api_patients():
    """API для получения списка всех пациентов"""
    if not is_lekarz():
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        patients = Pacjent.query.all()
        patients_data = []
        
        for patient in patients:
            patients_data.append({
                'id': patient.id_pacjenta,
                'name': f"{patient.imie} {patient.nazwisko}",
                'email': patient.email,
                'phone': patient.telefon or '',
                'pesel': patient.pesel or ''
            })
        
        return jsonify(patients_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500