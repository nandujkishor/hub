import os
import qrcode
from functools import wraps
import datetime
from flask import render_template, flash, redirect, request, url_for, jsonify
from app import app, db, api
from app.models import User, Staff
from config import Config
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

#normal user authorization
def authorize(request):
    def normauth_with_request(func):
        @wraps(func)
        def nd_view(*args, **kwargs):
            try:
                auth_t = auth_token(request)
                if auth_t:
                    resp = User.decode_auth_token(auth_t)
                    if not isinstance(resp, str):
                        u = User.query.filter_by(vid=resp).first()
                        if u is None:
                            responseObject = {
                                'status':'fail',
                                'message':'Go check your DB'
                            }
                            return jsonify(responseObject)
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
                # return 401
            return func(u, *args, **kwargs)
        return nd_view
    return normauth_with_request

#authorize staff
def authorizestaff(request, team="all", level=4):
    def auth_with_request(func):
        @wraps(func)
        def d_view(*args, **kwargs):
            try:
                auth_t = auth_token(request)
                if auth_t:
                    resp = User.decode_auth_token(auth_t)
                    if not isinstance(resp, str):
                        print("Authorization staff for  ", resp)
                        u = User.query.filter_by(vid=resp).first()
                        if u is None:
                            responseObject = {
                                'status':'fail',
                                'message':'Go check your DB'
                            }
                            return jsonify(responseObject)
                        if u.super():
                            return func(*args, **kwargs)
                        st = Staff.query.filter_by(vid=u.vid, team="web").first()
                        if st is not None:
                            if st.level < level:
                                responseObject = {
                                    'status':'fail',
                                    'message':'Not enough clearance levels for web'
                                }
                                return jsonify(responseObject)
                            return func(*args, **kwargs)
                        if team=="all":
                            st = Staff.query.filter_by(vid=u.vid).order_by(level).first()
                            if st is None:
                                responseObject = {
                                    'status':'fail',
                                    'message':'Not staff'
                                }
                                return jsonify(responseObject)
                            elif st.level < level:
                                responseObject = {
                                    'status':'fail',
                                    'message':'No clearance in any team'
                                }
                                return jsonify(responseObject)
                            return func(*args, **kwargs)
                        st = Staff.query.filter_by(vid=u.vid, team=team).first()
                        if st == None:
                            responseObject = {
                                'status':'fail',
                                'message':'Not staff'
                            }
                            return jsonify(responseObject)
                        elif st.level < level:
                            responseObject = {
                                'status':'fail',
                                'message':'Not enough permissions'
                            }
                            return jsonify(responseObject)
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
            return func(*args, **kwargs)
        return d_view
    return auth_with_request

@farer.route('/auth/user')
class user_auth(Resource):
    # API Params: JSON(idtoken, [Standard])
    # Standard: User IP, Sender ID
    # Returns: JWT
    # Authorizes a new / returning user and provides the Token
    @api.doc(params={
        'idtoken':'Identification token from google',
    })
    def post(self):
        print(request.args)
        print(request.get_json())
        data = request.get_json()
        token = data.get('idtoken')
        print(token)
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request())
            print("DEBUGGING = ", idinfo['iss'])
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            userid = idinfo['sub']
        except Exception as e:
            print(e)
            # flog = FarerLog(action="Login", point=point, status="error", message="ValueError - wrong issuer")
            # Send email on the error
            print("Error encountered - ValueError - Wrong issuer")
            return "Error encountered - ValueError - Wrong issuer"
        
        print(idinfo['email'])
        u = User.query.filter_by(id = userid).first()
        print(u)
        
        if u is None:
            try:
                u = User(id=userid,
                        email=idinfo.get('email'),
                        fname=idinfo.get('given_name'),
                        lname=idinfo.get('family_name'),
                        ppic=idinfo.get('picture'))
                # flog = FarerLog(vid=u.id, action="Register", point=point, ip=ip)
                db.session.add(flog)
                print("TRYING TO ADD TO DB = ", u)
                db.session.add(u)
                db.session.commit()
                # Send welcome email
                auth_token = u.encode_auth_token()
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully registered',
                    'auth_token': auth_token.decode()
                }
                print("RESPONOSE = ", responseObject)
                return jsonify(responseObject)
            except Exception as e:
                responseObject = {
                    'status': 'error',
                    'message': 'Error1 - Please try again'
                }
                print("Error", e)
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
        print("Auth token", auth_t)
        if auth_t:
            resp = User.decode_auth_token(auth_t)
            print("Decoded value", resp)
            if not isinstance(resp, str):
                print("RESP = ", resp)
                u = User.query.filter_by(vid=resp).first()
                if u is None:
                    responseObject = {
                        'status':'Fail',
                        'message':'User not logged in'
                    }
                    return jsonify(responseObject)
                
                print("U = ", u)

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

