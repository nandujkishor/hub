import os
import json
import datetime
from flask import render_template, flash, redirect, request, url_for, jsonify
from app import app, db, api
from app.farer import authorizestaff, authorize
from app.models import Workshops, Talks, Contests, Registrations, User, College
from app.mail import test_mail, sendcho, sendfas
from config import Config
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from flask_restplus import Resource

# @app.before_request
# def before_request():
#     print("Before req")

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', page="/home", uchange="")

@app.route('/mail/test')
@authorize(request)
def mailtest(u):
    print(request.get_data())
    test_mail(u)
    return "Sent"

# @app.route('/send/cho')
# def sendchoreo():
#     sendcho()
#     return "Okay"

# @app.route('/')

# @app.route('/send/fas')
# def sendfash():
#     sendfas()
#     return "Okay"

@api.route('/college/list/')
class college_list(Resource):
    def get(self):
        colleges = College.query.all()
        c = []
        for college in colleges:
            c.append({
                'id':college.id,
                'name':college.name,
                'district':college.district,
                'state':college.state
            })
        return jsonify(c)
