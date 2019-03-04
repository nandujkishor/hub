import datetime
import werkzeug.security
from flask import render_template, flash, redirect, request, url_for, jsonify,json
from app import app, db, api
from app.farer import authorizestaff, authorize
from config import Config
from app.models import Workshops, Talks, Contests, Registrations, User, Transactions
from app.mail import wkreg_mail, ctreg_mail, ctregteamleader_mail
from app.payments import workshopPay
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from flask_restplus import Resource, Api
from app.farer import auth_token
from datetime import date
from sqlalchemy.sql import func

events = api.namespace('events', description="Events management")

dept = ['CSE', 'ECE', 'ME', 'Physics', 'Chemisty', 'English', 'Biotech','BUG', 'Comm.', 'Civil', 'EEE', 'Gaming', 'Maths', 'Others']

@events.route('/workshops')
class events_workshops(Resource):

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON array
    # Sends list of all Workshops
    # Accessible to all users
    def get(self):
        try:
            workshops = Workshops.query.order_by('id').all()
            responseObject = []
            for workshop in workshops:
                responseObject.append({
                    'id':workshop.id,
                    'title':workshop.title,
                    'plink':workshop.plink,
                    'short':workshop.short,
                    'about':workshop.about,
                    'org': workshop.org,
                    'venue': workshop.venue,
                    'department':workshop.department,
                    'fee':workshop.fee,
                    'rules':workshop.rules,
                    'seats':workshop.seats,
                    'prereq':workshop.prereq,
                    'd1dur':workshop.d1dur,
                    'd2dur':workshop.d2dur,
                    'd3dur':workshop.d3dur,
                    'seats':workshop.seats,
                    'rmseats':workshop.rmseats
                })
        except Exception as e:
            print(e)
            responseObject = {
                'status':'failure',
                'Message':'Error Occured'
            }
        return jsonify(responseObject)

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status Code
    # Add Workshop
    # Permission: l3, l4 (Workshops)
    @api.doc(params = {
        'title':'Title',
        'plink':'Permanent Link',
        'short':'Short Description',
        'about':'Long Description in md',
        'prereq':'Prerequisites in md',
        'department':'Department',
        'vidurl':'Video URL',
        'company':'Company Name',
        'lead':'Company Lead',
        'contact':'Contact No',
        'incharge':'Incharge V-ID',
        'support':'Supporter V-ID',
        'fee':'Workshop Fee',
        'seats':'No of Seats',
        'companylogo':'Company Logo location',
        })
    @authorizestaff(request,"workshops", 3)
    def post(u, self):
        try:
            data = request.get_json()
            workshop = Workshops(
                title = data.get('title'),
                plink = data.get('plink'),
                short = data.get('short'),
                about = data.get('about'),
                department = data.get('department'),
                vidurl = data.get('vidurl'),
                org = data.get('org'),
                fee = data.get('fee'),
                rules = data.get('rules'),
                d1dur=data.get('d1dur'),
                d2dur=data.get('d2dur'),
                d3dur=data.get('d3dur'),
                venue=data.get('venue'),
                prereq = data.get('prereq'),
                incharge = data.get('incharge'),
                support = data.get('support'),
                seats = data.get('seats'),
                rmseats = data.get('seats')
            )
            # Put a log in Farerlog
            db.session.add(workshop)
            db.session.commit()
            responseObject={
                'status':'success',
                'message':' Workshop Details Succefully Posted'
            }
        except Exception as e:
            print(e)
            # Send email
            responseObject = {
                'status':'fail',
                'message':'Error occured'
            }
        return jsonify(responseObject)

@events.route('/workshops/count')
class w_count(Resource):
    def get(self):
        w = Workshops.query.all()
        return len(w)

