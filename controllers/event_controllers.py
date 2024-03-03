from flask import render_template, request, session, redirect, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models.event_models import db, User, Event, PasswordResetToken
from sqlalchemy.exc import OperationalError
import json
from flask_mail import Mail , Message
import os
import uuid

# Analyze
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
# to avoid RuntimeError: main thread is not in the main loop
matplotlib.use('Agg')

# local
# # Get the directory of the current file
# current_dir = os.path.dirname(__file__)

# # Get the full path to config.json by going up one directory
# config_file_path = os.path.abspath(os.path.join(current_dir, '..', 'config.json'))

# # reading from json
# with open(config_file_path, 'r') as file:
#     # this will be global
#     site_mail = json.load(file)['params']['gmail_username']

# prod 
site_mail = os.getenv('gmail_username')
# print(site_mail)

mail = Mail()

# index page
def index():
    try:
        if 'user_id' in session:
            return redirect(url_for('home', username=session['username'], user_id=session['user_id']))
        return render_template('index.html')
    except Exception as e:
        return render_template('views/something_wrong.html', error=e)

# home
def home():
    try:
        if 'user_id' in session:
            # print(username, user_id)
            # print(params)
            return render_template('views/home.html')
        flash('Please Login or Register first!')
        return redirect(url_for('index'))
    
    except Exception as e:
        return render_template('views/something_wrong.html', error=e)

# login
def login():
    try:
        if request.method == 'POST':
            user_email = request.form['username']
            password = request.form['password']

            user = User.query.filter_by(email=user_email).first()

            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['username'] = user.name
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid Credentials, try again!')
                return redirect('/')
    
    except Exception as e:
        return render_template('views/something_wrong.html', error=e)
        
# register
def register():
    try:
        if request.method == 'POST':
            name = request.form['username']
            email = request.form['email']
            phone = request.form['phone']
            password = request.form['password']

            # print(name, email, phone, password)

            # Check if user already exists
            if User.query.filter_by(email=email).first():
                flash('Email already exists. Please use a different email.', 'error')
                return redirect('/')

            # Hash the password before storing it
            password_hash = generate_password_hash(password)

            # Create a new user
            new_user = User(name=name, email=email, password=password_hash, phone=phone)
            db.session.add(new_user)
            db.session.commit()

            # redirecting
            user = User.query.filter_by(email=email).first()
            session['username'] = user.name
            session['user_id'] = user.id
            flash('You have been registered and logged in successfully', 'success')
            return redirect((url_for('home')))
    
    except Exception as e:
        return render_template('views/something_wrong.html', error=e)
    
# logout
def logout():
    try:
        session.pop('user_id')
        session.pop('username')
        flash('You have been logged out', 'success')
        return redirect('/')
    except Exception as e:
        return render_template('views/something_wrong.html', error=e)

# Reading Events
def events():
    # try:
        if 'user_id' in session:

            user_id = session['user_id']
            events_organized = Event.query.filter_by(event_organizer_id=user_id).all()
            event_participated = Event.query.filter(Event.event_participants.contains([user_id])).all()
            other_events = Event.query.filter(Event.event_organizer_id != user_id, ~Event.event_participants.contains([user_id])).all()

            # Avg Ratings
            ratings = {}
            for event in other_events:
                sum_ratings =0
                for value in event.event_rating.values():
                    sum_ratings+=int(value)
                if len(event.event_rating.values()):
                    rating_avg = sum_ratings/len(event.event_rating.values())
                    ratings[event.event_id] = rating_avg
                else:
                    ratings[event.event_id] = 0
                
            # local
            # event_participated = Event.query.filter(Event.event_participants.contains(user_id)).all() as we are storing in Text in Sqlite

            # print(events_organized, '\n')
            # print(event_participated, '\n')
            # print(type(user_id))
            # print(other_events, '\n')
            today_date = str(datetime.now().strftime("%Y-%m-%d %H:%M"))
            # print('2024-02-10 22:01' <= start_date)
            # print(str(today_date))
            return render_template('views/events.html', events_organized=events_organized, event_participated=event_participated, other_events=other_events, today_date = today_date, show=1, ratings=ratings)
        else:
            flash('Please Login or Register first!')
            return redirect(url_for('index'))
    
    # except Exception as e:
    #     return render_template('views/something_wrong.html', error=e)
    
