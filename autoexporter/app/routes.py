from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app
from app.user import User
from app.forms import LoginForm

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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/list')
@login_required
def list():
    # TODO: List current projects (queued, in progress, success, failure), Logout, Add project
    return render_template('list.html', title='LIST')
    
@app.route('/upload')
@login_required
def upload():
    # TODO: Add file, Add folder, Upload
    return render_template('upload.html', title='UPLOAD')