@events.route('/workshops/<int:id>')
class events_workshops_indv(Resource):

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Array
    # Send details of the Workshop
    def get(self, id):
        try:
            auth_t = auth_token(request)
            if auth_t:
                resp = User.decode_auth_token(auth_t)
            workshop = Workshops.query.filter_by(id=id).first()
            if workshop is not None:
                responseObject = {
                    'id': workshop.id,
                    'title':workshop.title,
                    'plink':workshop.plink,
                    'short':workshop.short,
                    'about':workshop.about,
                    'department':workshop.department,
                    'vidurl':workshop.vidurl,
                    'fee':workshop.fee,
                    'org':workshop.org,
                    'venue':workshop.venue,
                    'incharge':workshop.incharge,
                    'support':workshop.support,
                    'seats':workshop.seats,
                    'pub':workshop.pub,
                    'rules':workshop.rules,
                    'd1dur':workshop.d1dur,
                    'd2dur':workshop.d2dur,
                    'd3dur':workshop.d3dur,
                    'prereq':workshop.prereq,
                    'rmseats':workshop.rmseats
                }
            else:
                responseObject ={
                    'status':'fail',
                    'message':'invalid workshop id'
                }
        except Exception as e:
                print(e)
                # Send email
                responseObject = {
                    'status':'fail',
                    'message':'Error occured'
                }
        return jsonify(responseObject)

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status Code
    # Edit details of the Workshop
    @api.doc(params = {
        'title':'Title',
        'plink':'Permanent Link',
        'short':'Short Description',
        'about':'Long Description in md',
        'prereq':'Prerequisites in md',
        'department':'Department',
        'vidurl':'Video URL',
        'org':'Organiser Name',
        'incharge':'Incharge V-ID',
        'support':'Supporter V-ID',
        'fee':'Workshop Fee',
        'seats':'No of Seats',
        })
    @authorizestaff(request,"workshops", 3)
    def put(u, self, id):
        try:
            workshop = Workshops.query.filter_by(id=id).first()
            if workshop is not None:

                data = request.get_json()

                workshop.title=data.get('title')
                workshop.about=data.get('about')
                workshop.short=data.get('short')
                workshop.rules=data.get('rules')
                workshop.prereq=data.get('prereq')
                workshop.seats=data.get('seats')
                workshop.incharge=data.get('incharge')
                workshop.support=data.get('support')
                workshop.org=data.get('org')
                workshop.fee=data.get('fee')
                workshop.venue=data.get('venue')
                workshop.d1dur=data.get('d1dur')
                workshop.d2dur=data.get('d2dur')
                workshop.d3dur=data.get('d3dur')
                workshop.department=data.get('department')

                db.session.commit()
                responseObject = {
                    'status':'success',
                    'message':'workshop details edited successfully'
                }
            else:
                responseObject = {
                    'status':'failed',
                    'message':'invalid workshop id'
                }
        except Exception as e:
            print(e)
            # Send email
            responseObject = {
                    'status':'fail',
                    'message':'Error occured'
            }
        return jsonify(responseObject)

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status Code
    # Delete Workshop
    @authorizestaff(request, "workshops", 3)
    def delete(u, self, id):
        try:
            workshop = Workshops.query.filter_by(id=id).first()
            if workshop is not None:
                db.session.delete(workshop)
                db.session.commit()
                responseObject = {
                    'status':'success',
                    'message':'workshop deleted'
                }
            else:
                responseObject = {
                    'status':'failed',
                    'message':'Invalid workshop id'
                }
        except Exception as e:
            print(e)
            # Send email
            responseObject = {
                    'status':'fail',
                    'message':'Error occured'
            }
        return jsonify(responseObject)

@events.route('/contests')
class events_contests(Resource):
    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Array
    # Send list of all contests
    def get(self):
        try:
            contests = Contests.query.order_by('id').all()
            responseObject = []
            for contest in contests:
                responseObject.append({
                    'id':contest.id,
                    'title':contest.title,
                    'department':contest.department,
                    'about':contest.about,
                    'prize1':contest.prize1,
                    'prize2':contest.prize2,
                    'prize3':contest.prize3,
                    'short':contest.short,
                    'pworth':contest.pworth,
                    'd1dur':contest.d1dur,
                    'd2dur':contest.d2dur,
                    'd3dur':contest.d3dur,
                    'venue':contest.venue,
                    'team_limit':contest.team_limit,
                    'fee':contest.fee,
                    'incharge':contest.incharge,
                    'support':contest.support,
                    'rules':contest.rules,
                    'prereq':contest.prereq,
                })
            print(responseObject)
        except Exception as e:
                print(e)
                # Send email
                responseObject = {
                    'status':'fail',
                    'message':'Error occured'
                }
        return jsonify(responseObject)

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status
    # Add Contest
    @api.doc(params={
        'title':'Title',
        'short':'Short Description',
        'about':'Long Description in md',
        'rules':'Rules',
        'prereq':'Prerequisite in md',
        'organiser':'Organiser Name',
        'department':'Department No.',
        'prize1':'Prize 1',
        'prize2':'Prize 2',
        'prize3':'Prize 3',
        'pworth':'Total Prize Worth',
        'fee':'Entry Fee',
        'team_limit':'No of Team Members',
        'expense':'Expenses for internal use',
        'incharge':'Incharge V-ID',
    })
    @authorizestaff(request,"contests", 3)
    def post(u, self):
        try:
            data = request.get_json()
            contest = Contests(
                title = data.get('title'),
                short = data.get('short'),
                pworth = data.get('pworth'),
                department = data.get('department'),
                team_limit=data.get('team_limit'),
                support=data.get('support'),
                about=data.get('about'),
                rules=data.get('rules'),
                d1dur=data.get('d1dur'),
                d2dur=data.get('d2dur'),
                d3dur=data.get('d3dur'),
                venue=data.get('venue'),
                prereq=data.get('prereq'),
                prize1=data.get('prize1'),
                prize2=data.get('prize2'),
                prize3=data.get('prize3'),
                fee=data.get('fee'),
                incharge=data.get('incharge')
            )
            db.session.add(contest)
            db.session.commit()
            responseObject={
                'status':'success',
                'message':' Contest Details Succefully Posted'
            }
        except Exception as e:
            print(e)
            # Send email
            responseObject = {
                'status':'fail',
                'message':'Error occured'
            }
        return jsonify(responseObject)