# Create Event
def create_event():
    try:
        if 'user_id' in session and request.method == 'POST':

            # Creating user object
            user_id = session['user_id']
            user = User.query.filter_by(id=user_id).first()
            # print(user.name, user_id)
            # Formatting Date
            # start
            start_date = request.form["start_date"].split('T')
            start_date = (' ').join(start_date)
            # end
            end_date = request.form["end_date"].split('T')
            end_date = (' ').join(end_date)

            # Fetching data
            event_name = request.form['eventName']
            event_description = request.form['description']
            event_start_date = start_date
            event_end_date = end_date
            event_location = request.form['location']
            event_organizer_id = user_id
            event_organizer_name = session['username']

            # Create a new event
            new_event = Event(event_name = event_name, event_description=event_description, event_start_date=event_start_date,
                            event_end_date = event_end_date, event_location=event_location, event_organizer_id=event_organizer_id,
                            event_organizer_name = event_organizer_name)
            db.session.add(new_event)
            # commit the changes
            db.session.commit()

            # Adding events to the user event_organized list via serialization and desrialization
            current_events = json.dumps(user.events_organized)
            new_events = json.loads(current_events)
            new_events.append(new_event.event_id)
            
            # Final change
            user.events_organized = new_events
            db.session.commit()

            return redirect(url_for('events'))
    
    except Exception as e:
        return render_template('views/something_wrong.html', error=e)
    
# edit Events
def edit_event(event_id):
    try:
        if 'user_id' in session:

            if request.method == 'GET':
                # fetch out the event and User
                event = Event.query.filter_by(event_id=event_id).first()
                start_date_event = ("T").join(event.event_start_date.split(" "))
                end_date_event = ("T").join(event.event_end_date.split(" "))
                return render_template('views/edit_event.html', event = event ,start_date_event = start_date_event, end_date_event = end_date_event, show=0)
                
            else:

                # Formatting Date
                # start
                start_date = request.form["start_date"].split('T')
                start_date = (' ').join(start_date)
                # end
                end_date = request.form["end_date"].split('T')
                end_date = (' ').join(end_date)

                # Fetching data
                event_name = request.form['eventName']
                event_description = request.form['description']
                event_start_date = start_date
                event_end_date = end_date
                event_location = request.form['location']

                # fetch out the event and User
                event = Event.query.filter_by(event_id=event_id).first()

                # editing the values

                event.event_name = event_name
                event.event_description = event_description
                event.event_start_date = event_start_date
                event.event_end_date = event_end_date
                event.event_location = event_location

                # commit the changes
                db.session.commit()

                flash('Your event edited successfully!')        

                return redirect(url_for('events'))
        
        else:
            flash('Please Login or Register first!')
            return redirect(url_for('index'))
    
    except Exception as e:
        return render_template('views/something_wrong.html', error=e)
    
# Delete
def delete_event(event_id):
    try:
        if 'user_id' in session:

            user_id = session.get('user_id')

            # fetching details
            event = Event.query.filter_by(event_id=event_id).first()

            # from attended events we will delete for user backend
            participants_id = json.dumps(event.event_participants)
            catch_participants = json.loads(participants_id)
            if len(catch_participants):
                for paticipant in catch_participants:
                    participated_user = User.query.filter_by(id=paticipant).first()
                    events_attended_by_user = json.dumps(participated_user.events_attended)
                    this_event_catch = json.loads(events_attended_by_user)
                    this_event_catch.remove(event_id)
                    participated_user.events_attended = this_event_catch

            # Delete Event
            db.session.delete(event)

            # fetching user details to remove from organized events
            user = User.query.filter_by(id=user_id).first()

            # From organized events
            current_events = json.dumps(user.events_organized)
            remove_events = json.loads(current_events)
            # print(remove_events, event_id)
            # print(type(remove_events), type(event_id))
            remove_events.remove(event_id)

                
            # Final change
            user.events_organized = remove_events
            db.session.commit()

            flash('Event deleted successfully!')
            return redirect(url_for('events'))
        
        else:

            flash('Please Login or Register first!')
            return redirect(url_for('index'))
    
    except Exception as e:
        return render_template('views/something_wrong.html', error=e)

