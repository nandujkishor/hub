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
from app.mail import addon_pur
from sqlalchemy.sql import func

add = api.namespace('addons', description="Addons service")

products = ['Amritapuri: Proshow + Choreonite + Fashionshow','Outstation: Proshow + Choreonite + Fashionshow', 'General: Headbangers + Choreonite + Fashionshow', 'Choreonite + Fashionshow','T-Shirt','Amritapuri: All Tickets + T-Shirt','Outstation: All Tickets + T-Shirt','General: Headbangers + Choreonite + Fashionshow + T-Shirt']

def addonprice(pid, scount, mcount, lcount, xlcount, xxlcount, message, qty):
    # Returns total price, adds a message to message and updates qty, if needed
    print(scount, mcount, lcount, xlcount, xxlcount, qty)
    try:
        if qty == 0:
            return "Error: Quandity is 0"
        if pid == 1:
            # Amritapuri: Proshow + Choreonite + Fashionshow
            total = qty*Prices.P1
            if qty >= 20:
                qty += int(qty/20)
                message = "Offer applied. "+ str(int(qty/20)) +" free ticket(s) added."
        elif pid == 2:
            # Outstation: Proshow + Choreonite + Fashionshow
            total = qty*Prices.P2
            if qty >= 3:
                total -= int(qty/3)*100
                message = "Offer applied. Rs. " + str(int(qty/3)*100) + " off."
        elif pid == 3:
            # General: Headbangers + Choreonite + Fashionshow
            total = qty*Prices.P3
        elif pid == 4:
            # Choreonite + Fashionshow
            total = qty*Prices.P4
        elif pid == 5:
            # T-Shirt
            # qty = scount + mcount + lcount + xlcount + xxlcount
            total = qty*Prices.P5
        elif pid == 6:
            # Amritapuri: All Tickets + T-Shirt
            # qty = scount + mcount + lcount + xlcount + xxlcount
            total = qty*(Prices.P1 + Prices.P5)
        elif pid == 7:
            # Outstation: All Tickets + T-Shirt
            # qty = scount + mcount + lcount + xlcount + xxlcount
            total = qty*(Prices.P2 + Prices.P5)
        elif pid == 8:
            # General: Headbangers + Choreonite + Fashionshow + T-Shirt
            # qty = scount + mcount + lcount + xlcount + xxlcount
            total = qty*(Prices.P3 + Prices.P5)
    except Exception as e:
        print(e)
        return "Error"
    return total

def addon_purchase(staff, pid, purchasee, qty, scount, mcount, lcount, xlcount, xxlcount, typ, roll=None, bookid=None):
    total = 0
    message = "Success"
    try:
        if pid > 4:
            qty = scount + mcount + lcount + xlcount + xxlcount
        total = addonprice(pid=pid,
                    scount=scount,
                    mcount=mcount,
                    lcount=lcount,
                    xlcount=xlcount,
                    xxlcount=xxlcount,
                    message=message,
                    qty=qty)
        op = OtherPurchases(vid=purchasee.vid,
                            pid=pid,
                            qty=qty,
                            roll=roll,
                            bookid=bookid,
                            scount=scount,
                            mcount=mcount,
                            lcount=lcount,
                            xlcount=xlcount,
                            xxlcount=xxlcount,
                            total=total,
                            message=message,
                            typ=typ
                            )
        if staff is not None:
            op.by = staff.vid
        db.session.add(op)
        db.session.commit()
        print(op.purtime)
    except Exception as e:
        print(e)
        # error_mail(e)
        responseObject = {
            'status':'fail',
            'message':'Exception occured. (Error: '+str(e)+'. Please email or call web team'
        }
        return jsonify(responseObject)
    try:
        title = products[pid-1]
        purid = op.purid
        addon_pur(user=purchasee, title=title, purid=purid, count=qty)
    except Exception as e:
        print(e)
    qty = str(qty)
    print(qty)
    total = str(total)
    responseObject = {
        'status':'success',
        'message': str(message) + ' Total transaction amount: Rs. '+ total + ' for a total of '+ qty +' product(s)'
    }
    return jsonify(responseObject)

@add.route('/order/new')
class NewOrder(Resource):
    @api.doc(params={
        'pid':'Purchase ID',
        'scount':'S Shirt count',
        'mcount':'M Shirt count',
        'lcount':'L Shirt count',
        'xlcount':'XL Shirt count',
        'xxlcount':'XXL Shirt count',
        'qty':'qty'
    })
    @authorize(request)
    def get(u, self):
        addonPay()

