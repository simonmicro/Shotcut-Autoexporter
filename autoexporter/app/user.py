from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self):
        # TEMP generate here the login pwd hash
        self.pwdhash = generate_password_hash('password42')
        self.id = 42
        
    def check_password(self, pwd):
        return check_password_hash(self.pwdhash, pwd)
