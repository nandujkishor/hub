import os
import qrcode
import datetime
import hashlib
import sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode
from flask import render_template, flash, redirect, request, url_for, jsonify
from app import app, db, api
from app.mail import send_spam
from app.models import User, Staff, Transactions, Registrations, AddonTransactions
from config import Config
from app.farer import authorizestaff, authorize
from app.addons import addonprice, addon_purchase
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from flask_restplus import Resource, Api
pay = api.namespace('pay', description="Payments management")

key = b'WEGSNGOXHEUDEEDD'
iv = b'3564234432724374'

def encrypt(data):
	data = str.encode(data)
	cipher = AES.new(key, AES.MODE_CBC, iv)
	ct_bytes = cipher.encrypt(pad(data, AES.block_size))
	ct = b64encode(ct_bytes).decode('utf-8')
	return ct
def decrypt(data):
	data = b64decode(data)
	cipher = AES.new(key, AES.MODE_CBC, iv)
	ct_bytes = cipher.decrypt(data)
	ct_bytes = str(unpad(ct_bytes, AES.block_size),'utf-8')
	return ct_bytes

def pay_data(amt, tid):
# def pay_data(plaintext):
    # transactionId: Unique for each transaction
    # amount: Transaction amount (Positive integer only)
    # purpose: Transaction purpose: Conference code
    # currency: Transaction currency
    # checkSum: MD5 over the plaintext
    plaintext = "transactionId=VIDYUT"+str(tid)+"|amount="+str(amt)+"|purpose="+Config.PURPOSE+"|currency=inr"
    result = hashlib.md5(plaintext.encode())
    result = result.hexdigest()
    print("md5",result)
    pwc = plaintext + "|checkSum=" + result
    print("before aes",pwc)
    encd = encrypt(pwc)
    print("after aes", encd)
    payload = {
        'status':'success',
        'encdata':encd,
        'code':Config.PAYCODE
    }
    return jsonify(payload)

def response_data(data):
    # data: Encoded data
    plaintext = decrypt(data)
    print(plaintext)
    d = plaintext.split('|')
    print(d)
    send_spam("Pay2: "+str(d)+" as plaintext with split")
    trid = d[0].split('=')[1]
    trid = trid[6:]
    print(trid)
    t = Transactions.query.filter_by(trid=trid).first()
    if t is None:
        print("Invalid transaction ID - manage this!")
        send_spam("Error: Invalid transaction ID")
        return "H"
    t.bankref = d[4].split('=')[1]
    t.status = d[5].split('=')[1]
    t.statusdesc = d[6].split('=')[1]
    t.reply = plaintext
    # print(bankref)
    # print(status)
    # print(statusdesc)
    if (t.status.upper() == 'SUCCESS'):
        print("Success")
        send_spam("Pay success")
        resp = trsuccess(t)
        responseObject = {
            'status':'success',
            'message':'payment successful',
            'addition':resp
        }
        return jsonify(responseObject)
    else:
        responseObject = {
            'status':t.status.lower(),
            'message':t.reply
        }
        return jsonify(responseObject)
    return "1"

def workshopPay(workshop, user):
    transaction = Transactions(vid=user.vid, cat=1, eid=workshop.id, amount=workshop.fee)
    print(transaction.amount)
    print(workshop.fee)
    db.session.add(transaction)
    db.session.commit()
    return pay_data(transaction.amount, transaction.trid)

def addonPay(user, pid, scount, mcount, lcount, xlcount, xxlcount, qty):
    # Create a transaction
    # Create a Addon transaction
    message = "Success"
    amount = addonprice(pid=pid,
                scount=scount,
                mcount=mcount,
                lcount=lcount,
                xlcount=xlcount,
                xxlcount=xxlcount,
                message=message,
                qty=qty)
    print(message)
    transaction = Transactions(vid=user.vid, cat=3, eid=pid, amount=amount)
    db.session.add(transaction)
    db.session.commit()
    traddon = AddonTransactions(trid=transaction.trid,
                                scount=scount,
                                mcount=mcount,
                                lcount=lcount,
                                xlcount=xlcount,
                                xxlcount=xxlcount,
                                qty=qty
                                )
    db.session.add(traddon)
    db.session.commit()
    return pay_data(transaction.amount, transaction.trid)

