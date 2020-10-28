from flask import Flask
from app.models import User
from flask_login import LoginManager
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'you-will-never-guess' # TODO make that secure!
login = LoginManager(app)
login.login_view = 'login'

@login.user_loader
def load_user(id):
    return User()

from app import routes
