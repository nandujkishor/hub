from app import app, db
import datetime
# from config import Config
import jwt

class User(db.Model):
    vid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.String(40))
    email = db.Column(db.String(300), unique=True)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))
    ppic = db.Column(db.String(256))
    course = db.Column(db.String(200))
    major = db.Column(db.String(200))
    sex = db.Column(db.Integer)
    year = db.Column(db.Integer)
    college = db.Column(db.Integer)
    institution = db.Column(db.String(200))
    school = db.Column(db.Boolean)
    level = db.Column(db.Integer)
    # In case college is not listed.
    phno = db.Column(db.String(10))
    # Levels: power directly propotional to number
    detailscomp = db.Column(db.Boolean)
    educomp = db.Column(db.Boolean)
    mailsent = db.Column(db.Boolean, default=False)
    time_created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    lastseen = db.Column(db.DateTime)
    intime = db.Column(db.DateTime)
    outtime = db.Column(db.DateTime)
    farer = db.Column(db.String(50))
    balance = db.Column(db.Integer, default=0)
    # Assert non-negative values
    referrer = db.Column(db.Integer, db.ForeignKey('user.vid'))
    # regworkshops = db.relationship('Workshops', backref='user', lazy=True)
    # regcontests = db.relationship('Contests', backref='user', lazy=True)

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def super(self):
        return self.email=="nandujkishor@gmail.com" or self.email=="aswanth366@gmail.com" or self.email=="bvsabhishek@gmail.com"

    def encode_auth_token(self):
        # Params: None
        # Returns: JWT
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=10, seconds=0),
                'iat': datetime.datetime.utcnow(),
                'sub': self.vid
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            print("EXCEPTION CAUGHT = ", e)
            # Setup emailing to email the occured exception
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        # Params: JWT
        # Returns: UserID / ErrorID (int)
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.'
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            print("Expired token")
            return "Expired token"
            # Signature expired. Need to login again.
        except jwt.InvalidTokenError:
            print("Invalid token")
            return "Invalid token"
            # Invalid token. Need to login again.

class BlacklistToken(db.Model):
    # Token Model for storing JWT tokens
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.Text, unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()
        print("Blacklisted")

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False

