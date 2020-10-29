import os
import tempfile
import logging

dirConfig = {
    'upload': tempfile.mkdtemp(),
    'queue': os.path.join(os.getcwd(), 'data', 'queued'),
    'working': os.path.join(os.getcwd(), 'data', 'working'),
    'success': os.path.join(os.getcwd(), 'data', 'ok'),
    'failure': os.path.join(os.getcwd(), 'data', 'failed')
}
logging.debug(dirConfig)

for key in dirConfig:
    os.makedirs(dirConfig[key], exist_ok=True)