# Register for event
def register_for_event(event_id):
    try:
        if 'user_id' in session:

            user_id  = session.get('user_id')   
            # fetch data for user and event
            user = User.query.filter_by(id=user_id).first()
            event = Event.query.filter_by(event_id=event_id).first()
            organizer = User.query.filter_by(id= event.event_organizer_id).first()


            # registrating user with event
            attended_events = json.dumps(user.events_attended)
            add_attended_event = json.loads(attended_events)
            add_attended_event.append(event_id)
            user.events_attended = add_attended_event

            # adding user in event
            paticipants = json.dumps(event.event_participants)
            add_participants = json.loads(paticipants)
            add_participants.append(user_id)
            event.event_participants = add_participants

            # Commit the change
            db.session.commit()

            # mailing
            # Create a message object
            msg = Message('Event Registration Confirmation on EventHub', sender = site_mail, recipients=[user.email])
            msg_to_organizer= Message('User Confirmation for Event', sender = site_mail, recipients=[organizer.email])
            
            # Add content to the email body
            # msg.body = 'This is the plain text body of the email'
            # HTML body using a Jinja template and pass dynamic data
            html_body = render_template('views/email_template.html', recipient_name=user.name , event=event)
            msg.html = html_body

            # For Organizer
            message_for_organizer = f'This mail is regarding the confirmation of user for {event.event_name}. \n\nFollowing are the details of user:\
             \nName: {user.name} \nPhone: {user.phone} \n\nThank you\nEventify'
            msg_to_organizer.body = message_for_organizer

            # Send the message
            mail.send(msg)
            mail.send(msg_to_organizer)

            flash('You have been successfully registered for the event. You will shortly recieve a mail of confirmation')
            return redirect(url_for('events'))
        
        else:

            flash('Please Login or Register first!')
            return redirect(url_for('index'))
    
    except Exception as e:
        return render_template('views/something_wrong.html', error=e)

# Unregister for event
def cancel_event(event_id):
    try:
        if 'user_id' in session:

            user_id  = session.get('user_id')   
            # fetch data for user and event
            user = User.query.filter_by(id=user_id).first()
            event = Event.query.filter_by(event_id=event_id).first()
            organizer = User.query.filter_by(id= event.event_organizer_id).first()

            # canceling user with event
            attended_events = json.dumps(user.events_attended)
            remove_attended_events = json.loads(attended_events)
            remove_attended_events.remove(event_id)
            user.events_attended = remove_attended_events

            # removing user in event
            paticipants = json.dumps(event.event_participants)
            remove_event_particpants = json.loads(paticipants)
            remove_event_particpants.remove(user_id)
            event.event_participants = remove_event_particpants

            # Commit the change
            db.session.commit()

            # mailing
            # Create a message object
            msg = Message('Event Cancellation Confirmation on EventHub', sender = site_mail, recipients=[user.email])
            msg_to_organizer= Message('User Cancellation for Event', sender = site_mail, recipients=[organizer.email])
            
            # Add content to the email body
            # msg.body = 'This is the plain text body of the email'
            # For User
            message_for_user = f'This mail is for the confirmation that you have cancelled the participation in {event.event_name}. \nThank you \nEventify'
            msg.body = message_for_user

            # For Organizer
            message_for_organizer = f'This mail is regarding the cancellation of user for {event.event_name}. \n\nFollowing are the details of user:\
                \nName: {user.name} \nPhone: {user.phone} \n\nThank you\nEventify'
            msg_to_organizer.body = message_for_organizer

            # Send the message
            mail.send(msg)
            mail.send(msg_to_organizer)

            flash('You have been successfully cancelled for the event. You will shortly recieve a mail of confirmation')
            return redirect(url_for('events'))
        
        else:

            flash('Please Login or Register first!')
            return redirect(url_for('index'))
    
    except Exception as e:
        return render_template('views/something_wrong.html', error=e)


