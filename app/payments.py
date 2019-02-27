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
from app.models import User, Staff, Transactions, Registrations
from config import Config
from app.farer import authorizestaff, authorize
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
	return ct;
def decrypt(data):
	data = b64decode(data)
	cipher = AES.new(key, AES.MODE_CBC, iv)
	ct_bytes = cipher.decrypt(data)
	ct_bytes = str(ct_bytes,'utf-8')
	return ct_bytes

def pay_data(amt, tid):
#def pay_data(plaintext):
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

def workshopPay(workshop, user):
    transaction = Transactions(vid=user.vid, cat=1, eid=workshop.id, amount=workshop.fee)
    print(transaction.amount)
    print(workshop.fee)
    db.session.add(transaction)
    db.session.commit()
    return pay_data(transaction.amount, transaction.trid)

def paystatuschecker():
    return 1

@pay.route('/receive', methods=['GET', 'POST'])
class pay_receiver(Resource):
    def get(self):
        return pay_data("transactionId=ORDER1545904238000TK|amount=10|purpose=SOME|currency=inr|bankrefno=""|status=FAILED|statusDesc=User pressed cancel button|checkSum=d8dfb6b280e664b95b2c0a215661a2ec")

    # @authorize
    def post(self):
        try:
            d = request.get_json()
            data = d.get('data')
            code = d.get('code')
            plaintext = decrypt(data)
            print(plaintext)
            d = plaintext.split('|')
            print(d)
            trid = d[0].split('=')[1]
            trid = trid[6:]
            print(trid)
            t = Transactions.query.filter_by(trid=trid).first()
            if t is None:
                print("Invalid transaction ID - manage this!")
                # Send an email
            t.bankref = d[4].split('=')[1]
            t.status = d[5].split('=')[1]
            t.statusdesc = d[6].split('=')[1]
            t.reply = plaintext
            # print(bankref)
            # print(status)
            # print(statusdesc)
            if (t.status.upper() == 'SUCCESS'):
                print("Success")
                r = Registrations(vid=t.vid, cat=t.cat, eid=t.eid, typ=1, trid=t.trid)
                db.session.add(r)
                db.session.commit()
                responseObject = {
                    'status':'success',
                    'message':'payment successful. Reg ID:'+str(r.regid)
                }
                return jsonify(responseObject)
            else:
                responseObject = {
                    'status':t.status.lower(),
                    'message':t.reply
                }
                return jsonify(responseObject)

        except Exception as e:
            responseObject = {
                'status':'fail',
                'message':'Exception occured : '+str(e)
            }
            return jsonify(responseObject)

# @pay.route('/prob')
# def probbing(Resource):
#     # F you ACRD
#     def get(self):
#         payload = {

#         }
#         f = request.get('https://payments.acrd.org.in/pay/doubleverifythirdparty', json=)


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
