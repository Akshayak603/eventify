from flask import Flask

from models.event_models import db

from controllers.event_controllers import index, home, login, register, logout, events, create_event,edit_event, delete_event, register_for_event, mail, rating_and_feedback, delete_reviews, analyze_events, handle_404, forgot_password, reset_password, cancel_event

from dotenv import load_dotenv

import os

load_dotenv()
# local
# # reading from json
# with open('config.json', 'r') as file:
#     # this will be global
#     params = json.load(file)['params']

# prod
params={'local_uri':'','prod_uri':'','secret_key':'', 'gmail_username': '','gmail_pass': ''}

for key in params.keys():
    params[key]= os.getenv(key)

# print(params)

# local server boolean
local_server = False
# params['local_server']
# instance of flask app
app = Flask(__name__)

# secret key for session
app.secret_key = params['secret_key']

# connecting to db
if local_server:
    # print('hello local')
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
    # print('hello prod')
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]

# instance of SqlAlchemy for this app
db.init_app(app)

# Creating tables if they are not present using app_context to avoid outside error
with app.app_context():
    db.create_all()

# Mail
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail_username'],
    MAIL_PASSWORD = params['gmail_pass']
)

# Initialize Flask-Mail with the Flask application instance
mail.init_app(app)


# Index
app.route('/')(index)

# Entry Home
app.route('/home')(home)

# Login
app.route('/login', methods=['POST'])(login)

# Register
app.route('/register', methods=['POST'])(register)

# logout
app.route('/logout', methods=['GET'])(logout)

# Read
app.route('/events', methods=['GET'])(events) 
    
# Create
app.route('/createEvent',methods=['POST'])(create_event)

# Edit
app.route('/editEvent/<event_id>',methods=['GET','POST'])(edit_event)

# Delete
app.route('/delete/<event_id>', methods=['GET'])(delete_event)

# Registration for event
app.route('/registerEvent/<event_id>',methods=['GET'])(register_for_event)

# Cancellation for event
app.route('/cancelEvent/<event_id>',methods=['GET'])(cancel_event)

# Rating and feedback
app.route('/ratefeed/<event_id>', methods=['GET','POST'])(rating_and_feedback)

# Delete Review
app.route('/delete/review/<event_id>',methods=['GET'])(delete_reviews)

# Analyzer
app.route('/analyzeEvents',methods=['GET'])(analyze_events)

# Forgot password
app.route('/forgotpassword', methods=['GET','POST'])(forgot_password)

# reset password
app.route('/resetpassword/<token>',methods=['GET','POST'])(reset_password)

# all other roots or exception where its not found
app.register_error_handler(Exception,handle_404)

