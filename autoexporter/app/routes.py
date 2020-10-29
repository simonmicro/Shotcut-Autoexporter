from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app
from app.config import dirConfig
from app.models import User, STATUS_QUEUED, STATUS_WORKING, STATUS_SUCCESS, STATUS_FAILURE
from app.forms import LoginForm
import os
import shutil
import logging
import werkzeug

projects = [
    {
        'id':'ydnltizahg',
        'name':'Queued',
        'progress':None,
        'status':STATUS_QUEUED
    },
    {
        'id':'ydnltizfhg',
        'name':'In progress',
        'progress':0.6,
        'status':STATUS_WORKING
    },
    {
        'id':'ydnltiashg',
        'name':'Success',
        'progress':None,
        'status':STATUS_SUCCESS
    },
    {
        'id':'ydgltizbhg',
        'name':'Failed',
        'progress':None,
        'status':STATUS_FAILURE
    }
]

@app.route('/')
def index():
    # TODO: ?
    return redirect(url_for('login'))
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    # TODO: Login, when ip outside of range: Access denied
    if current_user.is_authenticated:
        return redirect(url_for('list'))
    # For now we will always login
    form = LoginForm()
    user = User()
    if form.validate_on_submit():
        if not user.check_password(form.password.data):
            flash('wrong pwd')
            return redirect(url_for('login'))
        flash('Welcome!')
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or werkzeug.urls.url_parse(next_page).netloc != '':
            next_page = url_for('login')
        return redirect(next_page)
    return render_template('login.html', title='LOGIN', form=form)
    
@app.route('/delete')
@login_required
def delete():
    flash('TODO: delete')
    return redirect('list')
    
@app.route('/log')
@login_required
def log():
    flash('TODO: log')
    return redirect('list')
    
@app.route('/download')
@login_required
def download():
    flash('TODO: download')
    return redirect('list')

@app.route('/logout')
@login_required
def logout():
    flash('Bye!')
    logout_user()
    return redirect(url_for('login'))

@app.route('/list')
@login_required
def list():
    # TODO: List current projects (queued, in progress, success, failure), Logout, Add project
    return render_template('list.html', title='LIST', projects=projects)
    
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' in request.files and 'path' in request.form and 'id' in request.form:
            # The following just resolves the given path to the new project dir root of the os
            projectId = werkzeug.utils.secure_filename(request.form['id'])
            absPathInProject = os.path.relpath(os.path.normpath(os.path.join('/', request.form['path'])), '/')
            absPathInSystem = os.path.join(dirConfig['upload'], projectId, absPathInProject)
            # Make in-project subdirs...
            os.makedirs(os.path.split(absPathInSystem)[0], exist_ok=True)
            # And save the file itself!
            request.files['file'].save(absPathInSystem)
            logging.info('File uploaded for project id ' + projectId + ' to ' + absPathInSystem)
            return 'OK'
        elif 'finish' in request.form and 'id' in request.form:
            projectId = werkzeug.utils.secure_filename(request.form['id'])
            absProjectPathInUpload = os.path.join(dirConfig['upload'], projectId)
            if not os.path.isdir(absProjectPathInUpload):
                return 'Project id not found', 404
            absProjectPathInQueue = os.path.join(dirConfig['queue'], projectId)
            if os.path.isdir(absProjectPathInQueue):
                return 'Project id already finished', 400
            shutil.move(absProjectPathInUpload, absProjectPathInQueue)
            logging.info('Upload complete for project id ' + projectId)
            return 'OK'
        else:
            return 'Incomplete upload/finish request!', 400
    # TODO: Add file, Add folder, Upload
    return render_template('upload.html', title='UPLOAD')
