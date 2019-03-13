import os
import qrcode
import datetime
import hashlib
import sys
import requests
import json
import werkzeug.security
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode
from flask import render_template, flash, redirect, request, url_for, jsonify
from app import app, db, api
from app.mail import send_spam, wkreg_mail, ctreg_mail, addon_pur,ctregteamleader_mail
from app.models import User, Staff, Transactions, Registrations, AddonTransactions, OtherPurchases, Workshops, Contests
from config import Config
from values import Prices
from app.farer import authorizestaff, authorize
# from app.addons import addon_purchase
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from flask_restplus import Resource, Api
pay = api.namespace('pay', description="Payments management")

key = b'&YnI$7LP(!#BEzI*'
iv = b'8838098342343849'

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
    print("md5", result)
    pwc = plaintext + "|checkSum=" + result
    print("before aes",pwc)
    encd = encrypt(pwc)
    print("after aes", encd)
    payload = {
        # 'status':'success',
        'encdata':encd,
        'code':Config.PAYCODE
    }
    return payload

def response_data(data):
    # data: Encoded data
    try:
        plaintext = decrypt(data)
        print(plaintext)
        d = plaintext.split('|')
        print(d)
    except Exception as e:
        print(e)
        responseObject = {
			'status':'failed',
			'message':'Decryption error: '+str(e)
		}
        return jsonify(responseObject)
    try:
        trid = d[0].split('=')[1]
        trid = trid[6:]
        print(trid)
    except Exception as e:
        print(e)
        responseObject = {
            'status':'failed',
            'message':'cant get trid'+str(e)
        }
        return jsonify(responseObject)
    try:
        t = Transactions.query.filter_by(trid=trid).first()
        if t is None:
            print("Invalid transaction ID - manage this!")
            responseObject = {
                'status':'failed',
                'message':'Invalid transaction ID'
            }
            return jsonify(responseObject)
        t.bankref = d[4].split('=')[1]
        t.status = d[5].split('=')[1]
        t.status = t.status.lower()
        t.statusdesc = d[6].split('=')[1]
        t.reply = plaintext
        if(t.cat == 1 and t.status=='failed'):
            print("Going to give back - 1")
            work = Workshops.query.filter_by(id=t.eid).first()
            work.rmseats = work.rmseats + 1;
            db.session.commit()
        else:
            db.session.commit()
        if (t.status == 'success'):
            print("Success")
            resp = trsuccess(t).get_json()
            print("RESP ", resp)
            responseObject = {
                'status':'success',
                'message':'payment successful',
                'addition':resp.get('message')
            }
            return jsonify(responseObject)
        else:
            responseObject = {
	            'status':t.status,
	            'message':t.reply
	        }
            return jsonify(responseObject)
    except Exception as e:
        print(e)
        responseObject = {
			'status':'failed',
			'message':'Exception occured: '+str(e)
		}
        return jsonify(responseObject)
    return "1"

def workshopPay(workshop, user,transaction):
    # transaction = Transactions(vid=user.vid, cat=1, eid=workshop.id, amount=workshop.fee)
    print(transaction.amount)
    print(workshop.fee)
    return pay_data(transaction.amount, transaction.trid)

def addonPay(user, pid, qty):
    # Online purchase method
    # Create a transaction
    # Create a Addon transaction
    message = "Success"
    if pid == 2:
        print("Yeah 2")
        # Outstation: Proshow + Choreonite + Fashionshow
        total = qty*Prices.P2
        if qty >= 3:
            total -= int(qty/3)*100
            message = "Offer applied. Rs. " + str(int(qty/3)*100) + " off."
    elif pid == 3:
        # General: Headbangers + Choreonite + Fashionshow
        total = qty*Prices.P3
    elif pid == 100:
        # Testing case
        total = qty*Prices.P100
    else:
        responseObject = {
            'status':'failed',
            'message':'No such product'
        }
        return jsonify(responseObject)
    transaction = Transactions(vid=user.vid, cat=3, eid=pid, amount=total)
    print("TOTAL ", total)
    print("Transactions ", transaction.__dict__)
    db.session.add(transaction)
    db.session.commit()
    traddon = AddonTransactions(trid=transaction.trid,
                                qty=qty
                                )
    db.session.add(traddon)
    db.session.commit()
    return jsonify(pay_data(transaction.amount, transaction.trid))