@events.route('/contests/count')
class c_count(Resource):
    def get(self):
        c = Contests.query.all()
        return len(c)

@events.route('/contests/<int:id>')
class events_contests_indv(Resource):

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Array
    # Send details of the Contest
    def get(self, id):
        try:
            contest = Contests.query.filter_by(id=id).first()
            if contest is not None:
                responseObject = {
                    'id': contest.id,
                    'title':contest.title,
                    'department':contest.department,
                    'about':contest.about,
                    'prize1':contest.prize1,
                    'prize2':contest.prize2,
                    'prize3':contest.prize3,
                    'short':contest.short,
                    'pworth':contest.pworth,
                    'd1dur':contest.d1dur,
                    'd2dur':contest.d2dur,
                    'd3dur':contest.d3dur,
                    'team_limit':contest.team_limit,
                    'fee':contest.fee,
                    'venue':contest.venue,
                    'incharge':contest.incharge,
                    'support':contest.support,
                    'rules':contest.rules,
                    'prereq':contest.prereq,
                }
            else:
                responseObject ={
                    'status':'fail',
                    'message':'invalid contest id'
                }
        except Exception as e:
                print(e)
                # Send email
                responseObject = {
                    'status':'fail',
                    'message':'Error occured'
                }
        return jsonify(responseObject)

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status Code
    # Edit details of the Contest
    @api.doc(params={
        'title':'Title',
        'short':'Short Description',
        'about':'Long Description in md',
        'rules':'Rules',
        'prereq':'Prerequisite in md',
        'organiser':'Organiser Name',
        'prize1':'Prize 1',
        'prize2':'Prize 2',
        'prize3':'Prize 3',
        'pworth':'Total Prize Worth',
        'fee':'Entry Fee',
        'team_limit':'No of Team Members',
        'expense':'Expenses for internal use',
        'incharge':'Incharge V-ID',
    })
    @authorizestaff(request,"contests", 3)
    def put(u, self, id):
        try:
            contest = Contests.query.filter_by(id=id).first()
            if contest is not None:

                data = request.get_json()

                contest.title=data.get('title')
                contest.short=data.get('short')
                contest.about=data.get('about')
                contest.rules=data.get('rules')
                contest.prereq=data.get('prereq')
                contest.pworth=data.get('pworth')
                contest.fee=data.get('fee')
                contest.d1dur=data.get('d1dur')
                contest.d2dur=data.get('d2dur')
                contest.d3dur=data.get('d3dur')
                contest.venue=data.get('venue')
                contest.incharge=data.get('incharge')
                contest.support=data.get('support')
                contest.department=data.get('department')
                contest.prize1=data.get('prize1')
                contest.prize2=data.get('prize2')
                contest.prize3=data.get('prize3')
                contest.team_limit=data.get('team_limit')

                db.session.commit()
                responseObject = {
                    'status':'success',
                    'message':'Contest details edited successfully'
                }
            else:
                responseObject = {
                    'status':'failed',
                    'message':'invalid workshop id'
                }
        except Exception as e:
            print(e)
            # Send email
            responseObject = {
                    'status':'fail',
                    'message':'Error occured'
            }
        return jsonify(responseObject)

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status Code
    # Delete Contest
    @authorizestaff(request,"contests", 3)
    def delete(u, self, id):
        try:
            contest = Contests.query.filter_by(id=id).first()
            if contest is not None:
                db.session.delete(contest)
                db.session.commit()
                responseObject = {
                    'status':'success',
                    'message':'contest deleted'
                }
            else:
                responseObject = {
                    'status':'failed',
                    'message':'Invalid contest id'
                }
        except Exception as e:
            print(e)
            # Send email
            responseObject = {
                    'status':'fail',
                    'message':'Error occured'
            }
        return jsonify(responseObject)

