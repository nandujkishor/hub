import datetime
from flask import render_template, flash, redirect, request, url_for, jsonify
from app import app, db, api
from config import Config
from app.models import Workshops,Talks,Contests
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from flask_restplus import Resource, Api

events = api.namespace('events', description="Event management")

@events.route('/workshops/')
class events_workshops(Resource):

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON array
    # Sends list of all Workshops
    @api.doc('List of all Workshops')
    def get(self):
        workshops = Workshops.query.all()
        return jsonify(Workshops.serialize_list(workshops))

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status Code
    # Add Workshop
    @api.doc('Workshop addition')
    def post(self):
        data = request.get_json()
        workshop = Workshops(title=data.get('title'),
                    about=data.get('description'),
                    company=data.get('compname'),
                    fee=data.get('fee'),
                    instructor=data.get('instructor'),
                    abins = data.get('abins')
                    )
        db.session.add(workshop)
        db.session.commit()
        return jsonify(201)

@events.route('/workshops/<int:id>/')
class events_workshops_indv(Resource):

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Array
    # Send details of the Workshop
    @api.doc('Details of the Workshop')
    def get(self, id):
        workshop = Workshops.query.filter_by(id=id).first()
        return jsonify(workshop.serialize())

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status Code
    # Edit details of the Workshop
    @api.doc('Edit details of the Workshop')
    def put(self, id):
        data = request.get_json()
        workshop = Workshops.query.filter_by(id=id).first()
        workshop.title=data.get('title')
        workshop.about=data.get('discription')
        workshop.fee=data.get('fee')
        workshop.instructor=data.get('instructor')
        workshop.abins=data.get('abins')
        db.session.commit()
        return jsonify(200)

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status Code
    # Delete Workshop
    @api.doc('Delete Workshop')
    def delete(self, id):
        workshop = Workshops.query.filter_by(id=id).first()
        if workshop is not None:
            db.session.delete(workshop)
            db.session.commit()
            return jsonify(200)
        return jsonify(406)

@events.route('/talks/')
class events_talks(Resource):

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Array
    # Send list of all Talks
    @api.doc('List of all talks')
    def get(self):
        talks = Talks.query.all()
        return jsonify(Talks.serialize_list(talks))

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status Code
    # Add Talk
    @api.doc('Talk addition')
    def post(self):
        data = request.get_json()
        talk = Talks(title=data.get('title'),
                    descr=data.get('description'),
                    person=data.get('person'),
                    amt=data.get('amount')
                    )
        db.session.add(talk)
        db.session.commit()
        print(talk)
        return jsonify(201)

@events.route('/talks/<int:id>/')
class events_talks_indv(Resource):

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Array
    # Send details of the Talk
    @api.doc('Detials of the talk')
    def get(self, id):
        talk = Talks.query.filter_by(id=id).first()
        return jsonify(talk.serialize())

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status Code
    # Edit details of the Talk
    @api.doc('Edit details of the Talk')
    def put(self, id):
        data=request.get_json()
        talk = Talks.query.filter_by(id=id).first()
        talk.title=data.get('title')
        talk.descr=data.get('description')
        talk.person=data.get('person')
        talk.amt=data.get('amount')
        db.session.commit()
        return jsonify(200)

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status Code
    # Delete Talk
    @api.doc('Delete Talk')
    def delete(self, id):
        talk = Talks.query.filter_by(id=id).first()
        if talk is not None:
            db.session.delete(talk)
            db.session.commit()
            return jsonify(200)

        return jsonify(406)

@events.route('/contests/')
class events_contests(Resource):
    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Array
    # Send list of all contests
    @api.doc('List of all Contests')
    def get(self):
        contests = Contests.query.all()
        return jsonify(Contests.serialize_list(contest))

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status
    # Add Talk
    @api.doc('Contest addition')
    def post(self):
        data = request.get_json()
        contest = Contests(title=data.get('title'),
                    about=data.get('description'),
                    task=data.get('task'),
                    pricing=data.get('pricing'),
                    team_limit=data.get('team_limit'),
                    expense=data.get('expense'),
                    incharge=data.get('incharge')
                    )
        db.session.add(contest)
        db.session.commit()
        print(contest)
        return jsonify(201)

@events.route('/talks/<int:id>/')
class events_contests_indv(Resource):

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Array
    # Send details of the Contest
    @api.doc('Detials of the Contest')
    def get(self, id):
        contest = Contests.query.filter_by(id=id).first()
        return jsonify(contest.serialize())

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status Code
    # Edit details of the Contest
    @api.doc('Edit details of the Contest')
    def put(self, id):
        data=request.get_json()
        contest = Contests.query.filter_by(id=id).first()
        contest.title=data.get('title')
        contest.about=data.get('description')
        contest.task=data.get('task')
        contest.pricing=data.get('pricing')
        contest.team_limit=data.get('team_limit')
        contest.expense=data.get('expense')
        contest.incharge=data.get('incharge')
        db.session.commit()
        return jsonify(200)

    # API Params: JSON([Standard])
    # Standard: IP, Sender ID
    # Returns: JSON Status Code
    # Delete Contest
    @api.doc('Delete Contest')
    def delete(self, id):
        contest = Contests.query.filter_by(id=id).first()
        if talk is not None:
            db.session.delete(contest)
            db.session.commit()
            return jsonify(200)

        return jsonify(406)