# Review and feedback
def rating_and_feedback(event_id):
    try:
        if 'user_id' in session:

            if request.method == 'GET':
                
                event = Event.query.filter_by(event_id=event_id).first()

                return render_template('views/review_feedback.html', event = event , show=0)
                
                
            else:
                user_id = session['user_id']
                rating = request.form['rating']
                feedback = request.form['feedback']

                event = Event.query.filter_by(event_id=event_id).first()

                # Event Rating dictionary
                events_rating = json.dumps(event.event_rating)
                events_rating_dict = json.loads(events_rating)
                events_rating_dict[user_id] = rating
                event.event_rating = events_rating_dict

                # Event Feedback dictionary
                events_feedback = json.dumps(event.event_feedback)
                events_feedback_dict = json.loads(events_feedback)
                print(events_feedback_dict)
                events_feedback_dict[user_id] = feedback
                event.event_feedback = events_feedback_dict

                db.session.commit()

                flash('You rated successfully!')
                return redirect(url_for('events'))
        
        else:

            flash('Please Login or Register first!')
            return redirect(url_for('index'))
    
    except Exception as e:
        return render_template('views/something_wrong.html', error=e)
    
# Delete review
def delete_reviews(event_id):
    try:
        if 'user_id' in session:
            user_id = session['user_id']
            event = Event.query.filter_by(event_id=event_id).first()

            # Deleting feedback
            events_feedback = json.dumps(event.event_feedback)
            events_feedback_dict = json.loads(events_feedback)
            if user_id in events_feedback_dict:
                del events_feedback_dict[user_id]
            event.event_feedback = events_feedback_dict

            # Deleting rating
            events_rating = json.dumps(event.event_rating)
            events_rating_dict = json.loads(events_rating)
            if user_id in events_rating_dict:
                del events_rating_dict[user_id]
            event.event_rating = events_rating_dict

            db.session.commit()

            flash('You successfully deleted your review!')
            return redirect(url_for('events'))
        
        else:

            flash('Please Login or Register first!')
            return redirect(url_for('index'))
    
    except Exception as e:
        return render_template('views/something_wrong.html', error=e)

# Analyze events route
def analyze_events():
    try:
        if 'user_id' in session:
            event_vs_rating()
            event_vs_participants()
            return render_template('views/analyze_data.html', show=0)
        
        else:

            flash('Please Login or Register first!')
            return redirect(url_for('index'))
    
    except Exception as e:
        return render_template('views/something_wrong.html', error=e)


# creating decorator to creat different analysis as flask wont allow main flask route to use as decorator or out of context
def analyze_events_data(func=[]):
    
    def wrapper():  
        #  using decorators analysis functions are given below
        plot_collection_x_y = func()
        x_axis = np.array(plot_collection_x_y[0])
        y_axis = np.array(plot_collection_x_y[1])

        plt.bar(x_axis,y_axis, color='#3da193')
        plt.xlabel(plot_collection_x_y[2])
        plt.ylabel(plot_collection_x_y[3])
        plt.title(plot_collection_x_y[4])

        # Customizing background color
        plt.gca().set_facecolor('#deab59')
        # Customizing grid lines
        # plt.grid(color='white', linestyle='-', linewidth=1)
        # Rotating x-axis labels for better visibility
        plt.xticks(rotation=30, ha='right') 

        # Define the folder path within the static directory
        static_folder = os.path.join('static', 'assets','plots')

        # Save the plot as an image file in the static folder
        plot_path = os.path.join(static_folder,plot_collection_x_y[5])

        # Automatically adjust subplot parameters for better layout
        plt.tight_layout()
        plt.savefig(plot_path)

        plt.close()
    
    return wrapper

