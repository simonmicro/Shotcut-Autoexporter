#!/usr/bin/env python3

import os
import sys
import xml.dom.minidom
import time
import subprocess
import dbus

sys.stdout = open('exporter.log', 'w')

print('Working dir is', os.getcwd())

def mkdir(path):
    try:
        os.mkdir(path)
    except OSError as e:
#        print 'Creation of the directory', path, 'failed:', format(e)
        pass

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
            print('Inputs:', dirnames)
            for dirname in dirnames:
                # Move it over to the processing section...
                print('Project', dirname, 'found -> moving the project over to the processing area...')
                os.rename(inputDir + dirname, processingDir + dirname)
            break
        os.remove(inputDir + 'OK')

    # Now run the export for every project folder inside the processing dir
    processed = False
    for (dirpath, dirnames, filenames) in os.walk(processingDir):
        if not len(dirnames):
            continue
        processed = True
        print('Queued projects:', dirnames)
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
                print('Could not find any .mlt file for', dirname, '-> FAILED')
                os.rename(processingDir + dirname, failureDir + dirname)
                continue
            print('Found project file for', dirname, '-> resolving to relative path...')
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
            print('Done', dirname, '-> starting export...')
            # Inhibit dbus if enabled
            inhibit_cookie = None
            if(enable_inhibit_prevention):
                print('Inhibiting dbus...')
                inhibit_cookie = session_manager.Inhibit('shotcut-autoexporter', dbus.UInt32(0), 'export', dbus.UInt32(8), dbus_interface='org.gnome.SessionManager')
            # Run export command with log file...
            log = open(projectPath + '/LOG', 'w')
            result = subprocess.run([shotcutQmelt, '-verbose', '-progress', '-consumer', 'avformat:' + os.path.splitext(projectFile)[0] + '.mp4', correctedPojectFile], stderr=log, stdout=log, cwd=processingDir + dirname)
            log.close()
            # Uninhibit dbus if enabled
            if(enable_inhibit_prevention):
                print('Uninhibiting dbus...')
                session_manager.Uninhibit(inhibit_cookie, dbus_interface='org.gnome.SessionManager')
            # Remove modified project file again...
            os.remove(projectPath + correctedPojectFile)
            # And check the return code
            if result.returncode is 0:
                print('Good return value -> SUCCESS')
                os.rename(projectPath, successDir + dirname)
            else:
                print('Bad return value -> FAILED')
                os.rename(projectPath, failureDir + dirname)
        break

    # Sleep a while before next run (only show text if we have done anything)...
    if foundOK or processed:
        print('Sleeping...')
    time.sleep(10)
