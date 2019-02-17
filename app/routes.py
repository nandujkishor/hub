import os
import json
import datetime
from flask import render_template, flash, redirect, request, url_for, jsonify
from app import app, db
from config import Config
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse

@app.before_request
def before_request():
    print("Before req")

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', page="/home", uchange="")