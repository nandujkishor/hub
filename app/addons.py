import datetime
import werkzeug.security
from flask import render_template, flash, redirect, request, url_for, jsonify,json
from app import app, db, api
from app.farer import authorizestaff, authorize
# from app.mail import exception_mail
from config import Config
from app.models import User, Transactions
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from flask_restplus import Resource, Api
from app.farer import auth_token

add = api.namespace('addons', description="Addons service")

@add.route('/order/staff')
class AddonStaff(Resource):
    @api.doc(params = {
        'vid':'VID of the purchasee',
        'pid':'Product ID',
        'tsize':'(Optional) Size of the T-shirt. Based on the Product ID',
        'qty':'Quandity of the product',
        })
    @authorizestaff(request, "registration", 3)
    def post(u, self):
        try:
            data = request.get_json()
            op = OtherPurchases(vid=data.get('vid'),
                                pid=data.get('pid'),
                                qty=data.get('qty'),
                                tsize = data.get('tsize'),
                                by=u.vid
                                )
            db.session.add(op)
            db.session.commit()
            responseObject = {
                'status':'success',
                'message': op.message + ' Total transaction amount: Rs. '+ op.total + 'for a total of '+op.qty+' products'
            }
            return jsonify(responseObject)
        except Exception as e:
            print(e)
            error_mail(e)
            responseObject = {
                'status':'fail',
                'message':'Exception occured. Please contact web team (nandakishore@vidyut.amrita.edu)'
            }
            return jsonify(responseObject)