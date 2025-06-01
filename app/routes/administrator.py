from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.forms import RegisterUserForm
from app.models.lekarz import Lekarz
from app.models.recepcjonista import Recepcjonista
from app.models.administrator import Administrator
from app.models.wizyta import Wizyta
from app.extensions import db

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
    wizyty = Wizyta.query.order_by(Wizyta.data_wizyty).all()
    return render_template('administrator/wizyty.html', wizyty=wizyty)

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
            user = Lekarz(imie=imie, nazwisko=nazwisko, email=email, telefon=telefon, haslo_hash=hashed_password, specjalizacja='Ogólna', numer_licencji='LIC' + email[:5])
        elif rola == 'recepcjonista':
            user = Recepcjonista(imie=imie, nazwisko=nazwisko, email=email, telefon=telefon, haslo_hash=hashed_password)
        elif rola == 'administrator':
            user = Administrator(imie=imie, nazwisko=nazwisko, email=email, telefon=telefon, haslo_hash=hashed_password)
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
