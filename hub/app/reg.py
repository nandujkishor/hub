import os
import datetime
import random, string
import werkzeug.security
from flask import render_template, flash, redirect, request, url_for, jsonify
from app import app, db, api
from app.models import User, Registrations
from app.farer import auth_token
from config import Config
# from app.forms import
# from app.models import
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from flask_restplus import Resource, Api
from google.oauth2 import id_token
from google.auth.transport import requests

reg = api.namespace('reg', description="Registration management")

@reg.route('/workshop/<int:wid>')
class workshop_reg(Resource):
    # API Params: JSON(Authorization, [Standard])
    # Standard: IP, Sender ID
    # Returns: JSON(Registration state)
    def get(self, wid):
        auth_header = auth_token(request)
        try:
            u = User.query.filter_by(vid = User.decode_auth_token(auth_header)).first()
            w = Registrations.query.filter_by(vid = u.vid, wid=wid)
            if w is None:
                responseObject = {
                    'state':'success',
                    'sub':0
                }
                return jsonify(responseObject), 201 #Not Registered
            else:
                responseObject = {
                    'state':'success',
                    'sub':1
                }
                return jsonify(responseObject), 201 #Registered
        except Exception as e:
            responseObject = {
                'state':'fail',
                'message':'Error occured'
            }
            return jsonify(responseObject), 401

    # API Params: JSON(idtoken, [Standard])
    # Standard: IP, Sender ID
    # Returns: JSON
    # Registers the user to a workshop
    def post(self, wid):
        data = request.get_json()
        auth_header = auth_token(request)
        try:
            u = User.query.filter_by(vid = User.decode_auth_token(auth_header)).first()
            reglist = Registrations.query.filter_by(wid = wid).all()
            workshop = Workshop.query.filter_by(wid = wid).first()
            if (count(reglist) >= workshop.seats):
                responseObject = {
                    'status':'Fail',
                    'message':'Slot unavailable'
                }
                return jsonify(responseObject), 401
            else:
                regis = Registrations(vid=u.vid, cat=1, eid=wid)
                responseObject = {
                    'status':'Success',
                    'message':'Added to queue'
                }
                return jsonify(responseObject), 201
        except Exception as e:
            print(e)
            # Send mail
            responseObject = {
                'status':'Fail',
                'message':'Error occured - exception'
            }
            return jsonify(responseObject), 401


@reg.route('/contest/<int:wid>')
class contest_reg(Resource):
    # API Params: JSON(Authorization, [Standard])
    # Standard: IP, Sender ID
    # Returns: JSON(Registration state)
    def get(self, wid):
        auth_header = auth_token(request)
        try:
            u = User.query.filter_by(vid = User.decode_auth_token(auth_header)).first()
            w = Registrations.query.filter_by(vid = u.vid,tid=u.tid, wid=wid)
            if w is None:
                responseObject = {
                    'state':'success',
                    'sub':0
                }
                return jsonify(responseObject), 201 #Not Registered
            else:
                responseObject = {
                    'state':'success',
                    'sub':1
                }
                return jsonify(responseObject), 201 #Registered
        except Exception as e:
            responseObject = {
                'state':'fail',
                'message':'Error occured'
            }
            return jsonify(responseObject), 401

    # API Params: JSON(idtoken, [Standard])
    # Standard: IP, Sender ID
    # Returns: JSON
    # Registers the user to a workshop
    def post(self, wid):
        data = request.get_json()
        auth_header = auth_token(request)
        try:
            u = User.query.filter_by(vid = User.decode_auth_token(auth_header)).first()
            if data.get_status() is 0:  #Register Team
                team_id = werkzeug.security.pbkdf2_hex(vid,salt= vid ,iterations=50000, keylen=5, hashfunc=None)
                regis = Registrations(vid=u.vid, cat=1,tid=team_id, eid=wid , team_size=1)
                responseObject = {
                    'status':'Success',
                    'message':'Added to queue'
                }
                return jsonify(responseObject), 201
            else:                       #Join Team
                c = Contests.query.filter_by(id = u.eid)
                if c.team_limit >= Registrations.query.filter_by(vid = u.vid, wid=wid,tid=data.get_tid()).count():
                    t = Registrations.query.filter_by(vid = u.vid, wid=wid,tid=data.get_tid())
                    if t is None:
                        responseObject = {
                        'state':'Fail',
                        'message':'Invalid team id'
                        }
                        return jsonify(responseObject), 401
                    else:
                        regis = Registrations(vid=u.vid, cat=1,tid=data.get_tid(), eid=wid)
                        responseObject = {
                        'status':'Success',
                        'message':'Added to queue'
                        }
                        return jsonify(responseObject), 201
                else:
                    responseObject = {
                    'state':'Fail',
                    'message':'Team Full'
                    }
                    return jsonify(responseObject), 401

        except Exception as e:
            print(e)
                                        # Send mail
            responseObject = {
                'status':'Fail',
                'message':'Error occured - exception'
            }
            return jsonify(responseObject), 401