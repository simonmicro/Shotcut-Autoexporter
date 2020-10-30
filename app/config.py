import os
import random
import tempfile
import logging

STATUS_UPLOAD = 4
STATUS_QUEUED = 0
STATUS_WORKING = 1
STATUS_SUCCESS = 2
STATUS_FAILURE = 3

dirConfig = {
    STATUS_UPLOAD: tempfile.mkdtemp(),
    STATUS_QUEUED: os.path.join(os.getcwd(), 'data', 'queued'),
    STATUS_WORKING: os.path.join(os.getcwd(), 'data', 'working'),
    STATUS_SUCCESS: os.path.join(os.getcwd(), 'data', 'ok'),
    STATUS_FAILURE: os.path.join(os.getcwd(), 'data', 'failed')
}
logging.debug(dirConfig)

# Make sure all dirs are there
for key in dirConfig:
    os.makedirs(dirConfig[key], exist_ok=True)

shotcutPath = os.path.join(os.getcwd(), 'shotcut')
shotcutQmelt = os.path.join(shotcutPath, 'Shotcut', 'Shotcut.app', 'qmelt')
password = os.environ.get('PASSWORD')
allowedIPs = os.environ.get('NETWORKS').split(',')
secretKey = os.environ.get('SECRET_KEY') or str(random.random())
shotcutURL = os.environ.get('SHOTCUT_URL')

# Is qmelt there? No? Download Shotcut!
if not os.path.exists(shotcutQmelt):
    logging.info('Shotcuts qmelt does not seem to be available!')
    
    import shutil
    logging.info('Removing old Shotcut files...')
    shutil.rmtree(shotcutPath, ignore_errors=True)
    os.makedirs(shotcutPath, exist_ok=True)
    
    import urllib.request
    tempPath = os.path.join(shotcutPath, 'shotcut.txz')
    logging.info('Downloading Shotcut from "' + shotcutURL + '"...')
    urllib.request.urlretrieve(shotcutURL, tempPath)
    
    import tarfile
    logging.info('Extracting Shotcut...')
    my_tar = tarfile.open(tempPath)
    my_tar.extractall(shotcutPath)
    my_tar.close()
    os.remove(tempPath)
    
    logging.info('Shotcut download complete! Starting app...')