@events.route('/talks')
class events_talks(Resource):

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status
    # List all the Talks
    def get(self):
        try:
            talks = Talks.query.all()
            responseObject = []
            for talk in talks:
                responseObject.append({
                    'id':talk.id,
                    'title':talk.title,
                    'person':talk.person,
                    'fee':talk.fee
                })
        except Exception as e:
                print(e)
                # Send email
                responseObject = {
                    'status':'fail',
                    'message':'Error occured'
                }
        return jsonify(responseObject)

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status
    # Add Talk
    @api.doc(params={
        'id':'Talk ID',
        'plink':'Permanent Link',
        'short':'Short Description',
        'about':'About Description',
        'person':'Name of the Person',
        'desig':'Designation',
        'contact':'Contact No',
        'picurl':'Picture of the Talk',
        'ppicurlsm':'Picture of the person small',
        'ppicurllr':'Picture of the person large',
        'fee':'fee for the talk',
        'incharge':'Incharge V-ID'
    })
    @authorizestaff(request,"talks", 3)
    def post(u, self):
        try:
            data = request.get_json()
            talk = Talks(
                title=data.get('title'),
                short=data.get('short'),
                person=data.get('person'),
                desig=data.get('desig'),
                fee=data.get('fee'),
                incharge=data.get('incharge')
            )
            db.session.add(talk)
            db.session.commit()
            responseObject={
                'status':'success',
                'message':' Talk Details Succefully Posted'
            }
        except Exception as e:
            print(e)
            # Send email
            responseObject = {
                'status':'fail',
                'message':'Error occured'
            }
        return jsonify(responseObject)

@events.route('/talks/count')
class w_count(Resource):
    def get(self):
        t = Talks.query.all()
        return len(t)

@events.route('/talks/<int:id>')
class events_talks_indv(Resource):

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Array
    # Send details of the Talk
    def get(self, id):
        try:
            talk = Talks.query.filter_by(id=id).first()
            if talk is not None:
                responseObject = {
                    'title':talk.title,
                    'short':talk.short,
                    'person':talk.person,
                    'desig':talk.desig,
                    'fee':talk.fee,
                    'incharge':talk.incharge,
                }
            else:
                responseObject ={
                    'status':'fail',
                    'message':'invalid contest id'
                }
        except Exception as e:
                print(e)
                # Send email
                responseObject = {
                    'status':'fail',
                    'message':'Error occured'
                }
        return jsonify(responseObject)

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status Code
    # Edit details of the Talk
    @api.doc(params={
        'id':'Talk ID',
        'plink':'Permanent Link',
        'short':'Short Description',
        'about':'About Description',
        'person':'Name of the Person',
        'desig':'Designation',
        'contact':'Contact No',
        'picurl':'Picture of the Talk',
        'ppicurlsm':'Picture of the person small',
        'ppicurllr':'Picture of the person large',
        'fee':'fee for the talk',
        'incharge':'Incharge V-ID'
    })
    @authorizestaff(request,"talks", 3)
    def put(u, self, id):
        try:
            talk = Talks.query.filter_by(id=id).first()
            if talk is not None:
                data = request.get_json()
                talk.title=data.get('title')
                talk.short=data.get('short')
                talk.person=data.get('person')
                talk.desig=data.get('desig')
                talk.fee=data.get('fee')
                talk.incharge=data.get('incharge')
                db.session.commit()
                responseObject = {
                    'status':'success',
                    'message':'Contest details edited successfully'
                }
            else:
                responseObject = {
                    'status':'failed',
                    'message':'invalid workshop id'
                }
        except Exception as e:
            print(e)
            # Send email
            responseObject = {
                    'status':'fail',
                    'message':'Error occured'
            }
        return jsonify(responseObject)

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status Code
    # Delete Talk
    @authorizestaff(request,"talks", 3)
    def delete(u, self, id):
        try:
            talk = Talks.query.filter_by(id=id).first()
            if talk is not None:
                db.session.delete(talk)
                db.session.commit()
                responseObject = {
                    'status':'success',
                    'message':'Talk deleted'
                }
            else:
                responseObject = {
                    'status':'failed',
                    'message':'Invalid talk id'
                }
        except Exception as e:
            print(e)
            # Send email
            responseObject = {
                    'status':'fail',
                    'message':'Error occured'
            }
        return jsonify(responseObject)

