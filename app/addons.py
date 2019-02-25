import datetime
import werkzeug.security
from flask import render_template, flash, redirect, request, url_for, jsonify,json
from app import app, db, api
from app.farer import authorizestaff, authorize
# from app.mail import other
from config import Config
from values import Prices
from app.models import User, Transactions, OtherPurchases
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from flask_restplus import Resource, Api
from app.farer import auth_token

add = api.namespace('addons', description="Addons service")

@add.route('/order/staff')
class AddonStaff(Resource):
    # @authorizestaff(request, "registration", 2)
    def get(self):
        rgs = OtherPurchases.query.all()
        r = []
        for i in rgs:
            print(i.__dict__)
        return "Hello!"

    @api.doc(params = {
        'vid':'VID of the purchasee',
        'pid':'Product ID',
        'roll':'(needed for amrita tickets) Amrita Roll Number',
        'bookid':'Register book ID',
        'scount':'S count',
        'mcount':'M count',
        'lcount':'L count',
        'xlcount':'XL count',
        'xxlcount':'XXL count',
        'qty':'Quandity of the product'
        })
    @authorizestaff(request, "registration", 3)
    def post(u, self):
        try:
            data = request.get_json()
            print("RECIEVING = ", data)
            pid = data.get('pid')
            qty = data.get('qty')
            if pid is None or vid is None or data.get('book') is None or data.get('roll') is None:
                responseObject = {
                    'status':'fail',
                    'message':'No proper data'
                }
            if pid == 1:
                # Amritapuri: Proshow + Choreonite + Fashionshow
                total = qty*Prices.P1
                if qty >= 20:
                    qty += int(qty/20)
                    message = "Offer applied. "+ int(qty/20) +" free ticket(s) added."
            elif pid == 2:
                # Outstation: Proshow + Choreonite + Fashionshow
                total = qty*Prices.P2
                if qty >= 3:
                    total -= int(qty/3)*100
                    message = "Offer applied. Rs. " + int(qty/3)*100 + " off."
            elif pid == 3:
                # General: Headbangers + Choreonite + Fashionshow
                total = qty*Prices.P3
                if qty >= 3:
                    total -= int(qty/3)*100
                    message = "Offer applied. Rs. " + int(qty/3)*100 + " off."
            elif pid == 4:
                # Choreonite + Fashionshow
                total = qty*Prices.P4
            elif pid == 5:
                # T-Shirt
                qty = scount + mcount + lcount + xlcount + xxlcount
                total = qty*Prices.P5
            elif pid == 6:
                # Amritapuri: All Tickets + T-Shirt
                total = qty*(Prices.P1 + Prices.P5 - 50)
                if qty >= 20:
                    qty += int(qty/20)
                    message = "Offer applied. "+ int(qty/20) +" free ticket(s) added."
            elif pid == 7:
                # Outstation: All Tickets + T-Shirt
                qty = scount + mcount + lcount + xlcount + xxlcount
                total = qty*(Prices.P2 + Prices.P5 - 50)
            elif pid == 8:
                # General: Headbangers + Choreonite + Fashionshow + T-Shirt
                qty = scount + mcount + lcount + xlcount + xxlcount
                total = qty*(Prices.P3 + Prices.P5 - 50)
                if qty >= 3:
                    total -= int(qty/3)*100
                    message = "Offer applied. Rs. " + int(qty/3)*100 + " off."
            op = OtherPurchases(vid=data.get('vid'),
                                pid=pid,
                                qty=qty,
                                roll=data.get('roll'),
                                bookid=data.get('bookid'),
                                scount=data.get('scount'),
                                mcount=data.get('mcount'),
                                lcount=data.get('lcount'),
                                xlcount=data.get('lcount'),
                                xxlcount=data.get('lcount'),
                                message=message,
                                by=u.vid
                                )
            db.session.add(op)
            db.session.commit()
        except Exception as e:
            print(e)
            # error_mail(e)
            responseObject = {
                'status':'fail',
                'message':'Exception occured. (Error: '+str(e)+'. Please email or call web team'
            }
            return jsonify(responseObject)
        responseObject = {
            'status':'success',
            'message': op.message + ' Total transaction amount: Rs. '+ op.total + 'for a total of '+op.qty+' products'
        }
        return jsonify(responseObject)