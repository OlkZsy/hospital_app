
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    submit = SubmitField('Zaloguj się')

class RegistrationForm(FlaskForm):
    imie = StringField('Imię', validators=[DataRequired(), Length(min=2, max=50)])
    nazwisko = StringField('Nazwisko', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telefon = StringField('Telefon', validators=[DataRequired(), Length(min=9, max=15)])
    haslo = PasswordField('Hasło', validators=[DataRequired(), Length(min=6)])
    adres = StringField('Adres', validators=[DataRequired(), Length(min=5, max=100)])
    data_urodzenia = DateField('Data urodzenia', format='%Y-%m-%d', validators=[DataRequired()])
    pesel = StringField('PESEL', validators=[DataRequired(), Length(min=11, max=11)])
    submit = SubmitField('Zarejestruj się')

class RegisterUserForm(FlaskForm):
    imie = StringField('Imię', validators=[DataRequired()])
    nazwisko = StringField('Nazwisko', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telefon = StringField('Telefon', validators=[DataRequired()])
    haslo = PasswordField('Hasło', validators=[DataRequired()])
    specjalizacja = SelectField('Specjalizacja', choices=[
        ('Medycyna Ogólna', 'Medycyna Ogólna'),
        ('Kardiologia', 'Kardiologia'),
        ('Pediatria', 'Pediatria'),
        ('Chirurgia', 'Chirurgia'),
        ('Neurologia', 'Neurologia'),
        ('Dermatologia', 'Dermatologia'),
        ('Ginekologia', 'Ginekologia'),
        ('Ortopedia', 'Ortopedia'),
        ('Okulistyka', 'Okulistyka'),
        ('Psychiatria', 'Psychiatria')
    ])
    dzial = StringField('Dział/Specjalizacja', validators=[Length(max=100)])
    rola = SelectField('Rola', choices=[
        ('lekarz', 'Lekarz'),
        ('recepcjonista', 'Recepcjonista'),
        ('administrator', 'Administrator'),
        ('ordynator', 'Ordynator') 
    ], validators=[DataRequired()])
    submit = SubmitField('Zarejestruj')
