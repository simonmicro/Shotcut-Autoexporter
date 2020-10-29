from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app
from app.models import User, STATUS_QUEUED, STATUS_WORKING, STATUS_SUCCESS, STATUS_FAILURE
from app.forms import LoginForm

projects = [
    {
        'name':'Queued',
        'progress':None,
        'status':STATUS_QUEUED
    },
    {
        'name':'In progress',
        'progress':0.6,
        'status':STATUS_WORKING
    },
    {
        'name':'Success',
        'progress':None,
        'status':STATUS_SUCCESS
    },
    {
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
        if not next_page or url_parse(next_page).netloc != '':
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
    if request.method == 'POST' and 'file' in request.files and 'path' in request.form and 'project' in request.form:
        flash('TODO: upload')
        return 'OK'
    # TODO: Add file, Add folder, Upload
    return render_template('upload.html', title='UPLOAD')
