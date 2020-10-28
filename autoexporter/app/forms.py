from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'autofocus': True})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')
