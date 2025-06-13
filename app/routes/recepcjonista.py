from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.models.recepcjonista import Recepcjonista
from app.models.pacjent import Pacjent
from app.models.lekarz import Lekarz
from app.models.wizyta import Wizyta
from app.models.recepta import Recepta
from app.models.harmonogram import HarmonogramLekarza
from app.extensions import db
from datetime import datetime, date, timedelta




def auto_complete_past_visits():
    #автоматически завершает прошедшие визиты
    try:
        cutoff_time = datetime.now() - timedelta(minutes=30)
        
        past_visits = Wizyta.query.filter(
            Wizyta.status == 'zaplanowana',
            Wizyta.data_wizyty < cutoff_time
        ).all()
        
        completed_count = 0
        for wizyta in past_visits:
            wizyta.status = 'zakonczona'
            if not wizyta.notatki:
                wizyta.notatki = "Automatycznie zakończona"
            else:
                wizyta.notatki += " [Auto-zakończona]"
            completed_count += 1
        
        if completed_count > 0:
            db.session.commit()
        
        return completed_count
        
    except Exception as e:
        db.session.rollback()
        return 0






recepcjonista_bp = Blueprint('recepcjonista_bp', __name__, url_prefix='/recepcjonista')

def is_recepcjonista():
    #проверяет, является ли текущий пользователь рецепционистом
    try:
        return isinstance(current_user, Recepcjonista)
    except:
        return False

