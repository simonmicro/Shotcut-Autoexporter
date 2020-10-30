import os
import tempfile
import logging

STATUS_UPLOAD = 4
STATUS_QUEUED = 0
STATUS_WORKING = 1
STATUS_SUCCESS = 2
STATUS_FAILURE = 3

shotcutQmelt = os.path.join(os.getcwd(), 'shotcut', 'qmelt')

allowedIPs = [
    '192.168.0.1/16'
]

dirConfig = {
    STATUS_UPLOAD: tempfile.mkdtemp(),
    STATUS_QUEUED: os.path.join(os.getcwd(), 'data', 'queued'),
    STATUS_WORKING: os.path.join(os.getcwd(), 'data', 'working'),
    STATUS_SUCCESS: os.path.join(os.getcwd(), 'data', 'ok'),
    STATUS_FAILURE: os.path.join(os.getcwd(), 'data', 'failed')
}
logging.debug(dirConfig)

for key in dirConfig:
    os.makedirs(dirConfig[key], exist_ok=True)
