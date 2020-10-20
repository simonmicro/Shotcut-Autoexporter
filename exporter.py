#!/usr/bin/env python3

import os
import sys
import xml.dom.minidom
import time
import subprocess
import dbus
import datetime
import logging
logging.basicConfig(filename='exporter.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

logging.info('Working dir is' + os.getcwd())

def mkdir(path):
    try:
        os.mkdir(path)
    except OSError as e:
        logging.warning('Creation of the directory ' + path + ' failed: ' + format(e))

# Config
enable_inhibit_prevention = True

# Some dir definitions
workingDir = os.getcwd()
inputDir = workingDir + '/input/'
processingDir = workingDir + '/processing/'
outDir = workingDir + '/output/'
failureDir = outDir + 'failure/'
successDir = outDir + 'success/'
shotcutDir = workingDir + '/shotcut/'
shotcutQmelt = shotcutDir + 'qmelt'

# Create the expected dirs...
mkdir(inputDir)
mkdir(processingDir)
mkdir(outDir)
mkdir(successDir)
mkdir(failureDir)

# Now prepare the dbus (if enabled)
session_manager = None
if(enable_inhibit_prevention):
    session_manager = dbus.SessionBus().get_object('org.gnome.SessionManager', '/org/gnome/SessionManager')

# Make sure we have the Shotcut exporter binary...
if not os.path.exists(shotcutQmelt):
    sys.exit('Ooops, Shotcuts qmelt is missing (expected at ' + shotcutQmelt + ')!')

while True:
    # Make sure the log is written
    sys.stdout.flush()

    # Check if the input folder contains the OK file
    foundOK = False
    for (dirpath, dirnames, filenames) in os.walk(inputDir):
        if 'OK' in filenames:
            foundOK = True
        break

    # If we've got the OK, move all project folders into processing...
    if(foundOK):
        for (dirpath, dirnames, filenames) in os.walk(inputDir):
            logging.debug('Inputs: ' + str(dirnames))
            for dirname in dirnames:
                # Move it over to the processing section...
                logging.info('Project ' + dirname + ' found -> moving the project over to the processing area...')
                os.rename(inputDir + dirname, processingDir + dirname)
            break
        os.remove(inputDir + 'OK')

    # Now run the export for every project folder inside the processing dir
    processed = False
    for (dirpath, dirnames, filenames) in os.walk(processingDir):
        if not len(dirnames):
            continue
        processed = True
        logging.info('Queued projects: ' + str(dirnames))
        for dirname in dirnames:
            projectFile = None
            for (dirpath, dirnames, filenames) in os.walk(processingDir + dirname):
                for filename in filenames:
                    if filename.endswith('.mlt'):
                        projectFile = filename
                        break
                break
            if projectFile is None:
                # No project file found -> move it over to failure
                logging.error('Could not find any .mlt file for ' + dirname + ' -> FAILED')
                os.rename(processingDir + dirname, failureDir + dirname)
                continue
            logging.debug('Found project file for ' + dirname + ' -> resolving to relative path...')
            projectPath = processingDir + dirname + '/'
            # Load the doc
            xmlFile = xml.dom.minidom.parse(projectPath + projectFile)
            items = xmlFile.getElementsByTagName('property')
            # Replace all path to relative
            for item in items:
                if item.getAttribute('name') == 'resource':
                    item.firstChild.nodeValue = os.path.basename(item.firstChild.nodeValue)
            # Write modified project file back
            correctedPojectFile = os.path.splitext(projectFile)[0] + '.relative.mlt'
            out = open(projectPath + correctedPojectFile, 'w')
            xmlFile.writexml(out)
            out.close()
            logging.debug('Prepared ' + dirname + ' -> starting export...')
            # Inhibit dbus if enabled
            inhibit_cookie = None
            if(enable_inhibit_prevention):
                logging.debug('Inhibiting dbus...')
                inhibit_cookie = session_manager.Inhibit('shotcut-autoexporter', dbus.UInt32(0), 'export', dbus.UInt32(8), dbus_interface='org.gnome.SessionManager')
            # Run export command with log file...
            log = open(projectPath + '/LOG', 'w')
            result = subprocess.run([shotcutQmelt, '-verbose', '-progress', '-consumer', 'avformat:' + os.path.splitext(projectFile)[0] + '.mp4', correctedPojectFile], stderr=log, stdout=log, cwd=processingDir + dirname)
            log.close()
            # Uninhibit dbus if enabled
            if(enable_inhibit_prevention):
                logging.debug('Uninhibiting dbus...')
                session_manager.Uninhibit(inhibit_cookie, dbus_interface='org.gnome.SessionManager')
            # Remove modified project file again...
            os.remove(projectPath + correctedPojectFile)
            # And check the return code
            if result.returncode == 0:
                logging.debug('Good return value -> SUCCESS')
                os.rename(projectPath, successDir + dirname)
            else:
                logging.error('Bad return value -> FAILED')
                os.rename(projectPath, failureDir + dirname)
        break

    # Sleep a while before next run (only show text if we have done anything)...
    if foundOK or processed:
        logging.debug('Sleeping...')
    time.sleep(10)
