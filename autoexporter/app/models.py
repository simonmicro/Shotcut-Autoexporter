import os
import shutil
import werkzeug
from flask_login import UserMixin
import app.config

import random #TEMP

projects = []

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
        if status == app.config.STATUS_QUEUED:
            # TODO extract .mlt filename now
            pass
        return os.path.join(app.config.dirConfig[app.config.STATUS_UPLOAD], self.id)
        
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
    Project('ydnltizahg', app.config.STATUS_QUEUED),
    Project('ydnltizfhg', app.config.STATUS_WORKING),
    Project('ydnltiashg', app.config.STATUS_SUCCESS),
    Project('ydgltizbhg', app.config.STATUS_FAILURE)
]
