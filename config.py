import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'secretsecretkey'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:admin@localhost/hospitaldb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOWED_IPS = ['192.168.1.0/24'] # <-- only local ip's