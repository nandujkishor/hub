import os
import datetime
import requests
import json
from flask import render_template, flash, redirect, request, url_for, jsonify
from app import app, db, api
from app.models import User, Staff, Notifications, NotifUser
from config import Config
# from app.addons import addon_purchase
from app.farer import authorizestaff, authorize
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from flask_restplus import Resource, Api

notif = api.namespace('notifications', description="Notifications")

@notif.route('/')
class NotificationsUser(Resource):
    @authorize(request)
    def get(user, self):
        alln = NotifUser.query.join(Notifications, NotifUser.nid==Notifications.nid).filter_by(vid=user.vid).all()
        # Passes all notifications, uncluding read. For just unread, goto /unread
        return jsonify(alln)

@notif.route('/unread')
class NotifUnread(Resource):
    @authorize(request)
    def get(user, self):
        alln = NotifUser.query.join(Notifications, NotifUser.nid==Notifications.nid).filter_by(vid=user.vid, read=False).all()
        return jsonify(alln)

@notif.route('/latest')
class NotifLatest(Resource):
    @authorize(request)
    # Only those notifications that are newer than passed NID
    def get(user, self):
        print("Sta  rt")
        data = request.get_json()
        if data.get('nid'):
            nid = data.get('nid')
        else:
            n = NotifUser.query.filter_by(vid=user.vid, read = True).order_by(time, desc).first()
            nid = n.nid
        alln = NotifUser.query.join(Notifications, NotifUser.nid==Notifications.nid).filter(__or__(vid==user.vid, NotifUser.nid > nid)).all()