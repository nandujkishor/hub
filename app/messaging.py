import requests
import urllib
from app.models import User
from app import db

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
    u = User.query.filter(User.college==0).filter(User.farer!=None).all()
    u.extend(User.query.filter(User.college > 5).filter(User.farer!=None).all())
    # u = User.query.filter_by(vid=1).all()
    # u.append(User.query.filter_by(vid=68).first())
    # u.append(User.query.filter_by(vid=12).first())
    print(u)
    print("Count: ", len(u))
    message = "Non-Amritapuri students are required to show Day-2 ticket + Vidyut ID + college ID for Choreonite entry. For more install Vidyut app http://bit.ly/vidyutapp"
    print(len(message))
    for i in u:
        if i.phno is not None:
            print("Sending message to ", i.fname, i.phno)
            send_message(message, i.phno)

def notpurchased():
    k = db.session.execute("select distinct(phno) from other_purchases, public.user where other_purchases.vid = public.user.vid and shirtdelivered = False and phno is not null").fetchall()
    # u = User.query.filter_by(vid=1).all()
    # u.append(User.query.filter_by(vid=68).first())
    # u.append(User.query.filter_by(vid=12).first())
    print(k)
    print("Count: ", len(k))
    message = "Please collect your proshows ticket from the sales counters in front of the college lobby. Sales end at 04.30pm. Install app from http://bit.ly/vidyutapp"
    print(len(message))
    for i in k:
        if i[0] is not None:
            print("Sending message to ", i[0])
            send_message(message, i)

def general_message_amr():
    u = User.query.filter(User.college<6).filter(User.college>0).all()
    # u = User.query.filter_by(vid=1).all()
    # u.append(User.query.filter_by(vid=68).first())
    # u.append(User.query.filter_by(vid=12).first())
    print(u)
    print("Count: ", len(u))
    message = "Amritapuri students are required to show Day-2 ticket + college ID for Choreonite entry. For more install Vidyut app http://bit.ly/vidyutapp"
    print(len(message))
    for i in u:
        if i.phno is not None:
            print("Sending message to ", i.fname, i.phno)
            send_message(message, i.phno)