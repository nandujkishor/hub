import datetime
import werkzeug.security
from flask import render_template, flash, redirect, request, url_for, jsonify,json
from app import app, db, api
from app.farer import authorizestaff, authorize
# from app.mail import other
from config import Config
from app.models import User, Transactions, OtherPurchases
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
            print("RECIEVING = ", data)
            self.vid = vid
            self.pid = pid
            self.total = 0
            self.qty = qty
            if pid == 1:
                # Amritapuri: Proshow + Choreonite + Fashionshow
                self.total = qty*Prices.P1
                if qty >= 20:
                    self.qty += 1
                    self.message = "Offer applied. One free ticket added."
                # Send mail regarding the purchase
            elif pid == 2:
                # Outstation: Proshow + Choreonite + Fashionshow
                self.total = qty*Prices.P2
                if qty >= 3:
                    self.total -= int(qty/3)*100
                    self.message = "Offer applied. Rs. " + int(qty/3)*100 + " off."
            elif pid == 3:
                # General: Headbangers + Choreonite + Fashionshow
                self.total = qty*Prices.P3
                if qty >= 3:
                    self.total -= int(qty/3)*100
                    self.message = "Offer applied. Rs. " + int(qty/3)*100 + " off."
            elif pid == 4:
                # Choreonite + Fashionshow
                self.total = qty*Prices.P4
            elif pid == 5:
                # T-Shirt
                self.tsize = tsize
                self.total = qty*Prices.P5
            elif pid == 6:
                # Amritapuri: Tickets + T-Shirt
                self.total = qty*Prices.P6
                self.tsize = tsize
            elif pid == 7:
                # Outstation: Tickets + T-Shirt
                self.total = qty*Prices.P7
                self.tsize = tsize
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
            # error_mail(e)
            responseObject = {
                'status':'fail',
                'message':'Exception occured. Please contact web team (nandakishore@vidyut.amrita.edu)'
            }
            return jsonify(responseObject)