@events.route('/registration')
class events_registration(Resource):

    @authorize(request)
    # Endpoint for getting registered events
    def get(user, self):
        try:
            reg = Registrations.query.filter_by(id=user.vid)
            responseObject = []
            for r in reg:
                if r.cat == 1:
                    e = Workshops.query.filter_by(id=r.eid).first()
                elif r.cat == 2:
                    e = Contests.query.filter_by(id=r.eid).first()
                if e is not None:
                    responseObject.append({
                        'regid':r.regid,
                        'vid':r.vid,
                        'regby':r.regby,
                        'typ':r.typ,
                        'registime':r.registime,
                        'cat':r.cat,
                        'eid':r.eid,
                        'title':e.title
                    })
            return jsonify(responseObject)
        except Exception as e:
            print(e)
            responseObject = {
                'status':'failure',
                'Message':'Exception occured. '
            }
        return jsonify(responseObject)

    @api.doc(params={
        'cat':'Event Catagory',
        'eid':'Event ID',
        'tid':'Team ID (Only for joining a team for a team competition)'
    })
    @authorize(request)
    # This route is for registrations through payment gateway
    def post(user, self):
        data = request.get_json()
        r = Registrations.query.filter_by(cat=data.get('cat'), eid=data.get('eid'), vid=user.vid).first()
        print(r)
        if r is not None:
            responseObject = {
                'status':'fail',
                'message':'User already registered'
            }
            return jsonify(responseObject)
        try:
            print(data)
            #Workshop Registration
            if data.get('cat') == 1:
                w = Workshops.query.filter_by(id=data.get('eid')).first()
                if w is not None:
                    try:
                        if w.rmseats is 0:
                            responseObject = {
                                'status':'fail',
                                'message':'No seats remaining'
                            }
                            return jsonify(responseObject)
                        w.rmseats = w.rmseats - 1
                        db.session.commit()
                        # tr = Transactions(cat=1, eid=w.id, vid=user.vid)
                        # db.session.add(tr)
                        # db.session.commit()
                        # return workshopPay(w, user)
                        # Start a 20 minute scheduler to increment the workshop slot
                        # in case the transaction got an issue / is pending.
                        # In all other cases, take the decision on return of endpoint
                    except Exception as e:
                        print(e)
                        responseObject = {
                            'status':'fail',
                            'message':'No seats remaining.'
                        }
                        return jsonify(responseObject)
                    try:
                        if w.fee == 0 or w.fee is None:
                            responseObject = {
                                'status':'registered',
                                'message':'Successfully registered for the workshop'
                            }
                            return jsonify(responseObject)
                        return workshopPay(w, user)
                    except Exception as e:
                        print(e)
                        responseObject = {
                            'status':'fail',
                            'message': str(e)
                        }
                else:
                    responseObject = {
                        'status':'failure',
                        'message':'Invalid workshop ID'
                    }
                return jsonify(responseObject)
            elif data.get('cat') == 2:
                c = Contests.query.filter_by(id=data.get('eid')).first()
                if c is not None:
                    if c.team_limit is 1:
                        r = Registrations(vid=user.id, cat=2, eid=data.get('eid'))
                        db.session.add(r)
                        db.session.commit()
                        print("Single member team registration successful")
                        responseObject={
                            'status':'success',
                            'message':'Registration Success'
                        }
                    elif data.get('tid') is None:
                        print("Team id generation")
                        r = Registrations(vid=user.vid, cat=2, eid=data.get('eid'))
                        db.session.add(r)
                        db.session.commit()
                        tid = werkzeug.security.pbkdf2_hex(str(r.regid), "F**k" ,iterations=50000, keylen=3)
                        # SHA:256 hashing
                        print("Team ID", tid)
                        r.tid = tid
                        db.session.commit()
                        # Send email with Team ID
                        ctregteamleader_mail(user=user, contest=c, registration=r, cdept=dept[c.department-1])
                        responseObject={
                            'status':'success',
                            'message':'Registration Success. Registration ID: '+str(tid)
                        }
                    else:
                        team = Registrations.query.filter_by(cat=2, eid=data.get('eid'), tid=data.get('tid')).count()
                        if count < c.team_limit:
                            r = Registrations(vid=u.vid, cat=2, eid=data.get('eid'), tid=form.data.get('eid'))
                            db.session.add(r)
                            db.session.commit()
                            responseObject = {
                                'status':'success',
                                'message':'Registration Success'
                            }
                        else:
                            responseObject={
                                'status':'failure',
                                'message':'Team is full'
                            }
                else:
                    responseObject = {
                        'status':'failure',
                        'message':'Invalid Event ID'
                    }
                return jsonify(responseObject)
        except Exception as e:
            print(e)
            responseObject={
                'status':'Failure',
                'message':'Error Occured'
            }
            return jsonify(responseObject)