def trsuccess(t):
    if t.cat is 1 or t.cat is 2:
        # Workshop
        try:
            r = Registrations(vid=t.vid, cat=t.cat, eid=t.eid, typ=1, trid=t.trid)
            db.session.add(r)
            db.session.commit()
        except Exception as e:
            print(e)
            responseObject = {
                'status':'fail',
                'message':'Error occured. '+str(e)
            }
            return jsonify(responseObject)
        try:
            if t.cat is 1:
                # send email
                p = 1
            elif t.cat is 2:
                # Send mail
                p = 2
        except Exception as e:
            print(e)
        responseObject = {
            'status':'success',
            'message':'Successfully registered. But error in sending mail: '+str(e)
        }
        return jsonify(responseObject)

    elif t.cat is 3:
        # Addon purchase
        purchasee = User.query.filter_by(vid=t.vid).first()
        ta = AddonTransactions.query.filter_by(trid=t.trid).first()
        response = addon_purchase(purchasee=purchasee,
                                qty=ta.qty,
                                scount=ta.scount,
                                mcount=ta.scount,
                                lcount=ta.lcount,
                                xlcount=ta.xlcount,
                                xxlcount=ta.xxlcount,
                                typ=1
                                )
        return response

def probber():
    payload = {
        'encdata':pay_data(t.trid, t.amount)
        'code':
    }
    f = request.get('https://payments.acrd.org.in/pay/doubleverifythirdparty', json=payload)
    j = f.json()
    print(j)
    return response_data(j.get('data'))

@pay.route('/receive', methods=['GET', 'POST'])
class pay_receiver(Resource):
    def get(self):
        # Random thing for test: Only call after modification of pay_data
        return pay_data("transactionId=VIDYUT1212|amount=10|purpose=SOME|currency=inr|bankrefno=1|status=FAILED|statusDesc=User pressed cancel button")

    # @authorize
    def post(self):
        try:
            d = request.get_json()
            data = d.get('data')
            # code = d.get('code')
            return response_data(data)
        except Exception as e:
            print(e)
            responseObject = {
                'status':'fail',
                'message':'Exception occured : '+str(e)
            }
            return jsonify(responseObject)

@pay.route('/prob')
def probbing(Resource):
    # F you ACRD
    @api.doc(params={
        'trid':'Transaction ID',
    })
    @authorizestaff(request, 4)
    def get(u, self):
        data = request.json()
        t = Transactions.query.filter_by(trid=data.get('trid')).first()
        return probber(t)

@pay.route('/prob/all')
def massprobbing(Resource):
    @authorizestaff(request, 4)
    def get(u, self):
        tlist = Transactions.query.filter_by(status="PROCESSING").all()
        res = []
        for t in tlist:
            res.append(probbeer(t))
        return jsonify(res)

# @pay.route('/testing')
# def payment():
#     plaintext = "transactionId=VIDYUTTEST10|amount=1|purpose=VIDYUT19TEST|currency=inr"
#     result = hashlib.md5(plaintext.encode())
#     result = result.hexdigest()
#     print("md5",result)
#     pwc = plaintext + "|checkSum=" + result
#     print("before aes",pwc)
#     cipher = AESCipher(key)
#     encd = cipher.encrypt(pwc)
#     print("after aes", encd)
#     return encd

# @pay.route('/callback/', methods=['POST', 'GET'])
# def callback():
#     print("Inside callback")
#     print(request.args)
#     return "Check terminal"

# @pay.route('/check/')
# def check_pay():
#     return render_template('payment.html')
