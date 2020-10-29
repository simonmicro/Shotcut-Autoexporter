import time
import atexit
import logging
import app.models
from multiprocessing import Process

def f():
    while True:
        logging.warn('JOB!')
        for p in app.models.projects:
            logging.warn('PROJECT:' + p.getName())
        time.sleep(10)

p = Process(target=f) #, args=('bob',)
p.start()

def stopAllJobs():
    logging.info('Shutting down jobs...')
    p.terminate()
    p.join()
atexit.register(stopAllJobs)
