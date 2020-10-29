import os
import time
import logging
import app.config
import app.models
from multiprocessing import Process

import signal
import atexit
import schedule
import threading

jLog = logging.getLogger(__name__)
run_threads = True

# Jobs

def doCleanup():
    jLog.info('Cleaning projects...')
    # TODO clean uploads (24h)!
    for p in app.models.projects:
        if p.getStatus() == app.config.STATUS_SUCCESS:
            s = os.stat(p.getDir())
            if s.st_atime < (time.time() - 60 * 60 * 24 * 30):
                p.delete()
        elif p.getStatus() == app.config.STATUS_FAILURE:
            s = os.stat(p.getDir())
            if s.st_atime < (time.time() - 60 * 60 * 24 * 7):
                p.delete()
schedule.every().day.do(doCleanup)
        
def doWork():
    jLog.debug('Working on queue...')
    for p in app.models.projects:
        jLog.debug(p.getName() + str(p.getStatus()))
        if p.getStatus() == app.config.STATUS_QUEUED:
            p.run()
schedule.every(10).seconds.do(doWork)

# Worker-thread-model

def bgWorker():
    global run_threads
    while run_threads:
        jLog.info('Running jobs...')
        schedule.run_pending()
        sleeptime = schedule.idle_seconds()
        if sleeptime > 0:
            time.sleep(sleeptime)
    jLog.info('Jobs execution stopped!')

bgThread = threading.Thread(target=bgWorker)
bgThread.start()

def stopAllJobs():
    global run_threads
    logging.info('Shutting down jobs...')
    run_threads = False
    bgThread.join() 
atexit.register(stopAllJobs)
signal.signal(signal.SIGINT, lambda a, b : stopAllJobs())
signal.signal(signal.SIGTERM, lambda a, b : stopAllJobs())