@add.route('/order/my')
class MyOrder(Resource):
    @authorize(request)
    def get(u, self):
        rgs = OtherPurchases.query.filter_by(vid=u.vid).order_by(OtherPurchases.purid.desc()).all()
        products = ['Amritapuri: Proshow + Choreonite + Fashionshow','Outstation: Proshow + Choreonite + Fashionshow', 'General: Headbangers + Choreonite + Fashionshow',
                        'Choreonite + Fashionshow','T-Shirt','Amritapuri: All Tickets + T-Shirt','Outstation: All Tickets + T-Shirt','General: Headbangers + Choreonite + Fashionshow + T-Shirt']
        for i in rgs:
            r.append({
                'purid':i.purid,
                'purchase':products[i.pid-1],
                'pid':i.pid,
                'scount':i.scount,
                'mcount':i.mcount,
                'lcount':i.lcount,
                'xlcount':i.xlcount,
                'xxlcount':i.xxlcount,
                'qty':i.qty,
                'total':i.total,
                'purtime':i.purtime
            })
        return jsonify(r)

@add.route('/order/staff')
class AddonStaff(Resource):
    @authorizestaff(request, "sales", 2)
    def get(u, self):
        rgs = OtherPurchases.query.order_by(OtherPurchases.purid.desc()).all()
        r = []
        products = ['Amritapuri: Proshow + Choreonite + Fashionshow','Outstation: Proshow + Choreonite + Fashionshow', 'General: Headbangers + Choreonite + Fashionshow',
                        'Choreonite + Fashionshow','T-Shirt','Amritapuri: All Tickets + T-Shirt','Outstation: All Tickets + T-Shirt','General: Headbangers + Choreonite + Fashionshow + T-Shirt']
        for i in rgs:
            r.append({
                'purid':i.purid,
                'vid':i.vid,
                'roll':i.roll,
                'purchase':products[i.pid-1],
                'bookid':i.bookid,
                'pid':i.pid,
                'scount':i.scount,
                'mcount':i.mcount,
                'lcount':i.lcount,
                'xlcount':i.xlcount,
                'xxlcount':i.xxlcount,
                'qty':i.qty,
                'total':i.total,
                'purtime':i.purtime
            })
        return jsonify(r)

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
            scount = data.get('scount')
            mcount = data.get('mcount')
            lcount = data.get('lcount')
            xlcount = data.get('xlcount')
            xxlcount = data.get('xxlcount')
            message = "Success."
            if pid is None or data.get('vid') is None or data.get('bookid') is None:
                responseObject = {
                    'status':'fail',
                    'message':'No proper data'
                }
                return jsonify(responseObject)
            purchasee = User.query.filter_by(vid=data.get('vid')).first()
            response = addon_purchase(staff=u,
                                    pid=pid,
                                    purchasee=purchasee,
                                    qty=qty,
                                    scount=scount,
                                    mcount=mcount,
                                    lcount=lcount,
                                    xlcount=xlcount,
                                    xxlcount=xxlcount,
                                    roll=data.get('roll'),
                                    bookid=data.get('bookid'),
                                    typ=2
                                    )
            return response
        except Exception as e:
            responseObject = {
                'status':'fail',
                'message':'Error occured. (Error: '+str(e)+')'
            }
            return jsonify(responseObject)
        #     if pid == 1:
        #         # Amritapuri: Proshow + Choreonite + Fashionshow
        #         total = qty*Prices.P1
        #         if qty >= 20:
        #             qty += int(qty/20)
        #             message = "Offer applied. "+ str(int(qty/20)) +" free ticket(s) added."
        #     elif pid == 2:
        #         # Outstation: Proshow + Choreonite + Fashionshow
        #         total = qty*Prices.P2
        #         if qty >= 3:
        #             total -= int(qty/3)*100
        #             message = "Offer applied. Rs. " + str(int(qty/3)*100) + " off."
        #     elif pid == 3:
        #         # General: Headbangers + Choreonite + Fashionshow
        #         total = qty*Prices.P3
        #         # if qty >= 3:
        #         #     total -= int(qty/3)*100
        #         #     message = "Offer applied. Rs. " + str(int(qty/3)*100) + " off."
        #     elif pid == 4:
        #         # Choreonite + Fashionshow
        #         total = qty*Prices.P4
        #     elif pid == 5:
        #         # T-Shirt
        #         qty = scount + mcount + lcount + xlcount + xxlcount
        #         total = qty*Prices.P5
        #     elif pid == 6:
        #         qty = scount + mcount + lcount + xlcount + xxlcount
        #         # Amritapuri: All Tickets + T-Shirt
        #         total = qty*(Prices.P1 + Prices.P5 - 50)
        #     elif pid == 7:
        #         # Outstation: All Tickets + T-Shirt
        #         qty = scount + mcount + lcount + xlcount + xxlcount
        #         total = qty*(Prices.P2 + Prices.P5 - 50)
        #     elif pid == 8:
        #         # General: Headbangers + Choreonite + Fashionshow + T-Shirt
        #         qty = scount + mcount + lcount + xlcount + xxlcount
        #         total = qty*(Prices.P3 + Prices.P5 - 50)
        #         # if qty >= 3:
        #         #     total -= int(qty/3)*100
        #         #     message = "Offer applied. Rs. " + str(int(qty/3)*100) + " off."
        #     if qty == 0:
        #         responseObject = {
        #             'status':'fail',
        #             'message':'No products added.'
        #         }
        #         return jsonify(responseObject)
        #     op = OtherPurchases(vid=data.get('vid'),
        #                         pid=pid,
        #                         qty=qty,
        #                         roll=data.get('roll'),
        #                         bookid=data.get('bookid'),
        #                         scount=data.get('scount'),
        #                         mcount=data.get('mcount'),
        #                         lcount=data.get('lcount'),
        #                         xlcount=data.get('xlcount'),
        #                         xxlcount=data.get('xxlcount'),
        #                         total=total,
        #                         message=message,
        #                         by=u.vid
        #                         )
        #     db.session.add(op)
        #     db.session.commit()
        #     print(op.purtime)
        # except Exception as e:
        #     print(e)
        #     # error_mail(e)
        #     responseObject = {
        #         'status':'fail',
        #         'message':'Exception occured. (Error: '+str(e)+'. Please email or call web team'
        #     }
        #     return jsonify(responseObject)
        # try:
        #     products = ['Amritapuri: Proshow + Choreonite + Fashionshow','Outstation: Proshow + Choreonite + Fashionshow', 'General: Headbangers + Choreonite + Fashionshow',
        #                 'Choreonite + Fashionshow','T-Shirt','Amritapuri: All Tickets + T-Shirt','Outstation: All Tickets + T-Shirt','General: Headbangers + Choreonite + Fashionshow + T-Shirt']
        #     title = products[pid-1]
        #     purid = op.purid
        #     user = User.query.filter_by(vid=op.vid).first()
        #     addon_pur(user=user, title=title, purid=purid, count=qty)
        # except Exception as e:
        #     print(e)
        # qty = str(qty)
        # print(qty)
        # total = str(total)
        # responseObject = {
        #     'status':'success',
        #     'message': str(message) + ' Total transaction amount: Rs. '+ total + ' for a total of '+ qty +' product(s)'
        # }
        # return jsonify(responseObject)

