from app import fApp
from app import login

# TODO rename fApp back to app and rename module dir to project name
print('THIS IS WIP - DO NOT USE IN PRODUCTION UNTIL THIS MESSAGE DISAPPEARS!')

def getApp():
    return fApp

def start():
    fApp.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    start()
