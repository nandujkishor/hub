import datetime
import werkzeug.security
from flask import render_template, flash, redirect, request, url_for, jsonify,json
from app import app, db, api
from app.farer import authorizestaff, authorize
from config import Config
from app.models import User, Transactions
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from flask_restplus import Resource, Api
from app.farer import auth_token

add = api.namespace('addons', description="Addons service")

@add.route('/order/staff')
class AddonStaff(Resource):
    @authorizestaff("registration", 3)
    @api.doc(params = {
        'vid':'VID of the purchasee',
        'pid':'Product ID',
        'size':'(Optional) Size of the T-shirt. Based on the Product ID',
        'qty':'Quandity of the product',
        })
    def post(u, self):
        data = request.get_json()
        op = OtherPurchases(vid=data.get('vid'),
                            pid=data.get('pid'),
                            qty=data.get('qty'),
                            by=u.vid
                            )
        
        return "Hello"