class College(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # caid = db.Column(db.Integer)
    district = db.Column(db.String(50))
    state = db.Column(db.String(50))

    def __repr__(self):
        return '<College {}>'.format(self.name)

class Eventsmixin():
    # Event details
    title = db.Column(db.String(300), nullable=False)
    plink = db.Column(db.String(80))
    department = db.Column(db.Integer)
    short = db.Column(db.Text)
    about = db.Column(db.Text)
    vidurl = db.Column(db.String(400))
    # URL for video on the event, if any, from Youtube, Vimeo or any other service.
    prereq = db.Column(db.Text) #Content in markdown
    rules = db.Column(db.Text)
    tags = db.Column(db.Text)
    # Need tags seperated by a delimiter - ','(coma)

    # Details on the Partner organisation
    org = db.Column(db.String(30))

    # # Vidyut staff contact points
    # incharge = db.Column(db.Integer, db.ForeignKey('user.vid'))
    # # ID of the internal person incharge
    # support = db.Column(db.Integer, db.ForeignKey('user.vid'))
    # support2 = db.Column(db.Integer, db.ForeignKey('user.vid'))
    # support3 = db.Column(db.Integer, db.ForeignKey('user.vid'))

    # Data for timings and logistics
    d1dur = db.Column(db.Text)
    d2dur = db.Column(db.Text)
    d3dur = db.Column(db.Text)
    d1beg = db.Column(db.Time)
    d1end = db.Column(db.Time)
    d2beg = db.Column(db.Time)
    d2end = db.Column(db.Time)
    d3beg = db.Column(db.Time)
    d3end = db.Column(db.Time)
    venue = db.Column(db.Text)
    fee = db.Column(db.Integer)
    expense = db.Column(db.Integer)
    # For internal use - expenses

    # State
    pub = db.Column(db.Boolean, default=False)
    regclosed = db.Column(db.Boolean)

# Not currently in usage
# Need to better define after talks
class Talks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person = db.Column(db.String(50), nullable=False)
    desig = db.Column(db.String(50))
    # Person designation
    contact = db.Column(db.String(10))
    picurl = db.Column(db.String(260))
    # Picture on the talk, large
    ppicurlsm = db.Column(db.String(260))
    # Picture of the person (small)
    ppicurllr = db.Column(db.String(260))
    # Picture of the person (large)
    fee = db.Column(db.Integer)
    # Amount spent to bring the person

class Workshops(db.Model, Eventsmixin):
    id = db.Column(db.Integer, primary_key=True)
    lead = db.Column(db.String(30))
    seats = db.Column(db.Integer)
    rmseats = db.Column(db.Integer)
    db.CheckConstraint('rmseats>=0')

    # Vidyut staff contact points
    incharge = db.Column(db.Integer, db.ForeignKey('user.vid'))
    # ID of the internal person incharge
    support = db.Column(db.Integer, db.ForeignKey('user.vid'))
    support2 = db.Column(db.Integer, db.ForeignKey('user.vid'))
    support3 = db.Column(db.Integer, db.ForeignKey('user.vid'))
# Need to build a seperate schema to manage expenses. Each row currosponds to certain payment, with which event for.
# Need to build a tag management system, to associate events in general.

class Contests(db.Model, Eventsmixin):
    id = db.Column(db.Integer, primary_key=True)
    prize1 = db.Column(db.Integer)
    prize2 = db.Column(db.Integer)
    prize3 = db.Column(db.Integer)
    pworth = db.Column(db.Integer)
    # Prizes worth ...
    # Pricing per team (1 to any)
    team_limit = db.Column(db.Integer, default=1)
    # Max. no of students in a team

    # Vidyut staff contact points
    incharge = db.Column(db.Integer, db.ForeignKey('user.vid'))
    # ID of the internal person incharge
    support = db.Column(db.Integer, db.ForeignKey('user.vid'))
    support2 = db.Column(db.Integer, db.ForeignKey('user.vid'))
    support3 = db.Column(db.Integer, db.ForeignKey('user.vid'))

class Registrations(db.Model):
    # Entry only if registration is successful
    regid = db.Column(db.Integer, primary_key=True)
    vid = db.Column(db.Integer, db.ForeignKey('user.vid'))
    cat = db.Column(db.Integer)
    eid = db.Column(db.Integer)
    typ = db.Column(db.Integer) # Mode of transaction 1:online 2:volunteer
    trid = db.Column(db.Integer, db.ForeignKey('transactions.trid')) # if processed through online medium
    regby = db.Column(db.Integer, db.ForeignKey('user.vid')) # volunteer, for mode 2
    amount = db.Column(db.Integer)
    tid = db.Column(db.String(10))
    mail = db.Column(db.Boolean, default=False)
    registime = db.Column(db.DateTime, default=datetime.datetime.now)
    # 0 if not paid, 1 if paid.

class AttendLog(db.Model):
    aid = db.Column(db.Integer, primary_key=True)
    vid = db.Column(db.Integer)
    cat = db.Column(db.Integer)
    # 1: Workshop, 2:Contest, 3:Culturals
    eid = db.Column(db.Integer)
    time = db.Column(db.DateTime)
    by = db.Column(db.Integer, db.ForeignKey('user.vid'))

class Transactions(db.Model):
    trid = db.Column(db.Integer, primary_key=True)
    # Acts as transaction ID
    vid = db.Column(db.Integer)
    inittime = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    status = db.Column(db.String(100), nullable=False, default="acrd")
    statusdesc = db.Column(db.Text)
    message = db.Column(db.Text)
    cat = db.Column(db.Integer)
    eid = db.Column(db.Integer)
    typ = db.Column(db.Integer) # Mode of transaction 1:online 2:volunteer
    amount = db.Column(db.Integer)
    bankref = db.Column(db.String(40))
    calls = db.Column(db.Integer, default=0)
    reply = db.Column(db.Text)
    refund = db.Column(db.Boolean,default=False)

class AddonTransactions(db.Model):
    trid = db.Column(db.Integer, db.ForeignKey('transactions.trid'), primary_key=True)
    scount = db.Column(db.Integer)
    mcount = db.Column(db.Integer)
    lcount = db.Column(db.Integer)
    xlcount = db.Column(db.Integer)
    xxlcount = db.Column(db.Integer)
    qty = db.Column(db.Integer)
    total = db.Column(db.Integer)

# class Refunds(db.Model):
#     trid = db.Column(db.Integer, primary_key=True)
#     processed = db.Column(db.Integer, default=False)
#     reason = db.Column(db.Text)

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

class Staff(db.Model):
    sid = db.Column(db.Integer, primary_key=True)
    vid = db.Column(db.Integer)
    team = db.Column(db.String(20))
    level = db.Column(db.Integer)
    # 1 for base level volunteer
    # 2 for ...
    # 3 for people with create previlige
    # 4 for core representative

class OtherPurchases(db.Model):
    purid = db.Column(db.Integer, primary_key=True)
    vid = db.Column(db.Integer, db.ForeignKey('user.vid')) #Purchasee
    roll = db.Column(db.String(20))
    bookid = db.Column(db.String(20))
    pid = db.Column(db.Integer) # Product ID
    scount = db.Column(db.Integer,default=0)
    mcount = db.Column(db.Integer,default=0)
    lcount = db.Column(db.Integer,default=0)
    xlcount = db.Column(db.Integer,default=0)
    xxlcount = db.Column(db.Integer,default=0)
    qty = db.Column(db.Integer)
    total = db.Column(db.Integer)
    by = db.Column(db.Integer)
    typ = db.Column(db.Integer)
    message = db.Column(db.Text)
    mail = db.Column(db.Boolean, default = False)
    trid = db.Column(db.Integer, db.ForeignKey('transactions.trid')) 
    purtime = db.Column(db.DateTime, default=datetime.datetime.now)

# class FarerLog(db.Model):
#     logid = db.Column(db.Integer)
#     vid = db.Column(db.Integer)
#     action = db.Column(db.Integer)
#     point = db.Column()
#     ip = db.Column()

# class Notifications(db.Model):
#     nid = db.Column(db.Integer, primary_key=True)
#     message = db.Column(db.Text)
#     img = db.Column(db.Text)
#     link = db.Column(db.String(1000))
#     typ = db.Column(db.Integer)
#     # 1 for individual, 2 for group (workshops), 3 for group (contests), 4 ..., 0 for general
#     by = db.Column(db.Integer, db.ForeignKey('user.vid'))
#     time = db.Column(db.DateTime, default=datetime.datetime.now)

# class NotifUser(db.Model):
#     nid = db.Column(db.Integer, db.ForeignKey('notifications.nid'), primary_key=True)
#     vid = db.Column(db.Integer, db.ForeignKey('user.vid'), primary_key=True)
#     read = db.Column(db.Boolean, default=False)
#     readtime = db.Column(db.DateTime)

class Pos(db.Model):
    posid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(800))
    descr = db.Column(db.Text)

