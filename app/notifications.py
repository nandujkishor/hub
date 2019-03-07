import os
import datetime
import requests
import json
from flask import render_template, flash, redirect, request, url_for, jsonify
from app import app, db, api
from app.models import User, Staff, Notifications, NotifUser
from config import Config
# from app.addons import addon_purchase
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from flask_restplus import Resource, Api

notif = api.namespace('notifications', description="Notifications")