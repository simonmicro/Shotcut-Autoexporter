from app import app

@app.route('/')
def index():
    return 'TODO: ?'
    
@app.route('/login')
def login():
    return 'TODO: Login, when ip outside of range: Access denied'
    
@app.route('/list')
def list():
    return 'TODO: List current projects (queued, in progress, success, failure), Logout, Add project'
    
@app.route('/upload')
def upload():
    return 'TODO: Add file, Add folder, Upload'
