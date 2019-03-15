import requests
from app.models import User

def send_message(message, number):
    # 'ip':'10.0.0.139',
    payload = {
        'key':'vidyuth1908030559',
        'num':number,
        'msg':message
    }
    r = requests.get('http://sms.amrita.ac.in/', data=payload)
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