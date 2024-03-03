from app import app
from models.event_models import Event, User
from flask import session
from unittest.mock import patch, MagicMock
import pytest

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            yield client

# simple index
def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Just login or register to view your organized events or participated ones at single place.' in response.data

# index with session
def test_index_with_session(client):
    with client.session_transaction() as sess:
        sess['username'] = 'test_username'
        sess['user_id'] = 'test_user_id'
    
    response = client.get('/')
    assert response.status_code == 302
    assert b'Redirecting...' in response.data

# Read event page
@patch('controllers.event_controllers.Event.query')
@patch('controllers.event_controllers.User.query')
def test_events(mock_user_query, mock_event_query, client):
    
    # Mock the behavior of User.query.filter_by().first()
    mock_user = User(id='1', name='Test User',email='test@gmail.com',password='testtest',phone='12345',events_attended=[],events_organized=[])
    mock_user_query.filter_by.return_value.first.return_value = mock_user

    # Mock the behavior of Event.query.filter().all()
    mock_events_organized = Event(event_id=1, event_name='Event 2',event_description='test',event_start_date='2024-02-12 16:00',
                             event_end_date= '2024-02-12 19:00', event_location='Delhi',event_participants=[],event_organizer_id='1'
                              ,event_organizer_name ='Test User',event_feedback={}, event_rating={})

    mock_event_participated = Event(event_id=2, event_name='Event 2',event_description='test',event_start_date='2024-02-12 16:00',
                             event_end_date= '2024-02-12 19:00', event_location='Delhi',event_participants=[],event_organizer_id='1'
                              ,event_organizer_name ='Test User',event_feedback={}, event_rating={})
    mock_other_events = Event(event_id=3, event_name='Event 2',event_description='test',event_start_date='2024-02-12 16:00',
                             event_end_date= '2024-02-12 19:00', event_location='Delhi',event_participants=[],event_organizer_id='1'
                              ,event_organizer_name ='Test User',event_feedback={}, event_rating={})
    
    mock_event_query.filter_by.return_value.all.return_value = [mock_events_organized,mock_event_participated,mock_other_events]

    # Set user_id in session
    with client.session_transaction() as sess:
        sess['user_id'] = '1'
        sess['username'] = 'test'

    # Make a request to '/events'
    response = client.get('/events')

    # Check if the response contains expected data
    assert response.status_code == 200
    assert b'Your Organized Events' in response.data
    assert b'Other Events' in response.data
    assert b'Your Participated Events' in response.data

# Edit Event page get
@patch('controllers.event_controllers.Event.query')
def test_edit_events(mock_event_query, client):

    # Mock the behavior of Event.query.filter().all()
    mock_event = Event(event_id='1', event_name='Event 2',event_description='test',event_start_date='2024-02-12 16:00',
                             event_end_date= '2024-02-12 19:00', event_location='Delhi',event_participants=[],event_organizer_id='1'
                              ,event_organizer_name ='Test User',event_feedback={}, event_rating={})
    
    mock_event_query.filter_by.return_value.first.return_value = mock_event

    # Set user_id in session
    with client.session_transaction() as sess:
        sess['user_id'] = '1'
        sess['username'] = 'test'

    # Make a request to '/events'
    response = client.get('/editEvent/1')

    # Check if the response contains expected data
    assert response.status_code == 200
    assert b'Hi test, edit your' in response.data


# Create
def test_create_event(client):
    # Mock the behavior of User.query.filter_by().first()
    with patch('controllers.event_controllers.User.query') as mock_user_query:
        mock_user = User(id='1', name='Test User',email='test@gmail.com',password='testtest',phone='12345')
        mock_user_query.filter_by.return_value.first.return_value = mock_user

        # Mock the behavior of db.session.add() and db.session.commit()
        with patch('controllers.event_controllers.db.session.add') as mock_add, \
             patch('controllers.event_controllers.db.session.commit') as mock_commit, \
             patch('controllers.event_controllers.json') as mock_json:

            # Mock the dumps method to return a mock string
            mock_dumps = MagicMock()
            mock_dumps.return_value = '{"events_organized": []}'
            mock_json.dumps = mock_dumps

            # Mock the loads method to return an empty list
            mock_loads = MagicMock()
            mock_loads.return_value = []
            mock_json.loads = mock_loads

            # Set user_id in session
            with client.session_transaction() as sess:
                sess['user_id'] = '1'
                sess['username'] = 'Test User'

            # Mock the request data
            client.post_data =  {
                'eventName': 'Test Event',
                'description': 'Test description',
                'start_date': '2024-01-01T16:00',
                'end_date': '2024-01-02T15:00',
                'location': 'Test Location'
            }

            # Make a POST request to '/createEvent'
            response = client.post('/createEvent', data=client.post_data, follow_redirects=True)

            # Check if the event creation was successful
            assert response.status_code == 200
            assert mock_add.called
            assert mock_commit.called
            assert b'You have not organized any events yet. So, what are you waiting for' in response.data

# Edit post
def test_edit_post(client):
    with patch('controllers.event_controllers.Event.query') as mock_event_query:
        mock_event = Event(event_name='Event 2',event_description='test',event_start_date='2024-02-12 16:00',
                             event_end_date= '2024-02-12 19:00', event_location='Delhi')
    
        mock_event_query.filter_by.return_value.first.return_value = mock_event

        with patch('controllers.event_controllers.db.session.commit') as mock_commit:

            # Set user_id in session
            with client.session_transaction() as sess:
                sess['user_id'] = '1'
                sess['username'] = 'test'


            # Mock the request data
            client.post_data =  {
                    'eventName': 'Test Event',
                    'description': 'Test description',
                    'start_date': '2024-01-01T16:00',
                    'end_date': '2024-01-02T15:00',
                    'location': 'Test Location'
                }
            
            # Make a POST request to '/editEvent/1'
            response = client.post('/editEvent/1', data=client.post_data, follow_redirects=True)

            # asserting
            assert response.status_code == 200
            assert mock_commit.called
            assert b'Your Organized Events' in response.data