@recepcjonista_bp.route('/dashboard')
@login_required
def dashboard():
    if not is_recepcjonista():
        flash('Brak dostępu. Ta strona jest tylko dla recepcjonistów.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    return render_template('dashboards/recepcjonista.html', user=current_user)

@recepcjonista_bp.route('/pacjenci')
@login_required
def pacjenci():
    if not is_recepcjonista():
        flash('Brak dostępu. Ta strona jest tylko dla recepcjonistów.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    search = request.args.get('search', '')
    if search:
        pacjenci = Pacjent.query.filter(
            (Pacjent.nazwisko.ilike(f'%{search}%')) |
            (Pacjent.imie.ilike(f'%{search}%')) |
            (Pacjent.pesel.ilike(f'%{search}%'))
        ).all()
    else:
        pacjenci = Pacjent.query.all()
    
    return render_template('recepcjonista/pacjenci.html', pacjenci=pacjenci, search=search)

@recepcjonista_bp.route('/pacjent/<int:id_pacjenta>')
@login_required
def pacjent_details(id_pacjenta):
    if not is_recepcjonista():
        flash('Brak dostępu. Ta strona jest tylko dla recepcjonistów.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    pacjent = Pacjent.query.get_or_404(id_pacjenta)
    
    # рецепты без диагноза
    recepty = Recepta.query.filter_by(id_pacjenta=id_pacjenta).order_by(Recepta.data_wystawienia.desc()).all()
    wizyty = Wizyta.query.filter_by(id_pacjenta=id_pacjenta).order_by(Wizyta.data_wizyty.desc()).all()
    
    return render_template('recepcjonista/pacjent_details.html', 
                         pacjent=pacjent, recepty=recepty, wizyty=wizyty)

@recepcjonista_bp.route('/pacjent/<int:id_pacjenta>/edit', methods=['GET', 'POST'])
@login_required
def edit_pacjent(id_pacjenta):
    if not is_recepcjonista():
        flash('Brak dostępu. Ta strona jest tylko dla recepcjonistów.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    pacjent = Pacjent.query.get_or_404(id_pacjenta)
    
    if request.method == 'POST':
        try:
            pacjent.telefon = request.form.get('telefon')
            pacjent.adres = request.form.get('adres')
            pacjent.email = request.form.get('email')
            
            db.session.commit()
            flash('Dane pacjenta zostały zaktualizowane.', 'success')
            return redirect(url_for('recepcjonista_bp.pacjent_details', id_pacjenta=id_pacjenta))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Błąd przy aktualizacji: {str(e)}', 'danger')
    
    return render_template('recepcjonista/edit_pacjent.html', pacjent=pacjent)

@recepcjonista_bp.route('/register_pacjent', methods=['GET', 'POST'])
@login_required
def register_pacjent():
    if not is_recepcjonista():
        flash('Brak dostępu. Ta strona jest tylko dla recepcjonistów.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    if request.method == 'POST':
        try:
            new_pacjent = Pacjent(
                imie=request.form['imie'],
                nazwisko=request.form['nazwisko'],
                email=request.form['email'],
                telefon=request.form['telefon'],
                adres=request.form['adres'],
                data_urodzenia=datetime.strptime(request.form['data_urodzenia'], '%Y-%m-%d').date(),
                pesel=request.form['pesel'],
                haslo_hash=generate_password_hash(request.form['haslo'])
            )
            
            db.session.add(new_pacjent)
            db.session.commit()
            flash('Pacjent został zarejestrowany pomyślnie!', 'success')
            return redirect(url_for('recepcjonista_bp.pacjenci'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Błąd przy rejestracji: {str(e)}', 'danger')
    
    return render_template('recepcjonista/register_pacjent.html')

@recepcjonista_bp.route('/lekarze')
@login_required
def lekarze():
    if not is_recepcjonista():
        flash('Brak dostępu. Ta strona jest tylko dla recepcjonistów.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    lekarze = Lekarz.query.all()
    return render_template('recepcjonista/lekarze.html', lekarze=lekarze)

@recepcjonista_bp.route('/lekarz/<int:id_lekarza>/kalendarz')
@login_required
def lekarz_kalendarz(id_lekarza):
    if not is_recepcjonista():
        flash('Brak dostępu. Ta strona jest tylko dla recepcjonistów.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    lekarz = Lekarz.query.get_or_404(id_lekarza)
    return render_template('recepcjonista/lekarz_kalendarz.html', lekarz=lekarz)

#///////////////////////////////////// DZISIEJSZE WIZYTY | ZAPISZ PACJENTA /////////////////////////////////

@recepcjonista_bp.route('/dzisiejsze-wizyty')
@login_required
def dzisiejsze_wizyty():
    if not is_recepcjonista():
        flash('Brak dostępu. Ta strona jest tylko dla recepcjonistów.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    # Автоматически завершаем прошедшие визиты
    completed = auto_complete_past_visits()
    if completed > 0:
        flash(f'Automatycznie zakończono {completed} przeszłych wizyt', 'info')
    
    # Получаем все визиты на сегодня
    today = date.today()
    wizyty = Wizyta.query.filter(
        db.func.date(Wizyta.data_wizyty) == today
    ).order_by(Wizyta.data_wizyty).all()
    
    return render_template('recepcjonista/dzisiejsze_wizyty.html', wizyty=wizyty, today=today)

@recepcjonista_bp.route('/zapisz-pacjenta', methods=['GET', 'POST'])
@login_required
def zapisz_pacjenta():
    """Запись пациента к врачу рецепционистом"""
    if not is_recepcjonista():
        flash('Brak dostępu. Ta strona jest tylko dla recepcjonistów.', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    if request.method == 'POST':
        try:
            id_pacjenta = request.form['id_pacjenta']
            id_lekarza = request.form['id_lekarza']
            data_wizyty = request.form['data_wizyty']
            notatki = request.form.get('notatki', '')
            
            # Конвертируем строку в datetime
            data_wizyty_dt = datetime.strptime(data_wizyty, '%Y-%m-%dT%H:%M')
            
            # Проверяем, не занят ли слот
            existing = Wizyta.query.filter(
                Wizyta.id_lekarza == id_lekarza,
                Wizyta.data_wizyty == data_wizyty_dt,
                Wizyta.status.in_(['zaplanowana', 'oczekujaca'])
            ).first()
            
            if existing:
                flash('Ten termin jest już zajęty!', 'danger')
                return redirect(url_for('recepcjonista_bp.zapisz_pacjenta'))
            
            # Создаем визиту
            wizyta = Wizyta(
                id_pacjenta=id_pacjenta,
                id_lekarza=id_lekarza,
                data_wizyty=data_wizyty_dt,
                status='zaplanowana',
                notatki=f"Zapisany przez recepcjonistę. {notatki}" if notatki else "Zapisany przez recepcjonistę.",
                utworzona_przez=current_user.id_recepcjonisty
            )
            
            db.session.add(wizyta)
            db.session.commit()
            flash('Pacjent został zapisany na wizytę!', 'success')
            return redirect(url_for('recepcjonista_bp.dzisiejsze_wizyty'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Błąd przy zapisywaniu wizyty: {str(e)}', 'danger')
    
    # Получаем всех пациентов и врачей для выбора
    pacjenci = Pacjent.query.all()
    lekarze = Lekarz.query.all()
    
    return render_template('recepcjonista/zapisz_pacjenta.html', 
                         pacjenci=pacjenci, lekarze=lekarze)

#API ENDPOINTS

@recepcjonista_bp.route('/api/lekarz/<int:id_lekarza>/schedule')
@login_required
def api_lekarz_schedule(id_lekarza):
    if not is_recepcjonista():
        return jsonify({'error': 'Unauthorized'}), 403
    
    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return jsonify({'error': 'Invalid date format'}), 400
    
    weekday_names = {
        0: 'Poniedziałek', 1: 'Wtorek', 2: 'Środa', 3: 'Czwartek',
        4: 'Piątek', 5: 'Sobota', 6: 'Niedziela'
    }
    weekday = weekday_names[target_date.weekday()]
    
    harmonogram = HarmonogramLekarza.query.filter_by(
        id_lekarza=id_lekarza,
        dzien_tygodnia=weekday
    ).first()
    
    if not harmonogram:
        return jsonify({'slots': [], 'message': f'Brak harmonogramu na {weekday}'})
    
    #Получаем занятые слоты
    wizyty = Wizyta.query.filter(
        Wizyta.id_lekarza == id_lekarza,
        db.func.date(Wizyta.data_wizyty) == target_date,
        Wizyta.status != 'anulowana'
    ).all()
    
    occupied_slots = []
    for wizyta in wizyty:
        occupied_slots.append({
            'start': wizyta.data_wizyty.strftime('%H:%M'),
            'patient': f"{wizyta.pacjent.imie} {wizyta.pacjent.nazwisko}",
            'id': wizyta.id_wizyty
        })
    
    #Геерируем слоты
    slots = []
    current_time = datetime.combine(target_date, harmonogram.godzina_start)
    end_time = datetime.combine(target_date, harmonogram.godzina_koniec)
    
    while current_time < end_time:
        slot_end = current_time + timedelta(minutes=15)
        if slot_end <= end_time:
            time_str = current_time.strftime('%H:%M')
            
            is_occupied = any(slot['start'] == time_str for slot in occupied_slots)
            
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
    
    return jsonify({
        'date': date_str,
        'weekday': weekday,
        'doctor': f"{Lekarz.query.get(id_lekarza).imie} {Lekarz.query.get(id_lekarza).nazwisko}",
        'slots': slots
    })

@recepcjonista_bp.route('/api/book-appointment', methods=['POST'])
@login_required
def api_book_appointment():
    #API записи пациента к врачу рецепционистом
    if not is_recepcjonista():
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    try:
        slot_datetime = datetime.fromisoformat(data['datetime'])
        doctor_id = data['doctor_id']
        patient_id = data['patient_id']
        notes = data.get('notes', '')
        
        #Проверяем, не занят ли слот
        existing = Wizyta.query.filter(
            Wizyta.id_lekarza == doctor_id,
            Wizyta.data_wizyty == slot_datetime,
            Wizyta.status.in_(['zaplanowana', 'oczekujaca'])
        ).first()
        
        if existing:
            return jsonify({'error': 'Ten termin jest już zajęty'}), 400
        
        #Создаем визиту
        wizyta = Wizyta(
            id_pacjenta=patient_id,
            id_lekarza=doctor_id,
            data_wizyty=slot_datetime,
            status='zaplanowana',
            notatki=f"Zapisany przez recepcjonistę. {notes}" if notes else "Zapisany przez recepcjonistę.",
            utworzona_przez=current_user.id_recepcjonisty
        )
        
        db.session.add(wizyta)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'appointment_id': wizyta.id_wizyty,
            'message': 'Pacjent został zapisany na wizytę!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500