class ValletTransaction(db.Model):
    tid = db.Column(db.Integer, primary_key=True)
    vid = db.Column(db.Integer, db.ForeignKey('user.vid'), nullable=False)
    typ = db.Column(db.Integer)
    pos = db.Column(db.Integer, db.ForeignKey('pos.posid'), nullable=False)
    notes = db.Column(db.Text)
    amt = db.Column(db.Integer, nullable=False)
    delivered = db.Column(db.Boolean, default=False)
    by = db.Column(db.Integer, db.ForeignKey('user.vid'))

class ValletPurchaseDetails(db.Model):
    # Details for a single transaction if of type2
    tid = db.Column(db.Integer, db.ForeignKey('vallet_transaction.tid'), primary_key=True)
    prodid = db.Column(db.Integer, db.ForeignKey('vallet_product.prodid'), primary_key=True)


class ValletProduct(db.Model):
    prodid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text)
    pos = db.Column(db.Integer, db.ForeignKey('pos.posid'))
    amount = db.Column(db.Integer, nullable=False)
    by = db.Column(db.Integer, db.ForeignKey('user.vid'))

class ConsolidatedPurch(db.Model):
    vid = db.Column(db.Integer, db.ForeignKey('user.vid'), primary_key=True) #Purchasee
    proamr = db.Column(db.Integer)
    proout = db.Column(db.Integer)
    prohea = db.Column(db.Integer)
    chnfas = db.Column(db.Integer)
    scount = db.Column(db.Integer)
    mcount = db.Column(db.Integer)
    lcount = db.Column(db.Integer)
    xlcount = db.Column(db.Integer)
    xxlcount = db.Column(db.Integer)
    qty = db.Column(db.Integer) # Total
    deliverby = db.Column(db.Integer, db.ForeignKey('user.vid'))
    message = db.Column(db.Text)
    deliver = db.Column(db.Boolean, default=False)
    collect = db.Column(db.DateTime, default=datetime.datetime.now)
