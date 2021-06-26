from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from EVE.models import Character, User
import EVE.config as config

class CharForm(FlaskForm):
    char_choices = []
    for char in Character.query.all():
        id = char.character_id
        name = char.character_name
        char_choices.append((id, name))
    
    char = SelectField("Character", choices=char_choices)
    
    options = SelectField("Option", choices=[("M", "Mail"), ("W", "Wallet"), ("S", "Skills"), ("SQ", "Skillquere"), ("BM", "Bookmarks"), ("CL", "Clones"), ("C", "Contacts"), ("CR", "Contracts"), ("L", "Location")])


class RegisterForm(FlaskForm):
    
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a diffrent one.')
    
    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email Address already exists! Please use a diffrent one.')

    def validate_registration_token(self, registration_token_to_check):
        if str(registration_token_to_check) == str(config.REGISTRATION_TOKEN):
            raise ValidationError('Registrationtoken does not exists.')
        
        
    username = StringField(label='Username:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='E-Mail Adresse:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Passwort:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Bestätige Passwort:', validators=[EqualTo('password1'), DataRequired()])
    registration_token = StringField(label='Registration Token:', validators=[DataRequired()])
    submit = SubmitField(label='Registrieren')
    
    
class LoginForm(FlaskForm):
    username = StringField(label='Username:', validators=[DataRequired()])
    password = StringField(label='Passwort:', validators=[DataRequired()])
    submit = SubmitField(label='Einloggen')