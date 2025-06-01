# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo





class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    submit = SubmitField('Zaloguj się')

class RegistrationForm(FlaskForm):
    imie = StringField('Imię', validators=[DataRequired()])
    nazwisko = StringField('Nazwisko', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    haslo = PasswordField('Hasło', validators=[DataRequired(), Length(min=6)])
    haslo_potwierdzenie = PasswordField('Potwierdź hasło', validators=[DataRequired(), EqualTo('haslo')])
    telefon = StringField('Telefon')
    adres = StringField('Adres')
    data_urodzenia = DateField('Data urodzenia')
    pesel = StringField('PESEL', validators=[Length(min=11, max=11)])
    submit = SubmitField('Zarejestruj się')