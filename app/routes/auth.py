
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from app.forms import LoginForm, RegistrationForm
from app.models.pacjent import Pacjent
from app.models.lekarz import Lekarz
from app.models.recepcjonista import Recepcjonista
from app.models.administrator import Administrator
from app.extensions import db



auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = None
        role = None

        #role check
        user = Pacjent.query.filter_by(email=email).first()
        if user and check_password_hash(user.haslo_hash, password):
            role = 'pacjent'
        else:
            user = Lekarz.query.filter_by(email=email).first()
            if user and check_password_hash(user.haslo_hash, password):
                role = 'lekarz'
            else:
                user = Recepcjonista.query.filter_by(email=email).first()
                if user and check_password_hash(user.haslo_hash, password):
                    role = 'recepcjonista'
                else:
                    user = Administrator.query.filter_by(email=email).first()
                    if user and check_password_hash(user.haslo_hash, password):
                        role = 'administrator'

        if user and role:
            login_user(user)
            if role == 'pacjent':
                return redirect(url_for('pacjent_bp.dashboard'))
            elif role == 'lekarz':
                return redirect(url_for('lekarz_bp.dashboard'))
            elif role == 'recepcjonista':
                return redirect(url_for('recepcjonista_bp.dashboard'))
            elif role == 'administrator':
                return redirect(url_for('administrator_bp.dashboard'))
        else:
            flash('Nieprawidłowy email lub hasło.', 'danger')

    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_bp.login'))


#registration form
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_pacjent = Pacjent(
            imie=form.imie.data,
            nazwisko=form.nazwisko.data,
            email=form.email.data,
            telefon=form.telefon.data,
            adres=form.adres.data,
            data_urodzenia=form.data_urodzenia.data,
            pesel=form.pesel.data,
            haslo_hash=generate_password_hash(form.haslo.data)
        )
        db.session.add(new_pacjent)
        db.session.commit()
        flash('Zarejestrowano pomyślnie. Możesz się zalogować.', 'success')
        return redirect(url_for('auth_bp.login'))
    return render_template('register.html', form=form)





# @auth_bp.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('auth_bp.login'))
