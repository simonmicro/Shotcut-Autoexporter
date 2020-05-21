import os
import sys
import time
import subprocess

print ("Working dir is %s" % os.getcwd())

def mkdir(path):
    try:
        os.mkdir(path)
    except OSError as e:
#        print 'Creation of the directory', path, 'failed:', format(e)
        True

# Some dir definitions
inputDir = os.getcwd() + '/input/'
processingDir = os.getcwd() + '/processing/'
successDir = os.getcwd() + '/success/'
failureDir = os.getcwd() + '/failure/'
shotcutDir = os.getcwd() + '/shotcut/'

# Create the expected dirs...
mkdir(inputDir)
mkdir(processingDir)
mkdir(successDir)
mkdir(failureDir)

# Make sure we have the Shotcut exporter binary...
if not os.path.exists(shotcutDir + 'qmelt'):
    sys.exit('Ooops, Shotcut binaries are missing!')

while True:
    # Now check every subfolder inside the input if the have the OK(-file) to start it...
    for (dirpath, dirnames, filenames) in os.walk(inputDir):
        print('Inputs:', dirnames)
        for dirname in dirnames:
            foundOK = False
            for (dirpath, dirnames, filenames) in os.walk(inputDir + dirname):
                if 'OK' in filenames:
                    foundOK = True
                break
            if not foundOK:
                print('Project', dirname, 'has no OK file -> ignoring...')
                continue
            # If yes, move it over to the processing section...
            print('Project', dirname, 'has the OK file -> moving the project over to processing...')
            os.rename(inputDir + dirname, processingDir + dirname)
            os.remove(processingDir + dirname + '/OK')
        break

    # Now run the export for every project folder inside the processing dir
    for (dirpath, dirnames, filenames) in os.walk(processingDir):
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
            print('Found project file for', dirname, '-> starting export...')
            # Run export command with log file...
            log = open(processingDir + dirname + '/LOG', 'w')
            result = subprocess.run([shotcutDir + 'qmelt', '-abort', '-progress', '-consumer', 'avformat:' + os.path.splitext(projectFile)[0] + '.mp4', projectFile], stderr=log, stdout=log, cwd=processingDir + dirname)
            log.close()
            # And check the return code
            if result.returncode is 0:
                print('Good return value -> SUCCESS')
                os.rename(processingDir + dirname, successDir + dirname)
            else:
                print('Bad return value -> FAILED')
                os.rename(processingDir + dirname, failureDir + dirname)
        break

    # Sleep a while before next run...
    print('Sleeping...')
    time.sleep(10)
