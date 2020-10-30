import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

import os
import time
import app.config
import app.models
from flask import Flask
from app.models import User
from flask_login import LoginManager

# TODO rename fApp back to app and rename module dir to project name
logging.warning('THIS IS WIP - DO NOT USE IN PRODUCTION UNTIL THIS MESSAGE DISAPPEARS!')

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
        
for project in app.models.projects:
    if project.getStatus() == app.config.STATUS_WORKING:
        # When we restart the project is commonly also crashed -> requeue!
        logging.warning('Export of ' + project.getId() + ' probably crashed -> requeuing')
        project.setStatus(app.config.STATUS_QUEUED)

# Load all the routes
from app import routes

# Execute the scheduled jobs...
import app.jobs
