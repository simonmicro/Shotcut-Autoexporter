from flask import render_template, redirect, url_for
from app import app

@app.route('/')
def index():
    # TODO: ?
    return redirect(url_for('login'))
    
@app.route('/login')
def login():
    # TODO: Login, when ip outside of range: Access denied
    return render_template('login.html', title='LOGIN')
    
@app.route('/list')
def list():
    # TODO: List current projects (queued, in progress, success, failure), Logout, Add project
    return render_template('list.html', title='LIST')
    
@app.route('/upload')
def upload():
    # TODO: Add file, Add folder, Upload
    return render_template('upload.html', title='UPLOAD')
