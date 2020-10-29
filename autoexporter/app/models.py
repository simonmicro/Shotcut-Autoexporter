import os
import shutil
import werkzeug
from flask_login import UserMixin
from app.config import dirConfig

import random #TEMP

projects = []

STATUS_UPLOAD = 4
STATUS_QUEUED = 0
STATUS_WORKING = 1
STATUS_SUCCESS = 2
STATUS_FAILURE = 3

class User(UserMixin):
    def __init__(self):
        # TEMP generate here the login pwd hash
        self.pwdhash = werkzeug.security.generate_password_hash('password42')
        self.id = 42
        
    def check_password(self, pwd):
        return werkzeug.security.check_password_hash(self.pwdhash, pwd)
        
class Project():
    def __init__(self, id, status):
        self.id = werkzeug.utils.secure_filename(id)
        self.status = status
        self.name = None
        
    def getId(self):
        return self.id
        
    def getName(self):
        return self.id
        
    def getStatus(self):
        return self.status
        
    def getProgress(self):
        return random.random()
        
    def getDir(self, status = None):
        if status == None:
            status = self.status
        if status == STATUS_UPLOAD:
            return os.path.join(dirConfig['upload'], self.id)
        elif status == STATUS_QUEUED:
            # TODO extract .mlt filename now
            return os.path.join(dirConfig['queue'], self.id)
        elif status == STATUS_WORKING:
            return os.path.join(dirConfig['working'], self.id)
        elif status == STATUS_SUCCESS:
            return os.path.join(dirConfig['success'], self.id)
        elif status == STATUS_FAILURE:
            return os.path.join(dirConfig['failure'], self.id)
        else:
            raise Exception('Unsopported status')
        
    def setStatus(self, status):
        if self.status == status:
            return
        oldPath = self.getDir()
        newPath = self.getDir(status)
        if not os.path.isdir(oldPath):
            raise Exception('Project id not found')
        if os.path.isdir(newPath):
            raise Exception('Project id conflict')
        shutil.move(oldPath, newPath)
        self.status = status
        
    def delete(self):
        # TODO remove dir
        pass
        
        
        
        
        
        
        
        
projects = [
    Project('ydnltizahg', STATUS_QUEUED),
    Project('ydnltizfhg', STATUS_WORKING),
    Project('ydnltiashg', STATUS_SUCCESS),
    Project('ydgltizbhg', STATUS_FAILURE)
]
