from app import db
import jwt

class User(UserMixin, db.Model, Serializer):
    vid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.String(30))
    email = db.Column(db.String(120), unique=True)
    fname = db.Column(db.String(30))
    lname = db.Column(db.String(30))
    ppic = db.Column(db.String(200))
    course = db.Column(db.String(200))
    major = db.Column(db.String(200))
    sex = db.Column(db.Integer)
    year = db.Column(db.Integer)
    college = db.Column(db.Integer)
    institution = db.Column(db.String(100))
    school = db.Column(db.Boolean)
    # In case college is not listed.
    phno = db.Column(db.String(10))
    # Levels: power directly propotional to number
    detailscomp = db.Column(db.Boolean)
    educomp = db.Column(db.Boolean)
    time_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    lastseen = db.Column(db.DateTime)

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def super(self):
        return self.email=="nandujkishor@gmail.com" or self.email=="aswanth366@gmail.com"

    def encode_auth_token(self, user_id):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            # Setup emailing to email the occured exception
            return e

class College(db.Model, Serializer):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # caid = db.Column(db.Integer)
    district = db.Column()
    state = db.
    # Campus Ambassador user ID for the institution

    def __repr__(self):
        return '<College {}>'.format(self.name)

class Talks(db.Model, Serializer):
    id = db.Column(db.Integer, primary_key=True)
    descr = db.Column(db.String(512))
    title = db.Column(db.String(50), nullable=False)
    plink = db.Column(db.String(30))
    person = db.Column(db.String(30), nullable=False)
    desig = db.Column(db.String(30))
    # Person designation
    contact = db.Column(db.String(10))
    picurl = db.Column(db.String(260))
    # Picture on the talk, large
    ppicurlsm = db.Column(db.String(260))
    # Picture of the person (small)
    ppicurllr = db.Column(db.String(260))
    # Picture of the person (large)
    amt = db.Column(db.Integer)
    # Amount spent to bring the person
    incharge = db.Column(db.Integer)
    # ID of the internal person incharge

    def serialize(self):
        d = Serializer.serialize(self)
        return d

class Workshops(db.Model, Serializer):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    plink = db.Column(db.String(30))
    # Permalink (extension only)
    about = db.Column(db.String(3000)) #Content in markdown
    # about on the workshop (1000 char)
    prereq = db.Column(db.String(3000)) #Content in markdown
    department = db.Column(db.Integer)
    # Need to come up with a numbering for departments
    theme = db.Column(db.String(20))
    # Theme, if any
    instructor = db.Column(db.String(40))
    abins = db.Column(db.String(300))
    # About the lead instructor
    vidurl = db.Column(db.String(400))
    # URL for video on the workshop, if any, from Youtube, Vimeo or any other service.
    picture1 = db.Column(db.String(200))
    picture2 = db.Column(db.String(200))
    picture3 = db.Column(db.String(200))
    lead = db.Column(db.String(30))
    company = db.Column(db.String(30))
    # Conducting company, if any
    companylogo = db.Column(db.String(200))
    contact = db.Column(db.String(10))
    # Organising company contact details
    fee = db.Column(db.Integer)
    incharge = db.Column(db.Integer)
    # V-ID of the internal person incharge
    support = db.Column(db.Integer)
    # V-ID of the support person assigned to the event
    pub = db.Column(db.Boolean, default=False)
    # Publish
# Workshop schedule addition needed - slot management with timings, seats available and so on.
# Need to build a seperate schema to manage expenses. Each row currosponds to certain payment, with which event for.
# Need to build a tag management system, to associate events in general.

class Contests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    img1 = db.Column(db.String(300))
    img2 = db.Column(db.String(300))
    img2 = db.Column(db.String(300))
    about = db.Column(db.String(2000), nullable=False)
    task = db.Column(db.String(512))
    pricing = db.Column(db.Integer, nullable=False)
    # Pricing per team (1 to any)
    team_limit = db.Column(db.Integer)
    # Need to manage teams
    expense = db.Column(db.Integer)
    # For internal use - expenses
    incharge = db.Column(db.Integer)

# class RegLog(db.Model):
#     regid = db.Column(db.Integer, nullable=False)
#     # Acts as the cart data + registrations
#     vid = db.Column(db.Integer,primary_key=True) 
#     #UserID
#     cat = db.Column(db.Integer, primary_key=True)
#     # Event category (Workshop, ...)
#     eid = db.Column(db.Integer, primary_key=True) 
#     #EventID
#     pay_completed = db.Column(db.Boolean)
#     # 0 if not paid, 1 if paid.
# Need to rethink registrations

class EventDLog(db.Model):
    # Logs Event dashboard changes
    # 1 for addition of a new event, 2 for edit, 3 for deletion
    vid = db.Column(db.Integer,primary_key=True) 
    #UserID
    cat = db.Column(db.Integer, primary_key=True)
    # Event category (Workshop, ...)
    eid = db.Column(db.Integer, primary_key=True) 
    #EventID
    action = db.Column(db.Integer)

class Team(db.Model, Serializer):
    tid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    leader = db.Column(db.Integer, nullable=False) #Leader VID
    state = db.Column(db.Integer, default=1) #1 for active, 2 for deleted / disabled
    r1 = db.Column(db.Integer)
    r2 = db.Column(db.Integer)
    r3 = db.Column(db.Integer)
    time_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