@events.route('/registration/all')
class registration_all(Resource):

    # Endpoint for getting registered events
    @authorizestaff(request,"registration",3)
    def get(user, self):
        try:
            reg = Registrations.query.filter_by()
            responseObject = []
            for r in reg:
                if r.cat == 1:
                    e = Workshops.query.filter_by(id=r.eid).first()
                elif r.cat == 2:
                    e = Contests.query.filter_by(id=r.eid).first()
                if e is not None:
                    responseObject.append({
                        'regid':r.regid,
                        'vid':r.vid,
                        'regby':r.regby,
                        'typ':r.typ,
                        'registime':r.registime,
                        'cat':r.cat,
                        'eid':r.eid,
                        'title':e.title,
                        'fee':e.fee
                    })
            return jsonify(responseObject)
        except Exception as e:
            print(e)
            responseObject = {
                'status':'failure',
                'Message':'Exception occured. '
            }
        return jsonify(responseObject)

@events.route('/registration/stats')
class registration_stats(Resource):

    # Endpoint for getting registrartion sts
    @authorizestaff(request,"registration",3)
    def get(user, self):
        try:
            reg = Registrations.query.filter_by(cat=1)
            totalwcost = 0
            totalw = 0
            for r in reg:
                totalwcost += r.amount
                totalw +=1

            reg = Registrations.query.filter_by(cat=2)
            totalccost = 0
            totalc = 0
            for r in reg:
                totalccost += r.amount
                totalc +=1

            total = totalwcost + totalccost
            responseObject = {
                'total':total,
                'totalc':totalc,
                'totalw':totalw,
                'totalccost':totalccost,
                'totalwcost':totalwcost
            }
            return jsonify(responseObject)
        except Exception as e:
            print(e)
            responseObject = {
                'status':'failure',
                'Message':'Exception occured. '
            }
        return jsonify(responseObject)


@events.route('/registration/workshops')
class events_registration(Resource):

    @authorize(request)
    # Endpoint for getting user registered events
    def get(user, self):
        try:
            responseObject=[]
            reg = Registrations.query.filter_by(vid=user.vid,cat=1)
            for r in reg:
                e = Workshops.query.filter_by(id=r.eid).first()
                if e is not None:
                    responseObject.append({
                        'regid':r.regid,
                        'typ':r.typ,
                        'registime':r.registime,
                        'eid':r.eid,
                        'title':e.title,
                        'fee':r.amount
                    })
            return jsonify(responseObject)
        except Exception as e:
            print(e)
            responseObject = {
                'status':'failure',
                'Message':'Exception occured. '
            }
            return jsonify(responseObject)

@events.route('/registration/contests')
class events_registration(Resource):

    @authorize(request)
    # Endpoint for getting user registered contests
    def get(user, self):
        try:
            responseObject=[]
            reg = Registrations.query.filter_by(vid=user.vid,cat=2)
            for r in reg:
                e = Contests.query.filter_by(id=r.eid).first()
                if e is not None:
                    responseObject.append({
                        'regid':r.regid,
                        'typ':r.typ,
                        'registime':r.registime,
                        'eid':r.eid,
                        'title':e.title,
                        'fee':r.amount
                    })
            return jsonify(responseObject)
        except Exception as e:
            print(e)
            responseObject = {
                'status':'failure',
                'Message':'Exception occured. '
            }
        return jsonify(responseObject)

