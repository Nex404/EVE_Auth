# -*- encoding: utf-8 -*-
import datetime

# -----------------------------------------------------
# Application configurations
# ------------------------------------------------------
DEBUG = True
SECRET_KEY = 'ChangeThisToBeSecure'
PORT = 'your port'
HOST = 'your host'

# -----------------------------------------------------
# SQL Alchemy configs
# -----------------------------------------------------
SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'

# -----------------------------------------------------
# ESI Configs
# -----------------------------------------------------
ESI_DATASOURCE = 'tranquility'  # Change it to 'singularity' to use the test server
ESI_SWAGGER_JSON = 'https://esi.tech.ccp.is/latest/swagger.json?datasource=%s' % ESI_DATASOURCE
ESI_SECRET_KEY = ''  # your secret key
ESI_CLIENT_ID = ''  # your client ID
ESI_CALLBACK = 'http://%s:%d/sso/callback' % (HOST, PORT)  # the callback URI you gave CCP
ESI_USER_AGENT = 'Change this so u can be identified by eve'


# ------------------------------------------------------
# Session settings for flask login
# ------------------------------------------------------
PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=30)

# ------------------------------------------------------
# DO NOT EDIT
# Fix warnings from flask-sqlalchemy / others
# ------------------------------------------------------
SQLALCHEMY_TRACK_MODIFICATIONS = True

# ------------------------------------------------------
# Registration Togen
# ------------------------------------------------------
REGISTRATION_TOKEN = 'use some string for registration'