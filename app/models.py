import os
import shutil
import werkzeug
import logging
from flask_login import UserMixin
import app.config
import xml.dom.minidom
import signal
import subprocess
import re
import datetime
import time

projects = []

class User(UserMixin):
    def __init__(self):
        # TEMP generate here the login pwd hash
        self.pwdhash = werkzeug.security.generate_password_hash(app.config.password)
        self.id = 42
        self.allowRun = None
        
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
            if bool(re.match('.*percentage:\s+\d+', line)):
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

    def canAbort(self):
        if self.status == app.config.STATUS_QUEUED:
            return False
        return self.allowRun

    def abortRun(self):
        if self.status == app.config.STATUS_QUEUED:
            raise Exception('Project is still queued!')
        self.allowRun = False
        
    def run(self):
        self.allowRun = True
        logging.info('Project id ' + self.id + ' running...')
        self.setStatus(app.config.STATUS_WORKING)
        # Open the log file...
        logFile = open(os.path.join(self.getDir(), 'LOG'), 'ab', buffering=0) # No buffering for maximum responsiveness!
        mltPath = os.path.join(self.getDir(), self.name + '.mlt')
        logFile.write(('Starting export of ' + mltPath + ' (' + self.id + ') at ' + str(datetime.datetime.now()) + '\n').encode())
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
        logFile.write(('Secured project file, starting Shotcut...\n').encode())
        # Run export command...
        process = subprocess.Popen([app.config.shotcutQmelt, '-verbose', '-progress', '-consumer', 'avformat:' + self.id + '.mp4', mltPath], stderr=logFile, stdout=logFile, cwd=self.getDir(), shell=False, preexec_fn=os.setsid, bufsize=1) # Minimal buffering for maximum responsiveness!
        running = None
        while running == None:
            if not self.allowRun:
                # Okay, someone requested to abort the run -> terminate process and set status to failed!
                os.killpg(os.getpgid(process.pid), signal.SIGTERM) # Kill the shell and every child process!
                logFile.write(('Terminate request received at ' + str(datetime.datetime.now()) + '! Waiting for process to end...\n').encode())
                process.communicate() # Wait until the process really ends
                logFile.close()
                self.setStatus(app.config.STATUS_FAILURE)
                return
            running = process.poll()
            time.sleep(1)
        
        logFile.write(('Finished export at ' + str(datetime.datetime.now()) + '\n').encode())
        logFile.close()
        if process.returncode == 0:
            self.setStatus(app.config.STATUS_SUCCESS)
        else:
            self.setStatus(app.config.STATUS_FAILURE)
