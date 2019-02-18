import os
import datetime
from flask import render_template, flash, redirect, request, url_for, jsonify
from app import app, db, api
from app.models import User
from config import Config
# from app.forms import
# from app.models import
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from flask_restplus import Resource, Api
from google.oauth2 import id_token
from google.auth.transport import requests

farer = api.namespace('farer', description="Farer management")

def auth_token(request):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        auth_token = ''
    return auth_token

@farer.route('/auth/user')
class user_auth(Resource):
    # API Params: JSON(idtoken, [Standard])
    # Standard: User IP, Sender ID
    # Returns: JWT
    # Authorizes a new / returning user and provides the Token
    def post(self):
        print(request.args)
        print(request.get_json())
        print(request.form)
        data = request.get_json()
        token = data.get('idtoken')
        print(token)
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request())
            print(idinfo)
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            userid = idinfo['sub']
        except:
            # flog = FarerLog(action="Login", point=point, status="error", message="ValueError - wrong issuer")
            # Send email on the error
            print("Error encountered - ValueError - Wrong issuer")
            return "Error encountered - ValueError - Wrong issuer"
        print(idinfo['email'])
        u = User.query.filter_by(id = userid).first()
        print(u)
        if u is None:
            try:
                u = User(id=userid, email=idinfo.get('email'), fname=idinfo.get('given_name'), lname=idinfo.get('family_name'), ppic=idinfo.get('picture'))
                # flog = FarerLog(uid=u.id, action="Register", point=point, ip=ip)
                # db.session.add(flog)
                db.session.add(u)
                db.session.commit()
                # Send welcome email
                auth_token = u.encode_auth_token()
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully registered',
                    'auth_token': auth_token
                }
                return jsonify(responseObject)
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Error1 - Please try again'
                }
                print(e)
                # Send mail on the error
                return jsonify(responseObject)
        else:
            try:
                auth_token = u.encode_auth_token()
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully logged in',
                    'auth_token': auth_token.decode()
                }
                return jsonify(responseObject)
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Error2 - Please try again'
                }
                print(e)
                # Send mail on the error
                return jsonify(responseObject)
        return "Other worldly!"

    # API Params: JSON(Auth header, [Standard])
    # Standard: IP, Sender ID
    # Returns: User info
    # Provides user information based on the header provided
    def get(self):
        auth_t = auth_token(request)
        if auth_t:
            resp = User.decode_auth_token(auth_t)
            if not isinstance(resp, str):
                u = User.query.filter_by(id=resp).first()
                responseObject = {
                    'status': 'success',
                    'data': {
                        'vid':u.vid,
                        'email':u.email,
                        'fname':u.fname,
                        'lname':u.lname,
                        'ppic':u.ppic,
                        'course':u.course,
                        'major':u.major,
                        'sex':u.sex,
                        'year':u.year,
                        'college':u.college,
                        'institution':u.institution,
                        'school':u.school,
                        'phno':u.phno,
                        'detailscomp':u.detailscomp,
                        'educomp':u.educomp,
                        'time_created':u.time_created,
                        'lastseen':u.lastseen
                    }
                }
                return jsonify(responseObject), 200
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return jsonify(responseObject), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return jsonify(responseObject), 401