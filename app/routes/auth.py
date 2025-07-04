from flask import Blueprint, render_template, redirect, url_for, request, flash 
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from app.forms import LoginForm, RegistrationForm
from app.models.pacjent import Pacjent
from app.models.lekarz import Lekarz
from app.models.recepcjonista import Recepcjonista
from app.models.administrator import Administrator
from app.extensions import db
from app.models.ordynator import Ordynator


auth_bp = Blueprint('auth_bp', __name__)

def find_user_by_email(email):
    user = (Administrator.query.filter_by(email=email).first() or
            Lekarz.query.filter_by(email=email).first() or
            Recepcjonista.query.filter_by(email=email).first() or
            Pacjent.query.filter_by(email=email).first() or
            Ordynator.query.filter_by(email=email).first()
            ) 
    #DEBUG
    # print(f"DEBUG find_user_by_email for {email}:")
    # print(f"  Admin: {admin}")
    # print(f"  Lekarz: {lekarz}")
    # print(f"  Pacjent: {pacjent}")
    # print(f"  Recepcjonista: {recepcjonista}")
    
    # user = admin or lekarz or pacjent or recepcjonista
    # print(f"  Selected: {user.__class__.__name__ if user else 'None'}")
    return user

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_bp.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = find_user_by_email(form.email.data)

        if user and check_password_hash(user.haslo_hash, form.password.data):
            login_user(user)
            print(f"Zalogowano jako: {user.__class__.__name__}")

            if isinstance(user, Administrator):
                return redirect(url_for('administrator_bp.dashboard'))
            elif isinstance(user, Lekarz):
                return redirect(url_for('lekarz_bp.dashboard'))
            elif isinstance(user, Pacjent):
                return redirect(url_for('pacjent_bp.dashboard'))
            elif isinstance(user, Recepcjonista):  
                return redirect(url_for('recepcjonista_bp.dashboard'))
            elif isinstance(user, Ordynator):  
                return redirect(url_for('ordynator_bp.dashboard'))
            else:
                flash('Nieznana rola użytkownika.', 'danger')
        else:
            flash('Nieprawidłowy email lub hasło.', 'danger')

    return render_template('login.html', form=form)


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

