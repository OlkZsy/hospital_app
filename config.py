import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'verysecretkey'
    SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin@localhost/hospitaldb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
