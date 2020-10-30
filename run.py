from app import fApp
from app import login

def getApp():
    return fApp
    
if __name__ == '__main__':
    fApp.run(host='0.0.0.0', port=5000, use_reloader=False, debug=True)
