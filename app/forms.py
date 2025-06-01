# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    submit = SubmitField('Zaloguj się')

class RegistrationForm(FlaskForm):
    imie = StringField('Imię', validators=[DataRequired()])
    nazwisko = StringField('Nazwisko', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    telefon = StringField('Telefon', validators=[DataRequired()])
    haslo = PasswordField('Hasło', validators=[DataRequired(), Length(min=6)])
    haslo_potwierdzenie = PasswordField('Potwierdź hasło', validators=[DataRequired(), EqualTo('haslo')])
    submit = SubmitField('Zarejestruj się')

class RegisterUserForm(FlaskForm): #administrator form
    imie = StringField('Imię', validators=[DataRequired()])
    nazwisko = StringField('Nazwisko', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telefon = StringField('Telefon', validators=[DataRequired()])
    haslo = PasswordField('Hasło', validators=[DataRequired()])
    rola = SelectField('Rola', choices=[
        ('lekarz', 'Lekarz'),
        ('recepcjonista', 'Recepcjonista'),
        ('administrator', 'Administrator')
    ], validators=[DataRequired()])
    submit = SubmitField('Zarejestruj')
