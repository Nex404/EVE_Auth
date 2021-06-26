from EVE import db, login_manager, bcrypt
from flask_login import UserMixin
from datetime import datetime
import time


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# but all model classes e.g. Mail, Transactions,
# clones, etc

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=100), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    # is_admin = db.Column(db.Boolean(), nullable=False, default=False)
    
    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
        
    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


class Character(db.Model):
    # our ID is the character ID from EVE API
    character_id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=False
    )
    character_owner_hash = db.Column(db.String(255))
    character_name = db.Column(db.String(200))

    # SSO Token stuff
    access_token = db.Column(db.String(4096))
    access_token_expires = db.Column(db.DateTime())
    refresh_token = db.Column(db.String(100))

    def get_id(self):
        """ Required for flask-login """
        return self.character_id

    def get_sso_data(self):
        """ Little "helper" function to get formated data for esipy security
        """
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_in': (
                self.access_token_expires - datetime.utcnow()
            ).total_seconds()
        }

    def update_token(self, token_response):
        """ helper function to update token data from SSO response """
        self.access_token = token_response['access_token']
        self.access_token_expires = datetime.fromtimestamp(
            time.time() + token_response['expires_in'],
        )
        if 'refresh_token' in token_response:
            self.refresh_token = token_response['refresh_token']


class skill(db.Model):
    skill_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=False
    )
    skill_name = db.Column(db.String(120))
    skill_category_name = db.Column(db.String(120))
    skill_category_id = db.Column(db.Integer)

    def __init__(self, id, name, category_name, category_id):
        self.skill_id = id
        self.skill_name = name
        self.skill_category_name = category_name
        self.skill_category_id = category_id 

class skill_abst():
    def __init__(self, name, category_name, skill_lvl):
        self.name = name
        self.category = category_name
        self.lvl = skill_lvl