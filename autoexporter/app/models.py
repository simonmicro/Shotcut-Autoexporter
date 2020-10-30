import os
import shutil
import werkzeug
import logging
from flask_login import UserMixin
import app.config
import xml.dom.minidom
import subprocess
import re
import datetime

projects = []

class User(UserMixin):
    def __init__(self):
        # TEMP generate here the login pwd hash
        self.pwdhash = werkzeug.security.generate_password_hash(app.config.password)
        self.id = 42
        
    def check_password(self, pwd):
        return werkzeug.security.check_password_hash(self.pwdhash, pwd)
        
class Project():
    def __init__(self, id, status):
        self.id = werkzeug.utils.secure_filename(id)
        self.name = None
        self.status = None
        self.setStatus(status)
        
    @staticmethod
    def get(id):
        for p in projects:
            if p.getId() == id:
                return p
        return None
        
    def getId(self):
        return self.id
        
    def getName(self):
        if self.name == None:
            self.searchName()
        return self.name
        
    def getStatus(self):
        return self.status
        
    def getProgress(self):
        value = None
        log = self.getLog()
        for line in log[::-1]:
            m = re.search(r'\d+$', line)
            # if the string ends in digits m will be a Match object, or None otherwise.
            if m is not None:
                value = int(m.group())
                break
        return value
        
    def getDir(self, status = None):
        if status == None:
            status = self.status
        return os.path.join(app.config.dirConfig[status], self.id)
        
    def setStatus(self, status):
        if self.status != None and self.status != status:
            oldPath = self.getDir()
            newPath = self.getDir(status)
            if not os.path.isdir(oldPath):
                raise Exception('Project id ' + self.id + ' not found')
            if os.path.isdir(newPath):
                raise Exception('Project id ' + self.id + ' conflict')
            shutil.move(oldPath, newPath)
            logging.info('Project id ' + self.id + ' status change: ' + str(self.status) + ' -> ' + str(status))
        self.status = status
        if self.status == app.config.STATUS_QUEUED:
                self.searchName()
                
    def searchName(self):
        foundMLT = False
        for fname in os.listdir(self.getDir()):
            if os.path.splitext(fname)[1].lower() == '.mlt':
                self.name = os.path.splitext(fname)[0]
                foundMLT = True
        if not foundMLT:
            self.setStatus(app.config.STATUS_FAILURE)
                
    def getLog(self):
        logFilePath = os.path.join(self.getDir(), 'LOG')
        if os.path.isfile(logFilePath):
            lines = None
            with open(logFilePath) as f:
                lines = f.readlines()
            return lines
        else:
            return None
            
    def getResultPath(self):
        if self.status == app.config.STATUS_SUCCESS:
            return os.path.join(self.getDir(), self.id + '.mp4')
        else:
            return None
        
    def delete(self):
        if self.status != app.config.STATUS_WORKING:
            shutil.rmtree(self.getDir())
            projects.remove(self)
            logging.info('Project id ' + self.id + ' deleted')
            return True
        return False
        
    def run(self):
        logging.info('Project id ' + self.id + ' running...')
        self.setStatus(app.config.STATUS_WORKING)
        # Open the log file...
        logFile = open(os.path.join(self.getDir(), 'LOG'), 'w')
        mltPath = os.path.join(self.getDir(), self.name + '.mlt')
        logFile.write('Starting export of ' + mltPath + ' (' + self.id + ') at ' + str(datetime.datetime.now()))
        # Load the project-xml
        xmlFile = xml.dom.minidom.parse(mltPath)
        items = xmlFile.getElementsByTagName('property')
        # Replace all paths to relative
        for item in items:
            if item.getAttribute('name') == 'resource':
                item.firstChild.nodeValue = os.path.basename(item.firstChild.nodeValue)
        # Write modified project file back
        out = open(os.path.join(self.getDir(), mltPath), 'w')
        xmlFile.writexml(out)
        out.close()
        logFile.write('Secured project file, starting Shotcut...')
        # Run export command...
        result = subprocess.run([app.config.shotcutQmelt, '-verbose', '-progress', '-consumer', 'avformat:' + self.id + '.mp4', mltPath], stderr=logFile, stdout=logFile, cwd=self.getDir())
        logFile.write('Finished export at ' + str(datetime.datetime.now()))
        logFile.close()
        if result.returncode == 0:
            self.setStatus(app.config.STATUS_SUCCESS)
        else:
            self.setStatus(app.config.STATUS_FAILURE)
