import os
import datetime
from flask import render_template, flash, redirect, request, url_for, jsonify
from app import app, db, api
from app.models import User, Staff
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
        auth_token = auth_header.split(" ")[0]
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
                print(resp)
                u = User.query.filter_by(vid=resp).first()
                print(u)
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
                return jsonify(responseObject)
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return jsonify(responseObject)
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return jsonify(responseObject)

@farer.route('/user/count')
class usercount(Resource):
    def get(self):
        u = User.query.all()
        responseObject = {
            'status':'success',
            'sub':len(u)
        }
        return jsonify(responseObject)

@farer.route('/staff')
class StaffAPI(Resource):
    def get(self):
        auth_t = auth_token(request)
        if auth_t:
            resp = User.decode_auth_token(auth_t)
            if not isinstance(resp, str):
                print(resp)
                u = User.query.filter_by(vid=resp).first()
                print(u)
                st = Staff.query.filter_by(vid=resp).all()
                roles = []
                for s in st:
                    roles.append({
                        'team':s.team,
                        'level':s.level
                    })
                return jsonify(st)
                # Returns empty list

    # Adds a staff profile to an existing account
    # Need sudo access to perform operation
    def post(self):
        auth_t = auth_token(request)
        if auth_t:
            resp = User.decode_auth_token(auth_t)
            u = User.query.filter_by(vid=resp).first()
            req = request.get_json()
            if u.super():
                st = Staff.query.filter_by(vid=req.get('vid'), team=req.get('team'))
                if st is not None:
                    st.level = req.get('level')
                else:
                    st = Staff(vid=req.get('vid'), team=req.get('team'), level=req.get('level'))

@farer.route('/user/list/detail')
class userslistd(Resource):
    # Params: Standard with Auth header
    # Access only for 4 and above
    def get(self):
        users = Users.query.all()
        usej = []
        for u in users:
            usej.append({
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
            })
        return jsonify(users)

@farer.route('/user/list/short')
class userslistd(Resource):
    # Params: Standard with Auth header
    def get(self):
        users = Users.query.all()
        usej = []
        for u in users:
            usej.append({
                'vid':u.vid,
                'email':u.email,
                'fname':u.fname,
                'lname':u.lname,
                'ppic':u.ppic,
                'detailscomp':u.detailscomp,
                'educomp':u.educomp,
                'time_created':u.time_created,
                'lastseen':u.lastseen
            })
        return jsonify(usej)

@farer.route('/user/education')
class farer_u_edu(Resource):
    # Manages data incoming
    def put(self):
        # Requires JSON Data
        try:
            auth_t = auth_token(request)
            if auth_t:
                resp = User.decode_auth_token(auth_t)
                if not isinstance(resp, str):
                    print(resp)
                    u = User.query.filter_by(vid=resp).first()
                    print(u)
                else:
                    responseObject = {
                        'status':'fail',
                        'message':'Authorization failure:C1'
                    }
                    return jsonify(responseObject)
            else:
                responseObject = {
                    'status':'fail',
                    'message':'Authorization failure:C2'
                }
                return jsonify(responseObject)
        except Exception as e:
            print(e)
            # Send mail on the exception
            return 401
        user = User.query.filter_by(id=resp).first()
        user.course = form.course.data
        user.major = form.major.data
        user.college = form.college.data
        user.institution = form.institution.data
        user.year = form.year.data
        user.educomp = True
        db.session.commit()
        responseObject = {
            'status':'success',
            'message':'Successfully completed addition of Data'
        }
        return jsonify(responseObject)

@farer.route('/user/details')
class farer_u_edu(Resource):
    # Manages Details data (incoming)
    def put(self):
        user = User.query.filter_by(id=current_user.id).first()
        user.fname = form.fname.data
        user.lname = form.lname.data
        user.phno = form.phno.data
        user.sex = form.sex.data
        user.detailscomp = True
        db.session.commit()
        responseObject = {
            'status':'success',
            'message':'Successfully completed addition of Data'
        }
        return jsonify(responseObject)

@farer.route('/registered/college')
class reg_coll(Resource):
    # Provides the list of colleges among registered users
    # Headers: Authorization
    def get(self):
        colleges = User.query.with_entities(User.college).distinct().all()
        clist = []
        for c in colleges:
            clist.append({
                'id':college.id,
                'name':college.name,
                'district':college.district,
                'state':college.state
            })
        return jsonify(clist)

@farer.route('/registered/college/count')
class reg_coll_count(Resource):
    # Provides the count of colleges with registered users
    def get(self):
        colleges = User.query.with_entities(User.college).distinct().all()
        responseObject = {
            'status':'success',
            'sub':len(colleges)
        }
        return jsonify(responseObject)

