from flask import Flask
from flask_sqlalchemy import SQLAlchemy

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1234@localhost/invoices'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    SECRET_KEY = 'dklsfnjdnj#e8272[afafe'
    # SECURITY_PASSWORD_SALT = 'fdagsksp33r5wtssgksghpdh'


app = Flask(__name__)
app.config.from_object(Config())
db = SQLAlchemy(app=app, session_options={'autoflush' : False})