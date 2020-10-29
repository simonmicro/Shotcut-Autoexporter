import os
import tempfile
import logging

dirConfig = {
    'upload': tempfile.mkdtemp(),
    'queue': os.path.join(os.getcwd(), 'queued'),
    'working': os.path.join(os.getcwd(), 'working'),
    'success': os.path.join(os.getcwd(), 'done', 'success'),
    'failure': os.path.join(os.getcwd(), 'done', 'failure')
}
logging.debug(dirConfig)

for key in dirConfig:
    os.makedirs(dirConfig[key], exist_ok=True)
