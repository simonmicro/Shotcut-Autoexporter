from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app
from app.config import dirConfig
from app.models import projects, User, Project, STATUS_UPLOAD, STATUS_QUEUED, STATUS_WORKING, STATUS_SUCCESS, STATUS_FAILURE
from app.forms import LoginForm
import os
import logging
import werkzeug

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
        if 'id' in request.form:
            project = Project(request.form['id'], STATUS_UPLOAD)
            if 'file' in request.files and 'path' in request.form:
                # The following just resolves the given path to the new project dir root of the os
                absPathInProject = os.path.relpath(os.path.normpath(os.path.join('/', request.form['path'])), '/')
                absPathInSystem = os.path.join(project.getDir(), absPathInProject)
                # Make in-project subdirs...
                os.makedirs(os.path.split(absPathInSystem)[0], exist_ok=True)
                # And save the file itself!
                request.files['file'].save(absPathInSystem)
                logging.info('File uploaded for project id ' + project.getId() + ' to ' + absPathInSystem)
                return 'OK'
            elif 'finish' in request.form:
                try:
                    project.setStatus(STATUS_QUEUED)
                except Exception as e:
                    return e, 500
                projects.append(project)
                logging.info('Upload complete for project id ' + project.getId())
                return 'OK'
            else:
                return 'Incomplete upload/finish request!', 400
        else:
            return 'Incomplete upload/finish request!', 400
    # TODO: Add file, Add folder, Upload
    return render_template('upload.html', title='UPLOAD')
