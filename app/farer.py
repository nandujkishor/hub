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

@farer.route('/auth/user/')
class user_auth(Resource):
    # API Params: JSON(idtoken, [Standard])
    # Standard: IP, Sender ID
    # Returns: JWT
    # Authorizes a new / returning user and provides the Token
    def post(self):
        data = request.get_json()
        token = data.get('idtoken')
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request())
            print(idinfo)
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            userid = idinfo['sub']
        except:
            flog = FarerLog(action="Login", point=point, status="error", message="ValueError - wrong issuer")
            # Send email on the error
            print("Error encountered - ValueError - Wrong issuer")
            return "Error encountered - ValueError - Wrong issuer"
        print(idinfo['email'])
        u = User.query.filter_by(id = userid).first()
        print(u)
        if u is None:
            try:
                u = User(id=userid, email=idinfo.get('email'), fname=idinfo.get('given_name'), lname=idinfo.get('family_name'), ppic=idinfo.get('picture'))
                flog = FarerLog(uid=u.id, action="Register", point=point, ip=ip)
                db.session.add(flog)
                db.session.add(u)
                db.session.commit()
                # Send welcome email
                auth_token = u.encode_auth_token()
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully registered',
                    'auth_token': auth_token.decode()
                }
                return jsonify(responseObject), 201
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Error - Please try again'
                }
                # Send mail on the error
                return jsonify(responseObject), 401
        else:
            try:
                auth_token = u.encode_auth_token()
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully logged in',
                    'auth_token': auth_token.decode()
                }
                return jsonify(responseObject), 201
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Error - Please try again'
                }
                # Send mail on the error
                return jsonify(responseObject), 401
        return "Other worldly!"

@farer.route('/user/')
class userdata(Resource):
    def get(self):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                u = User.query.filter_by(id=resp).first()
                responseObject = {
                    'status': 'success',
                    'data': {
                        'user_id': user.id,
                        'email': user.email,
                        'time_created': user.time_created
                    }
                }
                return make_response(jsonify(responseObject)), 200
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 401
