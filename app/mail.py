import smtplib
from config import Config
from threading import Thread
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import render_template
from app.models import User

def send_core(smtpserver, user, recipient, msg):
    smtpserver.sendmail(user, recipient, msg.as_string())
    smtpserver.close()

def send_mail(sub, body, htmlbody, recipient):
    smtpserver = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
    msg = MIMEMultipart('alternative')
    msg['Subject'] = sub
    msg['From'] = Config.MAIL_DEFAULT_SENDER
    msg['To'] = recipient
    part1 = MIMEText(htmlbody, 'html')
    msg.attach(part1)

    Thread(target=send_core, args=(smtpserver, Config.MAIL_DEFAULT_SENDER, recipient, msg)).start()

def farer_welcome_mail(user):
    print("Sending welcome mail to " + user.fname)
    send_mail("Thank you for registering with Vidyut", 
            body="Your Vidyut ID is " + str(user.vid), 
            htmlbody=render_template('emails/welcome.html', user=user), 
            recipient=user.email
            )
    return "Okay!"

def wkreg_mail(user, workshop, regid, wdept):
    print("Sending Workshop registration mail to " + user.fname)
    send_mail("Workshop: "+ workshop.title + " during Vidyut'19 - registration successful", 
            body="Your Vidyut ID is " + str(user.vid),
            htmlbody=render_template('emails/workshops-reg.html', user=user, workshop=workshop, regid=regid, wdept=wdept),
            recipient=user.email
            )
    return "mail sent - hopefully"

def test_mail(user):
    print("Sending test mail")
    farer_welcome_mail(user)