@farer.route('/user/details')
class farer_u_det(Resource):
    # Manages Details data (incoming)
    @api.doc(params={
        'fname':'First Name',
        'lname':'Last Name',
        'phno':'Phone No',
        'sex':'Sex',
        'detailscomp':'Personel details completed'
    })
    def put(self):
        try:
            auth_t = auth_token(request)
            if auth_t:
                resp = User.decode_auth_token(auth_t)
                if not isinstance(resp, str):
                    user = User.query.filter_by(vid=resp).first()
                    if user is not None:
                        if user.detailscomp is None:
                            inc = request.get_json()
                            user.fname = inc.get('fname')
                            user.lname = inc.get('lname')
                            user.phno = inc.get('phno')
                            user.sex = inc.get('sex')
                            user.detailscomp = True
                            db.session.commit()
                            responseObject = {
                                'status':'success',
                                'message':'Successfully completed addition of personel data'
                            }
                        else:
                            responseObject = {
                                'status':'failure',
                                'message':'Personel deatils added already'
                            }
                    else:
                        responseObject = {
                            'status':'failure',
                            'message':'Invalid User'
                        }
        except Exception as e:
            print(e)
            responseObject = {
                'status':'fail',
                'message':'Error occured'
            }
        return jsonify(responseObject)

@farer.route('/user/education')
class farer_u_edu(Resource):
    # Manages data incoming
    @api.doc(params={
        'course':'Course',
        'major':'Major',
        'college':'College',
        'institution':'Institution',
        'year':'Year',
        'educomp':'Education details completed'
    })
    def put(self):
        try:
            auth_t = auth_token(request)
            if auth_t:
                resp = User.decode_auth_token(auth_t)
                print(resp)
                if not isinstance(resp, str):
                    inc = request.get_json()
                    user = User.query.filter_by(vid=resp).first()
                    if user is not None:
                        if user.educomp is None:
                            user.course = inc.get('course')
                            user.major = inc.get('major')
                            user.college = inc.get('college')
                            user.institution = inc.get('institution')
                            user.year = inc.get('year')
                            user.educomp = True
                            db.session.commit()
                            responseObject = {
                                'status':'success',
                                'message':'Successfully completed addition of Educational Data'
                            }
                        else:
                            responseObject = {
                                'status':'failure',
                                'message':'Educational details added already'
                            }
                    else:
                        responseObject = {
                            'status':'failure',
                            'message':'Invalid User'
                        }
                    return jsonify(responseObject)
        except Exception as e:
            responseObject = {
                'status':'failure',
                'message':'Error Occured'
            }
            return jsonify(responseObject)


@farer.route('/user/list/detail')
class userslistd(Resource):
    # Params: Standard with Auth header
    # Access only for 4 and above
    def get(self):
        users = User.query.all()
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
        return jsonify(usej)

@farer.route('/user/list/short')
class userslistd(Resource):
    # Params: Standard with Auth header
    def get(self):
        users = User.query.all()
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
                # print(u)
                st = Staff.query.filter_by(vid=u.vid).all()
                roles = []
                for s in st:
                    roles.append({
                        'team':s.team,
                        'level':s.level
                    })
                return jsonify(roles)
    # Adds a staff profile to an existing account
    # Need sudo access to perform operation
    @api.doc(params={
        'vid':'Vidyut ID',
        'team':'Team Name',
        'level':'Level of the User'
    })
    def post(self):
        auth_t = auth_token(request)
        if auth_t:
            resp = User.decode_auth_token(auth_t)
            u = User.query.filter_by(vid=resp).first()
            req = request.get_json()
            if u.super():
                st = Staff.query.filter_by(vid=req.get('vid'), team=req.get('team')).first()
                if st is not None:
                    st.level = req.get('level')
                    db.session.commit()
                    responseObject={
                        'status':'success',
                        'message':'Upgraded Staff Level'
                    }
                    return jsonify(responseObject)
                else:
                    st = Staff(vid=req.get('vid'), team=req.get('team'), level=req.get('level'))
                    db.session.add(st)
                    db.session.commit()
                    responseObject={
                        'status':'success',
                        'message':'Upgraded to Staff'
                    }
                    return jsonify(responseObject)
    
#need to work on this
@farer.route('/registered/college')
class reg_coll(Resource):
    # Provides the list of colleges among registered users
    # Headers: Authorization
    @authorizestaff(request, "web", 4)
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

@farer.route('/user/contact')
class user_contact(Resource):
    def get(self):
        ent = request.get_json()
        print(ent)
        user = User.query.filter_by(vid=ent.get('vid')).first()
        responseObject = {
            'fname':user.fname,
            'lname':user.lname,
            'phno':user.phno
        }
        return jsonify(responseObject)

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