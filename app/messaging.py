import requests
import urllib
from app.models import User

def send_message(message, number):
    # 'ip':'10.0.0.139',
    payload = {
        'key':'vidyuth1908030559',
        'num':number,
        'msg':message,
        'ip':'10.0.0.139'
    }
    params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)
    r = requests.get('http://sms.amrita.ac.in/', params=params)
    print(r.url)

def transportation_message():
    # u = User.query.filter(college>5 | college==0).all()
    u = User.query.filter_by(vid=1).all()
    print(u)
    print("Count: ", len(u))
    message = "Vidyut transportation: Free shuttle buses will be available from 9 - 10 AM and PM from Kayankulam Railway station. For related queries contact:9847308706"
    print(len(message))
    for i in u:
        if u.phno is not None:
            print("Sending message to ", u.fname, u.phno)
            send_message(message, u.phno)

def general_message():
    # u = User.query.filter(college>5 | college==0).all()
    u = User.query.filter_by(vid=1).all()
    u.append(User.query.filter_by(vid=68).first())
    u.append(User.query.filter_by(vid=12).first())
    print(u)
    print("Count: ", len(u))
    message = "Vidyut Notification: Please make sure you carry your college issued ID cards with you. For notifications and schedule, install app http://bit.ly/vidyutapp"
    smessage = "Vidyut%20Notification:%20Please%20make%20sure%20you%20carry%20your%20college%20issued%20ID%20cards%20with%20you.%20For%20notifications%20and%20schedule,%20install%20app%20http://bit.ly/vidyutapp"
    print(len(message))
    for i in u:
        if i.phno is not None:
            print("Sending message to ", i.fname, i.phno)
            send_message(message, i.phno)