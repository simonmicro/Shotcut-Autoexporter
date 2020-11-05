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

logging.getLogger('schedule').propagate = False
jLog = logging.getLogger(__name__)
run_threads = True

# Jobs

def doCleanup():
    jLog.info('Cleaning projects...')
    # TODO clean failed uploads (24h)!
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
        
def startProjects():
    def doWork(p):
        try:
            p.run()
        except Exception as e:
            p.setStatus(app.config.STATUS_FAILURE)
            jLog.error('Project execution failure: ' + str(e))  

    jLog.debug('Working on queue...')
    for p in app.models.projects:
        if p.getStatus() == app.config.STATUS_QUEUED:
            threading.Thread(target=doWork, args=(p,)).start()
            time.sleep(1) # Sleep a while to give the thread time to start up...
schedule.every(10).seconds.do(startProjects)

# Worker-thread-model

def bgWorker():
    global run_threads
    sleeptime = 2
    while run_threads:
        if sleeptime > 0:
            time.sleep(sleeptime)
        jLog.debug('Running jobs...')
        schedule.run_pending()
        sleeptime = schedule.idle_seconds()

bgThread = threading.Thread(target=bgWorker)
bgThread.start()

def stopAllJobs():
    global run_threads
    if run_threads:
        jLog.info('Shutting down jobs (this will may take a while)...')
        run_threads = False
        bgThread.join()
        jLog.info('Jobs shutdowned.')
    else:
        jLog.error('Shutdown already in progress - killing!') # ...just proceed to the exit!
    exit(0)
atexit.register(stopAllJobs)
signal.signal(signal.SIGINT, lambda a, b : stopAllJobs())
#signal.signal(signal.SIGTERM, lambda a, b : stopAllJobs())