@events.route('/registration/staff')
class registration_through_staff(Resource):
    @authorizestaff(request,"registration", 3)
    def get(user, self):
        l = Registrations.query.filter_by(mode=2).all()
        r = []
        for i in l:
            r.append({
                'regid':l.regid,
                'vid':l.vid,
                'cat':l.cat,
                'eid':l.eid,
                'registime':l.registime
            })
        return jsonify(r)

    @authorizestaff(request, "registration", 3)
    def post(user, self):
        data = request.get_json()
        if data.get('vid') is None or data.get('cat') is None or data.get('eid') is None:
            responseObject = {
                'status':'fail',
                'message':'Data Inadequate'
            }
            return jsonify(responseObject)
        regu = User.query.filter_by(vid=data.get('vid')).first()
        if regu is None:
            responseObject = {
                'status':'fail',
                'message':'User does not exist'
            }
            return jsonify(responseObject)
        registered = Registrations.query.filter_by(vid=data.get('vid'),
                                                            cat=data.get('cat'),
                                                            eid=data.get('eid')
                                                            ).first()
        if registered is not None:
            responseObject = {
                'status':'fail',
                'message':'User already registered for the event'
            }
            return(responseObject)
        if data.get('cat') is 1:
            w = Workshops.query.filter_by(id=data.get('eid')).first()
            r = None
            if w is not None:
                try:
                    w.rmseats = w.rmseats - 1
                    r = Registrations(vid=data.get('vid'),
                                    cat=data.get('cat'),
                                    eid=data.get('eid'),
                                    typ=2,
                                    regby=user.vid,
                                    amount=w.fee
                                    )
                    db.session.add(r)
                    db.session.commit()
                    print("Successful")
                except Exception as e:
                    print(e)
                    responseObject = {
                        'status':'fail',
                        'message':'No seats remaining'
                    }
                    return jsonify(responseObject)
                try:
                    user = User.query.filter_by(vid=r.vid).first()
                    dept = ['CSE', 'ECE', 'ME', 'Physics', 'Chemisty', 'English', 'Biotech','BUG', 'Comm.', 'Civil', 'EEE', 'Gaming', 'Maths', 'Others']
                    wkreg_mail(user=user, workshop=w, regid=r.regid, wdept=dept[w.department - 1])
                    r.mail = True;
                    db.session.commit();
                    responseObject = {
                        'status':'success',
                        'message':'User successfully registered'
                    }
                    return jsonify(responseObject)
                except Exception as e:
                    responseObject = {
                        'status':'success',
                        'message':'User successfully registered. Exception encountered. Please mail or call the web team (Error: '+str(e)+')'
                    }
                    return jsonify(responseObject)
            responseObject = {
                'status':'fail',
                'message':'Workshop ID incorrect'
            }
            return jsonify(responseObject)
        elif data.get('cat') is 2:
            c = Contests.query.filter_by(id=data.get('eid')).first()
            r = None
            if c is not None:
                try:
                    r = Registrations(vid=data.get('vid'),
                                    cat=data.get('cat'),
                                    eid=data.get('eid'),
                                    typ=2,
                                    regby=user.vid,
                                    amount=c.fee
                                    )
                    db.session.add(r)
                    db.session.commit()
                    print("Successful")
                except Exception as e:
                    print(e)
                    responseObject = {
                        'status':'fail',
                        'message':'Some exception occured. Contact web team (Error code: x31as432. Error: '+e+')'
                    }
                    return jsonify(responseObject)
                try:
                    dept = ['CSE', 'ECE', 'ME', 'Physics', 'Chemisty', 'English', 'Biotech','BUG', 'Comm.', 'Civil', 'EEE', 'Gaming', 'Maths', 'Others']
                    ctreg_mail(user=user, contest=c, regid=r.regid, cdept=dept[c.department - 1])
                    r.mail = True;
                    db.session.commit()
                    responseObject = {
                        'status':'success',
                        'message':'User successfully registered'
                    }
                    return jsonify(responseObject)
                except Exception as e:
                    print(e)
                    responseObject = {
                        'status':'success',
                        'message':'User registered. Exception occured. Please call or mail web team (Error: '+str(e)+')'
                    }
                    return jsonify(responseObject)
            responseObject = {
                'status':'fail',
                'message':'Contest does not exist'
            }
            return jsonify(responseObject)
        responseObject = {
            'status':'fail',
            'message':'Some exception occured. Contact web team (Error code: w31as432t)'
        }
        return jsonify(responseObject)

