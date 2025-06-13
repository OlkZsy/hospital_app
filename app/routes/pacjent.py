from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.wizyta import Wizyta
from app.models.pacjent import Pacjent
from app.models.lekarz import Lekarz
from app.models.historia import HistoriaMedyczna
from app.models.recepta import Recepta
from app.models.harmonogram import HarmonogramLekarza
from app.extensions import db
from datetime import datetime, date, timedelta

pacjent_bp = Blueprint('pacjent_bp', __name__, url_prefix='/pacjent')

def is_pacjent():
    """Проверяет, является ли текущий пользователь пациентом"""
    return (hasattr(current_user, 'id_pacjenta') or 
            current_user.__class__.__name__ == 'Pacjent' or
            hasattr(current_user, '__tablename__') and current_user.__tablename__ == 'pacjenci')

@pacjent_bp.route('/dashboard')
@login_required
def dashboard():
    if not is_pacjent():
        flash('Brak dostępu. Ta strona jest tylko dla pacjentów.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    return render_template('dashboards/pacjent.html', user=current_user)

@pacjent_bp.route('/wizyty')
@login_required
def wizyty():
    if not is_pacjent():
        flash('Brak dostępu. Ta strona jest tylko dla pacjentów.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    wizyty = Wizyta.query.filter_by(
        id_pacjenta=current_user.id_pacjenta
    ).order_by(Wizyta.data_wizyty.desc()).all()
    
    #Dodajemy obliczenia dni dla każdej wizyty
    from datetime import datetime, date
    today = date.today()
    now = datetime.now()
    
    for wizyta in wizyty:
        wizyta.days_diff = (wizyta.data_wizyty.date() - today).days
        wizyta.hours_diff = (wizyta.data_wizyty - now).total_seconds() / 3600
    
    return render_template('pacjent/wizyty.html', wizyty=wizyty)
    
    

@pacjent_bp.route('/kalendarz')
def kalendarz():
    if not is_pacjent():
        flash('Brak dostępu. Ta strona jest tylko dla pacjentów.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    return render_template('pacjent/kalendarz.html')

@pacjent_bp.route('/zapisz-sie')
@login_required
def zapisz_sie():
    """Страница записи к врачу"""
    if not is_pacjent():
        flash('Brak dostępu. Ta strona jest tylko dla pacjentów.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    #Получаем всех врачей
    lekarze = Lekarz.query.all()
    
    return render_template('pacjent/zapisz_sie.html', lekarze=lekarze)

@pacjent_bp.route('/api/doctor-schedule/<int:doctor_id>')
@login_required
def api_doctor_schedule(doctor_id):
    """API расписания врача для пациента (без имен других пациентов)"""
    if not is_pacjent():
        return jsonify({'error': 'Unauthorized'}), 403
    
    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return jsonify({'error': 'Invalid date format'}), 400
    
    #Получаем расписание врача
    weekday_names = {
        0: 'Poniedziałek', 1: 'Wtorek', 2: 'Środa', 3: 'Czwartek',
        4: 'Piątek', 5: 'Sobota', 6: 'Niedziela'
    }
    weekday = weekday_names[target_date.weekday()]
    
    harmonogram = HarmonogramLekarza.query.filter_by(
        id_lekarza=doctor_id,
        dzien_tygodnia=weekday
    ).first()
    
    if not harmonogram:
        return jsonify({
            'slots': [],
            'message': f'Lekarz nie pracuje w {weekday}',
            'available_days': []
        })
    
    #Получаем занятые слоты
    wizyty = Wizyta.query.filter(
        Wizyta.id_lekarza == doctor_id,
        db.func.date(Wizyta.data_wizyty) == target_date,
        Wizyta.status.in_(['zaplanowana', 'oczekujaca'])
    ).all()
    
    occupied_slots = []
    patient_slots = []  #Слоты этого пациента
    
    for wizyta in wizyty:
        slot_info = {
            'start': wizyta.data_wizyty.strftime('%H:%M'),
            'end': (wizyta.data_wizyty + timedelta(minutes=15)).strftime('%H:%M'),
            'id': wizyta.id_wizyty
        }
        
        if wizyta.id_pacjenta == current_user.id_pacjenta:
            patient_slots.append(slot_info)
        else:
            occupied_slots.append(slot_info)
    
    # Генерируем слоты
    slots = []
    current_time = datetime.combine(target_date, harmonogram.godzina_start)
    end_time = datetime.combine(target_date, harmonogram.godzina_koniec)
    
    while current_time < end_time:
        slot_end = current_time + timedelta(minutes=15)
        if slot_end <= end_time:
            time_str = current_time.strftime('%H:%M')
            
            # Проверяем статус слота
            is_patient_slot = any(slot['start'] == time_str for slot in patient_slots)
            is_occupied = any(slot['start'] == time_str for slot in occupied_slots)
            
            slot_data = {
                'time': time_str,
                'datetime': current_time.isoformat(),
                'available': not (is_occupied or is_patient_slot),
                'is_mine': is_patient_slot,
                'status': 'mine' if is_patient_slot else ('occupied' if is_occupied else 'available')
            }
            
            if is_patient_slot:
                patient_slot = next(s for s in patient_slots if s['start'] == time_str)
                slot_data['appointment_id'] = patient_slot['id']
            
            slots.append(slot_data)
        
        current_time += timedelta(minutes=15)
    
    return jsonify({
        'date': date_str,
        'weekday': weekday,
        'doctor': f"{Lekarz.query.get(doctor_id).imie} {Lekarz.query.get(doctor_id).nazwisko}",
        'slots': slots
    })

@pacjent_bp.route('/api/book-appointment', methods=['POST'])
@login_required
def api_book_appointment():
    #API записи пациента к врачу
    if not is_pacjent():
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    try:
        slot_datetime = datetime.fromisoformat(data['datetime'])
        doctor_id = data['doctor_id']
        notes = data.get('notes', '')
        
        #Проверяем, не занят ли слот
        existing = Wizyta.query.filter(
            Wizyta.id_lekarza == doctor_id,
            Wizyta.data_wizyty == slot_datetime,
            Wizyta.status.in_(['zaplanowana', 'oczekujaca'])
        ).first()
        
        if existing:
            return jsonify({'error': 'Ten termin jest już zajęty'}), 400
        
        #Проверяем, не записан ли пациент на то же время к другому врачу
        patient_conflict = Wizyta.query.filter(
            Wizyta.id_pacjenta == current_user.id_pacjenta,
            Wizyta.data_wizyty == slot_datetime,
            Wizyta.status.in_(['zaplanowana', 'oczekujaca'])
        ).first()
        
        if patient_conflict:
            return jsonify({'error': 'Masz już wizytę o tej godzinie'}), 400
        
        #Создаем визиту
        wizyta = Wizyta(
            id_pacjenta=current_user.id_pacjenta,
            id_lekarza=doctor_id,
            data_wizyty=slot_datetime,
            status='zaplanowana',
            notatki=f"Zapisany przez pacjenta. {notes}" if notes else "Zapisany przez pacjenta."
        )
        
        db.session.add(wizyta)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'appointment_id': wizyta.id_wizyty,
            'message': 'Pomyślnie zapisano na wizytę!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@pacjent_bp.route('/api/cancel-appointment/<int:appointment_id>', methods=['POST'])
@login_required
def api_cancel_appointment(appointment_id):
    #API anulowania wizyty przez pacjenta
    if not is_pacjent():
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        wizyta = Wizyta.query.get_or_404(appointment_id)
        
        # Sprawdź czy to wizyta tego pacjenta
        if wizyta.id_pacjenta != current_user.id_pacjenta:
            return jsonify({'error': 'Nie masz uprawnień do tej wizyty'}), 403
        
        # Sprawdź czy wizyta nie była już za późno na anulowanie (np. mniej niż 2 godziny)
        if wizyta.data_wizyty <= datetime.now() + timedelta(hours=2):
            return jsonify({'error': 'Nie można anulować wizyty na mniej niż 2 godziny przed terminem'}), 400
        
        wizyta.status = 'anulowana'
        wizyta.notatki = (wizyta.notatki or '') + f" [Anulowana przez pacjenta {datetime.now().strftime('%d.%m.%Y %H:%M')}]"
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Wizyta została anulowana'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@pacjent_bp.route('/api/my-calendar')
@login_required
def api_my_calendar():
    #API kalendarza pacjenta - tylko jego wizyty
    if not is_pacjent():
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Получаем параметры даты для месяца
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    # Получаем все визиты пациента в этом месяце
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    wizyty = Wizyta.query.filter(
        Wizyta.id_pacjenta == current_user.id_pacjenta,
        Wizyta.data_wizyty >= start_date,
        Wizyta.data_wizyty < end_date,
        Wizyta.status != 'anulowana'
    ).all()
    
    # Группируем по дням
    appointments_by_day = {}
    for wizyta in wizyty:
        day_str = wizyta.data_wizyty.strftime('%Y-%m-%d')
        if day_str not in appointments_by_day:
            appointments_by_day[day_str] = []
        
        appointments_by_day[day_str].append({
            'id': wizyta.id_wizyty,
            'time': wizyta.data_wizyty.strftime('%H:%M'),
            'doctor': f"Dr {wizyta.lekarz.imie} {wizyta.lekarz.nazwisko}",
            'status': wizyta.status,
            'notes': wizyta.notatki
        })
    
    return jsonify(appointments_by_day)

        #  o|_|o
        #  o|x|_
        #  x|x|x

@pacjent_bp.route('/leczenie')
@login_required
def view_treatment():
    if not is_pacjent():
        flash('Brak dostępu. Ta strona jest tylko dla pacjentów.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    return render_template('pacjent/view_treatment.html', user=current_user)

@pacjent_bp.route('/api/my-historia')
@login_required
def api_my_historia():
    #API для получения истории медицинской пациента
    if not is_pacjent():
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        historia = HistoriaMedyczna.query.filter_by(
            id_pacjenta=current_user.id_pacjenta
        ).order_by(HistoriaMedyczna.data_wpisu.desc()).all()
        
        historia_data = []
        for wpis in historia:
            historia_data.append({
                'data_wpisu': wpis.data_wpisu.strftime('%d.%m.%Y'),
                'lekarz': f"{wpis.lekarz.imie} {wpis.lekarz.nazwisko}",
                'diagnoza': wpis.diagnoza,
                'notatki': wpis.notatki
            })
        
        return jsonify(historia_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pacjent_bp.route('/api/my-recepty')
@login_required
def api_my_recepty():
    #API dla получения рецептов пациента
    if not is_pacjent():
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        recepty = Recepta.query.filter_by(
            id_pacjenta=current_user.id_pacjenta
        ).order_by(Recepta.data_wystawienia.desc()).all()
        
        recepty_data = []
        for recepta in recepty:
            recepty_data.append({
                'id_recepty': recepta.id_recepty,
                'data_wystawienia': recepta.data_wystawienia.strftime('%d.%m.%Y'),
                'leki': recepta.leki,
                'instrukcje': recepta.instrukcje,
                'lekarz': f"{recepta.lekarz.imie} {recepta.lekarz.nazwisko}"
            })
        
        return jsonify(recepty_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pacjent_bp.route('/api/my-wizyty')
@login_required
def api_my_wizyty():
    #API для получения визит пациента
    if not is_pacjent():
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        wizyty = Wizyta.query.filter_by(
            id_pacjenta=current_user.id_pacjenta
        ).order_by(Wizyta.data_wizyty.desc()).all()
        
        wizyty_data = []
        for wizyta in wizyty:
            wizyty_data.append({
                'id_wizyty': wizyta.id_wizyty,
                'data_wizyty': wizyta.data_wizyty.strftime('%d.%m.%Y %H:%M'),
                'lekarz': f"{wizyta.lekarz.imie} {wizyta.lekarz.nazwisko}",
                'status': wizyta.status,
                'notatki': wizyta.notatki
            })
        
        return jsonify(wizyty_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@pacjent_bp.route('/profil', methods=['GET', 'POST'])
@login_required
def profil():
    if not is_pacjent():
        flash('Brak dostępu. Ta strona jest tylko dla pacjentów.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    if request.method == 'POST':
        try:
            # Aktualizujemy tylko adres i telefon
            current_user.adres = request.form.get('adres', current_user.adres)
            current_user.telefon = request.form.get('telefon', current_user.telefon)
            
            db.session.commit()
            flash('Profil został zaktualizowany pomyślnie!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Błąd przy aktualizacji profilu: {str(e)}', 'danger')
        
        return redirect(url_for('pacjent_bp.profil'))
    
    return render_template('pacjent/profil.html', user=current_user)
