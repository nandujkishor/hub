import os
import qrcode
import datetime
import hashlib
from flask import render_template, flash, redirect, request, url_for, jsonify
from app import app, db, api
from app.models import User, Staff
from config import Config
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from flask_restplus import Resource, Api

pay = api.namespace('pay', description="Payments management")

def get_checksum() {
}

def 