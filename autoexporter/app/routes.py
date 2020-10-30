from flask import render_template, redirect, url_for, flash, request, send_file
from flask_login import current_user, login_user, logout_user, login_required
from app import fApp
import app.config
from app.models import projects, User, Project
from app.forms import LoginForm
import os
import logging
import werkzeug
from netaddr import IPNetwork, IPAddress

@fApp.route('/')
def index():
    return redirect(url_for('login'))
    
@fApp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('list'))
    ipOK = False
    for n in app.config.allowedIPs:
        if IPAddress(request.remote_addr) in IPNetwork(n):
            ipOK = True
            break;
    if ipOK:
        form = LoginForm()
        user = User()
        if form.validate_on_submit():
            if not user.check_password(form.password.data):
                flash('Wrong password.')
                return redirect(url_for('login'))
            flash('Welcome!')
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or werkzeug.urls.url_parse(next_page).netloc != '':
                next_page = url_for('login')
            return redirect(next_page)
        return render_template('login.html', title='LOGIN', form=form)
    else:
        return render_template('login.html', title='LOGIN', ipblock=request.remote_addr)
    
@fApp.route('/delete')
@login_required
def delete():
    pid = request.args.get('id')
    if pid:
        p = Project.get(pid)
        if p:
            if p.delete():
                flash('Project "' + p.getName() + '" deleted.')
            else:
                flash('Project "' + p.getName() + '" could not be deleted!')
        else:
            flash('Project not found')
    return redirect('list')
    
@fApp.route('/retry')
@login_required
def retry():
    pid = request.args.get('id')
    if pid:
        p = Project.get(pid)
        if p:
            p.setStatus(app.config.STATUS_QUEUED)
            flash('Project "' + p.getName() + '" requeued.')
        else:
            flash('Project not found')
    return redirect('list')
    
@fApp.route('/log')
@login_required
def log():
    pid = request.args.get('id')
    if pid:
        p = Project.get(pid)
        if p:
            log = p.getLog()
            if log:
                returnme = ''
                for line in log:
                    returnme += line
                return '<pre>' + returnme + '</pre>'
            else:
                flash('Log file for project "' + p.getName() + '" is not available!')
        else:
            flash('Project not found')
    return redirect('list')
    
@fApp.route('/download')
@login_required
def download():
    pid = request.args.get('id')
    if pid:
        p = Project.get(pid)
        if p:
            result = p.getResultPath()
            if result:
                return send_file(result, as_attachment=True, attachment_filename=p.getName() + os.path.splitext(result)[1])
            else:
                flash('Download for project "' + p.getName() + '" is not available!')
        else:
            flash('Project not found')
    return redirect('list')

@fApp.route('/logout')
@login_required
def logout():
    flash('Bye!')
    logout_user()
    return redirect(url_for('login'))

@fApp.route('/list')
@login_required
def list():
    if not len(projects):
        flash('No projects found, please upload one!')
        return redirect(url_for('upload'))
    autoreload = 0
    for p in projects:
        if p.getStatus() == app.config.STATUS_QUEUED or p.getStatus() == app.config.STATUS_WORKING:
            autoreload = 10
            break
    return render_template('list.html', title='LIST', projects=projects, autoreload=autoreload)
    
@fApp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'id' in request.form:
            project = Project(request.form['id'], app.config.STATUS_UPLOAD)
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
                    project.setStatus(app.config.STATUS_QUEUED)
                except Exception as e:
                    return str(e), 500
                projects.append(project)
                logging.info('Upload complete for project id ' + project.getId())
                return 'OK'
            else:
                return 'Incomplete upload/finish request!', 400
        else:
            return 'Incomplete upload/finish request!', 400
    return render_template('upload.html', title='UPLOAD')
