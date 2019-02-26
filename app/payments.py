import os
import qrcode
import datetime
import hashlib
from Crypto.Cipher import AES
import sys
import base64
from Crypto.Cipher import AES
from flask import render_template, flash, redirect, request, url_for, jsonify
from app import app, db, api
from app.models import User, Staff
from config import Config
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from flask_restplus import Resource, Api

pay = api.namespace('pay', description="Payments management")

key = "WEGSNGOXHEUDEEDD"
iv = "3564234432724374"

class AESCipher(object):
    def __init__(self, key):
        self.bs = 16
        self.cipher = AES.new(key, AES.MODE_CBC, iv)

    def encrypt(self, raw):
        raw = self._pad(raw)
        encrypted = self.cipher.encrypt(raw)
        encoded = base64.b64encode(encrypted)
        return str(encoded, 'utf-8')

    def decrypt(self, raw):
        decoded = base64.b64decode(raw)
        decrypted = self.cipher.decrypt(decoded)
        return str(self._unpad(decrypted), 'utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]

@pay.route('/authorize', methods=['GET', 'POST'])
def payauth():
    # return "Inside authorize"
    # payload = {
    #     'code': request.form.get('code'),
    #     'data': request.form.get('data')
    # }
    try:
        if request.method == 'POST':
            return request.form.get('data')
    except Exception as e:
        return "Exception occured : " + str(e)

    return ("Check localhost")

@pay.route('/testing/', methods=['POST', 'GET'])
def payment():
    plaintext = "transactionId=VIDYUTTEST10|amount=1|purpose=VIDYUT19TEST|currency=inr"
    result = hashlib.md5(plaintext.encode())
    result = result.hexdigest()
    print("md5",result)
    pwc = plaintext + "|checkSum=" + result
    print("before aes",pwc)
    cipher = AESCipher(key)
    encd = cipher.encrypt(pwc)
    print("after aes", encd)
    return encd

@pay.route('/callback/', methods=['POST', 'GET'])
def callback():
    print("Inside callback")
    print(request.args)
    return "Check terminal"

@pay.route('/check/')
def check_pay():
    return render_template('payment.html')
