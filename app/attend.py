import os
import datetime
import requests
import json
from flask import render_template, flash, redirect, request, url_for, jsonify
from app import app, db, api
from app.models import User, AttendLog
from config import Config
# from app.addons import addon_purchase
from app.farer import authorizestaff, authorize
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
            user.intime = datetime.datetime.now()
            user.farer = d.get('farer')
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
            # Send email
            p = 1
        except Exception as e:
            print(e)
        responseObject = {
            'status':'success',
            'message':'User successfully linked to Farer'
        }
        return jsonify(responseObject)

@attend.route('/check')
class AttendCheck(Resource):
    # Checkin with Farer
    @api.doc(params={
        'farer':'farer',
        'cat':'Event category',
        'eid':'Event ID'
    })
    @authorizestaff(request)
    def post(u, self):
        data = request.get('data')
        user = User.query.filter_by(farer=data.get('farer')).first()
        a = AttendLog(vid=user.vid,
                    cat=data.get('cat'),
                    eid=data.get('eid'),
                    )
                    # Log the registration staff VID as well