def trsuccess(t):
    u = User.query.filter_by(vid=t.vid).first()
    if t.cat is 1 or t.cat is 2:
        r = None
        try:
            reg = Registrations.query.filter_by(vid=t.vid,cat=t.cat,eid=t.eid).first()
            if reg is None:
                r = Registrations(vid=t.vid, cat=t.cat, eid=t.eid, typ=1, trid=t.trid, amount=t.amount)
                db.session.add(r)
                db.session.commit()
                if (t.cat == 2):
                    eve = Contests.query.filter_by(id=t.eid).first()
                    if eve.team_limit > 1:
                        r.tid = werkzeug.security.pbkdf2_hex(str(r.regid), "F**k" ,iterations=50000, keylen=3)
                        db.session.commit()

            else:
                t.refund = True
                if(t.cat==1):
                    work = Workshops.query.filter_by(id=t.eid).first()
                    work.rmseats = work.rmseats + 1;
                    db.session.commit()
                else:
                    db.session.commit()
                responseObject = {
					'status':'failed',
					'message':'Refund'
				}

                return jsonify(responseObject)
        except Exception as e:
            print(e)
            responseObject = {
            	'status':'failed',
            	'message':'Error occured. '+str(e)
            }
            return jsonify(responseObject)
        try:
            user = User.query.filter_by(vid=t.vid).first()
            dept = ['CSE', 'ECE', 'ME', 'Physics', 'Chemisty', 'English', 'Biotech','BUG', 'Comm.', 'Civil', 'EEE', 'Gaming', 'Maths', 'Others']
            if t.cat is 1:
                w = Workshops.query.filter_by(id=t.eid).first()
                wkreg_mail(user=u, workshop=w, regid=r.regid, wdept=dept[w.department - 1])
                r.mail = True;
                db.session.commit()
            elif t.cat is 2:
                c = Contests.query.filter_by(id=t.eid).first()
                if c.team_limit == 1:
                    ctreg_mail(user=u, contest=c, regid=r.regid, cdept=dept[c.department - 1])
                else:
                    ctregteamleader_mail(user=u,contest=c,registration=r,cdept=dept[c.department - 1])
                r.mail = True;
                db.session.commit()
            responseObject = {
                'status':'success',
                'message':'Successfully registered'
            }
            return jsonify(responseObject)
        except Exception as e:
        	print(e)
        responseObject = {
        	'status':'success',
        	'message':'Successfully registered. But error in sending mail: '+str(e)
        }
        return jsonify(responseObject)
    elif t.cat is 3:
    	purchasee = User.query.filter_by(vid=t.vid).first()
    	try:
    		print("TRYING TO ADD")
    		ta = AddonTransactions.query.filter_by(trid=t.trid).first()
    		op = OtherPurchases(vid=t.vid,
                                pid=t.eid,
                                qty=ta.qty,
                                message='online_success',
                                bookid='ONLINE',
                                total=t.amount,
                                typ=1,
                                trid=t.trid
                                )
    		db.session.add(op)
    		db.session.commit()
    		print("ADDED TO DB")
    	except Exception as e:
    		print("Exception ", e)
    		responseObject = {
                'status':'failed',
                'message':'Not added to db'
            }
    		return jsonify(responseObject)
    	try:
    		products = ['Amritapuri: Proshow + Choreonite + Fashionshow','Outstation: Proshow + Choreonite + Fashionshow', 'General: Headbangers + Choreonite + Fashionshow', 'Choreonite + Fashionshow','T-Shirt','Amritapuri: All Tickets + T-Shirt','Outstation: All Tickets + T-Shirt','General: Headbangers + Choreonite + Fashionshow + T-Shirt']
    		print("PID = ", op.pid)
    		if op.pid == 100:
    			title = "TESTING"
    		else:
    			title = products[op.pid-1]
    		addon_pur(user=purchasee, title=title, purid=op.purid, count=op.qty)
    		op.mail = True;
    		db.session.commit()
    		responseObject = {
                'status':'success',
                'message':'transaction successful'
            }
    		print(" reached here 1")
    		return jsonify(responseObject)
    	except Exception as e:
    		print("Exception ", e)
    		responseObject = {
                'status':'success',
                'message':'Transaction successful. Mail not sent'
            }
    		return jsonify(responseObject)

def probber(t):
    payload = pay_data(tid=t.trid, amt=t.amount)
    print("Probber payload")
    print(payload)
    try:
        f = requests.post('https://payments.acrd.org.in/pay/doubleverifythirdparty', data=payload)
    except Exception as e:
        print(e)
        return 0
    print("Hello")
    j = f.text
    print("J = ", j)
    if not j:
        print("INSIDE IF")
        t.status = 'failed'
        if(t.cat == 1 and t.status=='failed'):
            print("Going to give back - 2")
            work = Workshops.query.filter_by(id=t.eid).first()
            work.rmseats = work.rmseats + 1
            db.session.commit()
        else:
            db.session.commit()
        return 'empty response'
    print("Text", j)
    try:
        k = json.loads(j)
        print("JSON", k)
        return response_data(k["data"])
    except Exception as e:
        print("No text ", e)
    # if j.get('response') is False:
    #     return j
    # # return "1"
    # return response_data(j.get('encdata'))
    # print(jsonify(j))
    return j

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
            return response_data(data)
        except Exception as e:
            print(e)
            responseObject = {
                'status':'failed',
                'message':'Exception occured : '+str(e)
            }
            return jsonify(responseObject)

@pay.route('/prob')
class probbing(Resource):
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
class massprobbing(Resource):
    # @authorizestaff(request, 4)
    def get(self):
        tlist = Transactions.query.filter(Transactions.status=="processing").filter(Transactions.trid<=2570).all()
        tlist.extend(Transactions.query.filter(Transactions.status=="acrd").filter(Transactions.trid<=2570).all())
        res = []
        print(tlist)
        for t in tlist:
            print(t)
            print(t.status)
            probber(t)

        return "Probing completed"

@pay.route('/custom')
class custom(Resource):
    def get(self):
        t = Transactions.query.filter(Transactions.trid==839).first()
        probber(t)
        return "completed"

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
