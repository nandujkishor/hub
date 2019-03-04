import smtplib
from config import Config
from threading import Thread
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
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

def ctreg_mail(user, contest, regid, cdept):
    print("Sending contest mail")
    send_mail("Contest: "+ contest.title + " during Vidyut'19 - registration successful",
            body="Your Vidyut ID is " + str(user.vid),
            htmlbody=render_template('emails/contest-reg.html', user=user, contest=contest, regid=regid, wdept=cdept),
            recipient=user.email
            )
    return "mail sent - hopefully"

def ctregteamleader_mail(user, contest, registration, cdept):
    print("Sending contest mail")
    send_mail("Contest: "+ contest.title + " during Vidyut'19 - registration successful (team leader)",
            body="Your Vidyut ID is " + str(user.vid),
            htmlbody=render_template('emails/contest-team-reg.html', user=user, contest=contest, registration=registration, wdept=cdept),
            recipient=user.email
            )
    return "mail sent - hopefully"

def ctregteammember_mail(user, contest, registration, cdept):
    print("Sending contest mail")
    send_mail("Successfully joined team for Contest: "+ contest.title + " during Vidyut'19",
            body="Your Vidyut ID is " + str(user.vid),
            htmlbody=render_template('emails/contest-team-reg-member.html', user=user, contest=contest, registration=registration, wdept=cdept),
            recipient=user.email
            )
    return "mail sent - hopefully"

def addon_pur(user, title, purid, count):
    print("Sending addon purchase mail to " + user.fname)
    send_mail("Addon: "+ title + " purchase successful - Vidyut'19",
            body="Thank you for the purchase. VID: " + str(user.vid),
            htmlbody=render_template('emails/addon-purchase.html', user=user, title=title, purid=purid, count=count),
            recipient=user.email
            )
    return "mail sent - hopefully"

def error_mail(user, point, ip='0', time=datetime.datetime.now):
    print("Sending error mail")
    send_mail("Error occured: "+ title + " purchase successful - Vidyut'19", 
            body="Thank you for the purchase. VID: " + str(user.vid),
            htmlbody=render_template('emails/error.html', user=user, point=point, purid=purid),
            recipient=ambtestingmaster@gmail.com
            )
    return "mail sent - hopefully"

def send_spam(content):
    print("Sending spam mail")
    send_mail("Pay test",
            body="Pay test",
            htmlbody=render_template('emails/anycontent.html', content=content),
            recipient='nandujkishor1@gmail.com'
            )
    return "mail sent - hopefully"

def test_mail(user):
    print("Sending test mail")
    farer_welcome_mail(user)