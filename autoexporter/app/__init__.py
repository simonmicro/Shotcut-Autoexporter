from flask import Flask
from app.models import User
from flask_login import LoginManager
import os
import logging
import app.config
import app.models
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

# Init app
fApp = Flask(__name__)
fApp.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'you-will-never-guess' # TODO make that secure!
login = LoginManager(fApp)
login.login_view = 'login'

@login.user_loader
def load_user(id):
    return User()
    
# Rescan projects...
for status in app.config.dirConfig:
    for id in os.listdir(app.config.dirConfig[status]):
        app.models.projects.append(app.models.Project(id, status))
        
from app import routes