@add.route('/order/stats')
class AddonStaffCount(Resource):
    @authorizestaff(request, "registration", 3)
    def get(u, self):
        try:
            amt = db.session.query(func.sum(OtherPurchases.total)).scalar()
            scount = db.session.query(func.sum(OtherPurchases.scount)).scalar()
            mcount = db.session.query(func.sum(OtherPurchases.mcount)).scalar()
            lcount = db.session.query(func.sum(OtherPurchases.lcount)).scalar()
            xlcount = db.session.query(func.sum(OtherPurchases.xlcount)).scalar()
            xxlcount = db.session.query(func.sum(OtherPurchases.xxlcount)).scalar()
            pid1 = len(OtherPurchases.query.filter_by(pid=1).all())
            pid2 = len(OtherPurchases.query.filter_by(pid=2).all())
            pid3 = len(OtherPurchases.query.filter_by(pid=3).all())
            pid4 = len(OtherPurchases.query.filter_by(pid=4).all())
            pid5 = len(OtherPurchases.query.filter_by(pid=5).all())
            pid6 = len(OtherPurchases.query.filter_by(pid=6).all())
            pid7 = len(OtherPurchases.query.filter_by(pid=7).all())
            pid8 = len(OtherPurchases.query.filter_by(pid=8).all())
            tshirt = scount+mcount+lcount+xlcount+xxlcount

            proshow=0
            headbangers=0
            choreonite=0

            total = OtherPurchases.query.all()
            for each in total:
                if each.pid == 3 or each.pid == 8:
                    headbangers += each.qty
                if each.pid == 1 or each.pid == 2 or each.pid == 6 or each.pid == 7:
                    proshow += each.qty
                if each.pid == 4:
                    choreonite += each.qty

            proshow += headbangers
            choreonite += proshow
            fashionshow = choreonite

            responseObject = {
                'status':'success',
                'count':amt,
                'scount':scount,
                'mcount':mcount,
                'lcount':lcount,
                'xlcount':xlcount,
                'xxlcount':xxlcount,
                'pid1':pid1,
                'pid2':pid2,
                'pid3':pid3,
                'pid4':pid4,
                'pid5':pid5,
                'pid6':pid6,
                'pid7':pid7,
                'pid8':pid8,
                'headbangers':headbangers,
                'proshow':proshow,
                'choreonite':choreonite,
                'fashionshow':fashionshow,
                'tshirt':tshirt,
            }
            return jsonify(responseObject)
        except Exception as e:
            print(e)
