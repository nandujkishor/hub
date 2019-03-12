import os
import datetime
import requests
import json
from flask import render_template, flash, redirect, request, url_for, jsonify
from app import app, db, api
from app.models import User, Staff, Pos, ValletTransaction, ValletProduct
from config import Config
# from app.addons import addon_purchase
from app.farer import authorizestaff, authorize
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from flask_restplus import Resource, Api
from sqlalchemy.sql import func

vallet = api.namespace('vallet', description="Vallet service")

def valletbalance(vid):
    topup = ValletTransaction.query.with_entities(func.sum(ValletTransaction.amt)).filter(__or__(vid==vid, typ=1))
    spent = ValletTransaction.query.with_entities(func.sum(ValletTransaction.amt)).filter(__or__(vid==vid, typ=2))
    balance = topup - spent
    return balance

@vallet.route('/transaction')
class VTransaction(Resource):
    @authorize(request)
    def get(u, self):
        vt = ValletTransaction.query.filter_by(vid=u.vid).all()
        return jsonify(vt)

    @authorizestaff(request, "pay", 3)
    @api.doc(params={
        'vid':'Vidyut ID of the staff',
        'pos':'Point of sale ID',
        'amt':'Transaction Amount'
    })
    def post(u, self):
        data = request.get_json()
        if data.get('amt') is None or data.get('vid') is None or data.get('pos') is None:
            responseObject = {
                'status':'fail',
                'message':'Inadequate data'
            }
            return jsonify(responseObject)
        try:
            amt = data.get('amt')
            vid = data.get('vid')
            truser = User.query.filter_by(vid=vid).first()
            if truser is None:
                responseObject = {
                    'status':'fail',
                    'message':'Invalid User'
                }
                return jsonify(responseObject)
        except Exception as e:
            print(e)
            responseObject = {
                'status':'fail',
                'message':'Error: '+str(e)
            }
            return jsonify(responseObject)
        try:
            pos = Pos.query.filter_by(posid=data.get('pos')).first()
            if pos is None:
                responseObject = {
                    'status':'fail',
                    'message':'Invalid point of sale'
                }
                return jsonify(responseObject)
        except Exception as e:
            print(e)
        try:
            typ = 2
            if pos < 100:
                truser.balance = truser.balance + amt
                typ = 1
            else:
                truser.balance = truser.balance - amt
                typ = 2
            # db.session.commit()
            # Check if working
            vt = ValletTransaction(vid=data.get('vid'),
                                    typ=typ,
                                    pos=data.get('pos'),
                                    notes=data.get('notes'),
                                    amt=data.get('amt'),
                                    by=u.vid
                                    )
            db.session.add(vt)
            db.session.commit()
        except Exception as e:
            responseObject = {
                'status':'fail',
                'message':'No balance or database error. Error: '+str(e)
            }
        try:
            # mail the user and send message on the transaction
            payload = {
                # 'ip':
                'key':'vidyuth1908030559',
                'num':truser.phno,
                'message':'Vallet Transaction of Rs. '+str(amt)+' at '+str(pos.title)+'.'
            }
            r = requests.get('http://sms.amrita.ac.in/', data=payload)
            # Uncomment only when needed
        except Exception as e:
            responseObject = {
                'status':'success',
                'message':'Transaction succesful with errors (message not sent). Please inform user the transaction is successful. Error: '+str(e)
            }
            return jsonify(responseObject)
        responseObject = {
            'status':'success',
            'transaction ID':vt.tid
        }
        return jsonify(responseObject)

@vallet.route('/deliver/pos/<int:id>')
class VDeliver(Resource):
    @authorizestaff(request)
    # Sends all undelivered transactions
    def get(u, self, id):
        if pos < 100:
            responseObject = {
                'status':'fail',
                'message':'No deliveries for recharge station'
            }
            return jsonify(responseObject)
        und = ValletTransaction.query.filter_by(pos=id, delivered=False).all()
        resp = []
        for i in und:
            resp.append({
                'tid':i.tid,
                'vid':i.vid,
                'notes':i.notes,
                'amt':i.amt,
                'by':i.by
            })
        responseObject = {
            'status':'success',
            'data':jsonify(resp)
        }
        return jsonify(responseObject)

@vallet.route('/products/<int:id>')
class PosProducts(Resource):
    def get(self, id):
        p = ValletProduct.query.filter_by(pod=id).all()
        pr = []
        for i in p:
            pr.append({
                'prodid':i.prodid,
                'title':i.title,
                'desc':i.desc,
                'amount':i.amount
            })
        responseObject = {
            'status':'success',
            'response':jsonify(pr)
        }
        return jsonify(responseObject)

    @authorizestaff(request, "pay", 4)
    def post(u, self, id):
        try:
            data = request.get_json()
            product = ValletProduct(pos=id,
                                    title=data.get('title'),
                                    desc=data.get('desc'),
                                    amount=data.get('amount'),
                                    by=u.vid
                                )
            db.session.add(product)
            db.session.commit()
            responseObject = {
                'status':'success',
                'message':'Product successfully added'
            }
            return jsonify(responseObject)
        except Exception as e:
            print(e)
            responseObject = {
                'status':'fail',
                'message':'Inadequate data / Database error',
                'error':str(e)
            }
            return jsonify(responseObject)

@vallet.route('/deliver')
class VDeliverNow(Resource):
    @authorizestaff(request)
    @api.doc(params={
        'tid':'Transaction ID'
    })
    def post(u, self):
        try:
            data = request.get_json()
            tid = data.get('tid')
        except Exception as e:
            responseObject = {
                'status':'fail',
                'message':'Invalid data'
            }
            return jsonify(responseObject)
        try:
            t = ValletTransaction.query.filter_by(tid=tid).first()
            t.delivered = True
            db.session.commit()
        except Exception as e:
            print(e)
            responseObject = {
                'status':'fail',
                'message':'Error: '+str(e)
            }
            return jsonify(responseObject)
        responseObject = {
            'status':'success',
            'message':'Successfully delivered'
        }
        return jsonify(responseObject)

@vallet.route('/balance')
class VBalance(Resource):
    @authorize(request)
    def get(u, self):
        try:
            balance = valletbalance(u.vid)
        except Exception as e:
            print(e)
            responseObject = {
                'status':'fail',
                'message':'Error: '+str(e)
            }
            return jsonify(responseObject)
        responseObject = {
            'status':'success',
            'balance':balance
        }
        return jsonify(responseObject)

@vallet.route('/pos')
class ValletPOS(Resource):
    def get(self):
        try:
            pos = Pos.query.all()
            resp = []
            for i in pos:
                resp.append({
                    'posid':i.posid,
                    'title':i.title,
                    'descr':i.descr
                })
        except Exception as e:
            print(e)
            responseObject = {
                'status':'fail',
                'message':'Database error: '+str(e)
            }
        responseObject = {
            'status':'success',
            'data':jsonify(resp)
        }
        return jsonify(responseObject)

    @api.doc(params={
        'title':'POS title',
        'descr':'Description'
    })
    @authorizestaff(request, "pay", 4)
    def post(u, self):
        data = request.get_json()
        pos = Pos(title=data.get('title'), descr=data.get('descr'))
        db.session.add(pos)
        db.session.commit()
        responseObject = {
            'status':'success',
            'message':'POS added'
        }
        return jsonify(responseObject)