@events.route('/registration/check')
class events_registration_check(Resource):

    # End point for getting total registrations made by a volunteer
    @api.doc(params={
        'vid':'Vidyut ID',
        'start':'Start Date',
        'end':'End Date'
            })
    # @authorizestaff(request,"registrations", 3)
    def get(self):
        try:
            data = request.get_json()
            start = datetime.datetime.strptime(data.get('start')+' 00:00:00', '%d-%m-%Y %H:%M:%S')
            end = datetime.datetime.strptime(data.get('end')+' 23:59:59', '%d-%m-%Y %H:%M:%S')
            if start<=end:
                regs = db.session.query(Registrations).filter(Registrations.regby==data.get('vid')).\
                        filter(Registrations.registime>=start).filter(Registrations.registime<=end).all()
                if regs is not None:
                    responseObject = []
                    totalsum=0
                    for reg in regs:
                        if reg.cat == 1:
                            w = Workshops.query.filter_by(id = reg.eid).first()
                            if w is not None:
                                totalsum+=w.fee
                                responseObject.append({
                                    'regid':reg.regid,
                                    'vid':reg.vid,
                                    'cat':reg.cat,
                                    'catn':'Workshop',
                                    'eid':reg.eid,
                                    'ename':w.title,
                                    'fee':reg.amount
                                })
                        elif reg.cat == 2:
                            c = Contests.query.filter_by(id = reg.eid).first()
                            if c is not None:
                                totalsum+=c.fee
                                responseObject.append({
                                    'regid':reg.regid,
                                    'vid':reg.vid,
                                    'cat':reg.cat,
                                    'catn':'Contest',
                                    'eid':reg.eid,
                                    'ename':c.title,
                                    'fee':reg.amount
                                })
                    responseObject = {
                            'data': responseObject,
                            'totalsum': totalsum
                    }
                    return jsonify(responseObject)
                else:
                    responseObject={
                        'status': 'fail',
                        'message':'No registraions done in between these dates'
                    }
            else:
                responseObject={
                    'status':'fail',
                    'message':'Invalid Dates'
                }
            return jsonify(responseObject)
        except Exception  as e:
            print(e)
            responseObject = {
                'status':'fail',
                'message':'Error Occured'
            }
            return jsonify(responseObject)

@events.route('/registration/workshops/<int:id>')
class events_registration_workshop(Resource):

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Array
    # Send details of the Talk
    def get(self, id):
        try:
            reg = Registrations.query.filter_by(cat=1,eid=id)
            if reg is not None:
                responseObject = []
                for regs in reg:
                    responseObject.append({
                        'regid':regs.regid,
                        'vid':regs.vid,
                        'cat':regs.cat,
                        'eid':regs.eid,
                        'pay_completed':regs.pay_completed,
                    })
            else:
                responseObject ={
                    'status':'fail',
                    'message':'invalid contest id'
                }
        except Exception as e:
                print(e)
                # Send email
                responseObject = {
                    'status':'fail',
                    'message':'Error occured'
                }
        return jsonify(responseObject)

@events.route('/registration/contests/<int:id>')
class events_registration_contests(Resource):

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Array
    # Send details of the Talk
    def get(self, id):
        try:
            reg = Registrations.query.filter_by(cat=2,eid=id)
            if reg is not None:
                responseObject = []
                for regs in reg:
                    responseObject.append({
                        'regid':regs.regid,
                        'vid':regs.vid,
                        'cat':regs.cat,
                        'eid':regs.eid,
                        'tid':regs.tid,
                        'pay_completed':regs.pay_completed,
                    })
            else:
                responseObject ={
                    'status':'fail',
                    'message':'invalid contest id'
                }
        except Exception as e:
                print(e)
                # Send email
                responseObject = {
                    'status':'fail',
                    'message':'Error occured'
                }
        return jsonify(responseObject)

@events.route('/registration/talks/<int:id>')
class events_registration_talks(Resource):

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Array
    # Send details of the Talk
    def get(self, id):
        try:
            reg = Registrations.query.filter_by(cat=3,eid=id)
            if reg is not None:
                responseObject = []
                for regs in reg:
                    responseObject.append({
                        'regid':regs.regid,
                        'vid':regs.vid,
                        'cat':regs.cat,
                        'eid':regs.eid,
                        'pay_completed':regs.pay_completed,
                    })
            else:
                responseObject ={
                    'status':'fail',
                    'message':'invalid contest id'
                }
        except Exception as e:
                print(e)
                # Send email
                responseObject = {
                    'status':'fail',
                    'message':'Error occured'
                }
        return jsonify(responseObject)
