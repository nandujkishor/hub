import os
import datetime
import requests
import json
from flask import render_template, flash, redirect, request, url_for, jsonify
from app import app, db, api
from app.models import User, AttendLog, Registrations, OtherPurchases
from config import Config
# from app.addons import addon_purchase
from app.farer import authorizestaff, authorize
from app.mail import checkin_welcome_mail
from flask_restplus import Resource, Api
from sqlalchemy.sql import func

attend = api.namespace('attend', description="Attend")

@attend.route('/entry')
class AtEntry(Resource):
    @api.doc(params={
        'vid':'VID in (int) format (without V19)',
        'farer':'Next farer available for the user'
    })
    @authorizestaff(request, "registration", 1)
    def post(u, self):
        d = request.get_json()
        user = User.query.filter_by(vid=d.get('vid')).first()
        if user.intime is not None:
            print("Error: user already checked in")
            responseObject = {
                'status':'fail',
                'message':'Student already checked in'
            }
            return jsonify(responseObject)
        anouser = User.query.filter_by(farer=d.get('farer')).first()
        if anouser is not None:
            responseObject = {
                'status':'fail',
                'message':'Farer already assigned. Check for duplicate.'
            }
            return jsonify(responseObject)
        try:
            # To be or not to be?
            user.intime = datetime.datetime.now()
            user.farer = d.get('farer')
            user.checkinby = u.vid
            db.session.commit()
        except Exception as e:
            print(e)
            responseObject = {
                'status':'fail',
                'message':'Error on database write',
                'error':str(e)
            }
            return jsonify(responseObject)
        try:
            checkin_welcome_mail(user)
        except Exception as e:
            print(e)
        responseObject = {
            'status':'success',
            'message':'User successfully linked to Farer'
        }
        return jsonify(responseObject)

@attend.route('/check/workshop')
class AttendCheck(Resource):
    # Checkin with Farer
    @api.doc(params={
        'farer':'farer',
        'id':'Workshop ID'
    })
    @authorizestaff(request, "workshops", 4)
    def post(u, self):
        try:
            data = request.get_json()
            user = User.query.filter_by(farer=data.get('farer')).first()
            reg = Registrations.query.filter_by(vid=user.vid, cat=1, eid=data.get('id')).first()
            if reg is None:
                responseObject = {
                    'status':'fail',
                    'message':'User not registered for the workshop'
                }
        except Exception as e:
            print(e)
            responseObject = {
                'status':'fail',
                'message':'DB error / input error',
                'error':str(e)
            }
            return jsonify(responseObject)
        try:
            a = AttendLog(vid=user.vid,
                        cat=1,
                        eid=data.get('id'),
                        by=u.vid
                        )
            db.session.add(a)
            db.session.commit()
            responseObject = {
                'status':'success',
                'message':'User checked in'
            }
            return jsonify(responseObject)
        except Exception as e:
            print(e)
            responseObject = {
                'status':'fail',
                'message':'DB error',
                'error':str(e)
            }
            return jsonify(responseObject)

@attend.route('/check/contest')
class AttendCheck(Resource):
    # Checkin with Farer
    @api.doc(params={
        'farer':'farer',
        'id':'Contest ID'
    })
    @authorizestaff(request, "contests", 4)
    def post(u, self):
        try:
            data = request.get_json()
            user = User.query.filter_by(farer=data.get('farer')).first()
            reg = Registrations.query.filter_by(vid=user.vid, cat=2, eid=data.get('id')).first()
            if reg is None:
                responseObject = {
                    'status':'fail',
                    'message':'User not registered for the competition'
                }
        except Exception as e:
            print(e)
            responseObject = {
                'status':'fail',
                'message':'DB error / input error',
                'error':str(e)
            }
            return jsonify(responseObject)
        try:
            a = AttendLog(vid=user.vid,
                        cat=2,
                        eid=data.get('id'),
                        by=u.vid
                        )
            db.session.add(a)
            db.session.commit()
            responseObject = {
                'status':'success',
                'message':'User checked in'
            }
            return jsonify(responseObject)
        except Exception as e:
            print(e)
            responseObject = {
                'status':'fail',
                'message':'DB error',
                'error':str(e)
            }
            return jsonify(responseObject)

@attend.route('/stats')
class AttendStats(Resource):
    print("Atten")
