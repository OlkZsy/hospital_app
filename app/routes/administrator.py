from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.models.wizyta import Wizyta
from app.models.lekarz import Lekarz
from app.models.recepcjonista import Recepcjonista
from app.models.administrator import Administrator
from app import db
from app.forms import RegisterUserForm

administrator_bp = Blueprint('administrator_bp', __name__, url_prefix='/administrator')

@administrator_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboards/administrator.html')

@administrator_bp.route('/wizyty')
@login_required
def wizyty():
    wizyty = Wizyta.query.order_by(Wizyta.data_wizyty).all()
    return render_template('administrator/wizyty.html', wizyty=wizyty)

@administrator_bp.route('/register-user', methods=['GET', 'POST'])
@login_required
def register_user():
    if not isinstance(current_user, Administrator):
        flash("Brak dostępu", "danger")
        return redirect(url_for('auth_bp.login'))

    form = RegisterUserForm()
    if form.validate_on_submit():
        hashed = generate_password_hash(form.haslo.data)

        rola = form.rola.data
        email = form.email.data

        if rola == 'lekarz':
            nowy = Lekarz(imie=form.imie.data, nazwisko=form.nazwisko.data,
                          email=email, telefon=form.telefon.data,
                          haslo_hash=hashed, specjalizacja='', numer_licencji='L' + email[:4])
        elif rola == 'recepcjonista':
            nowy = Recepcjonista(imie=form.imie.data, nazwisko=form.nazwisko.data,
                                 email=email, telefon=form.telefon.data,
                                 haslo_hash=hashed)
        elif rola == 'administrator':
            nowy = Administrator(imie=form.imie.data, nazwisko=form.nazwisko.data,
                                 email=email, telefon=form.telefon.data,
                                 haslo_hash=hashed)

        db.session.add(nowy)
        db.session.commit()
        flash(f'Użytkownik {rola} został utworzony.', 'success')
        return redirect(url_for('administrator_bp.dashboard'))

    return render_template('register_user.html', form=form)
