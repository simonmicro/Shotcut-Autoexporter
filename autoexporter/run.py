from app import fApp
from app import login

print('THIS IS AN TECHNICAL DEMO - DO NOT USE IN PRODUCTION UNTIL THIS MESSAGE DISAPPEARS!')

def init():
    return fApp

def start():
    fApp.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    start()

# TODO rename fApp back to app and rename module dir to project name