# Defining Top-5 Events based on rating
@analyze_events_data
def event_vs_rating():
    event_data = Event.query.all()

    resulted_rating = {}

    for event in event_data:
        rating_sum=0
        for rating in event.event_rating.values():
            rating_sum+=int(rating)
        if len(event.event_rating.values()):
            rating_avg = rating_sum/len(event.event_rating.values())
            resulted_rating[event.event_name] = rating_avg
        else:
            resulted_rating[event.event_name] = 0
        
    resulted_rating= dict(sorted(resulted_rating.items(),key=lambda item:item[1], reverse = True))

    return [ list(resulted_rating.keys())[:5], list(resulted_rating.values())[:5],
                               'Event Name', 'Ratings', 'Top-5 Events as per Ratings', 
                               'event_ratings.png']

# Event vs Participants analysis by using decorator
@analyze_events_data
def event_vs_participants():
    event_data = Event.query.all()

    event_participation={event.event_name : len(event.event_participants) for event in event_data}
        
    event_participation= dict(sorted(event_participation.items(),key=lambda item:item[1], reverse = True))

    return [ list(event_participation.keys())[:5], list(event_participation.values())[:5],
                               'Event Name', 'Number of Participants', 'Top-5 Events as per Participation', 
                               'event_participations.png']

#forgot password
def forgot_password():
    # try:
        if request.method == 'POST':
            email = request.form['pass_email']
            user = User.query.filter_by(email=email).first()
            # print(user)
            if user:
                check_its_present = PasswordResetToken.query.filter_by(user_id=user.id).first()
                # print(check_its_present)

                if check_its_present:
                    # remove token_data
                    db.session.delete(check_its_present)
                    db.session.commit()
                    flash('New Link sent!')

                token = str(uuid.uuid4())

                reset_token= PasswordResetToken(user_id=user.id,token=token)

                db.session.add(reset_token)
                db.session.commit()

                reset_link= url_for('reset_password', token=token, _external= True)

                message = f'Here is your password reset link: {reset_link} \n This link is valid for next 15 minutes only. \n\n Thanks \nEVENTIFY Team'
                msg = Message('EVENTIFY: Password Reset', sender = site_mail, recipients=[user.email])
                msg.body= message

                mail.send(msg)
                
                flash('Kindly check your mail and reset your password.')
                return redirect(url_for('index'))
            
            else:
                flash('No user found, kindly check your email id.')
                return redirect(url_for('forgot_password'))

        return render_template('views/forgot_password.html')
    
    # except Exception as e:
    #     return render_template('views/something_wrong.html', error=e)

# reset password
def reset_password(token):
    try:
        token_data= PasswordResetToken.query.filter_by(token=token).first()
        # print(token_data.expiration_at)
        if token_data and token == token_data.token  and (token_data.expiration_at > datetime.utcnow()):
            if request.method == 'POST':
                new_password = request.form['password_update']
                user = User.query.filter_by(id= token_data.user_id).first()
                user.password = generate_password_hash(new_password)

                # remove token_data
                db.session.delete(token_data)

                db.session.commit()

                flash('Your password changed, try login now.')
                return redirect(url_for('index'))

            return render_template('views/reset_password.html', token= token)
        else:
            if token_data:
                db.session.delete(token_data)
                db.session.commit()
            return render_template('views/404_error.html')

    except Exception as e:
        return render_template('views/something_wrong.html', error=e)


# catch all other non-defined routes error
def handle_404(e):
    print(e)
    # error= OperationalError('SSL connection has been closed unexpectedly')
    # for i in error:
    #     print(i)
    # if 'SSL connection has been closed unexpectedly' in e:
    #     return render_template('views/something_wrong.html', error=e)
    return render_template('views/404_error.html')





