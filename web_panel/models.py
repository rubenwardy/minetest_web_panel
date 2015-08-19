from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from web_panel import app
from datetime import datetime
from sqlalchemy.orm import validates

# Initialise database
db = SQLAlchemy(app)

# Generate a 32 bit salt
def genSalt():
	import uuid
	return uuid.uuid4().hex

# Hash a password given the plaintext password, and a salt
def hashPassword(plain, salt):
	import hashlib
	return hashlib.sha512(plain + salt).hexdigest()

class User(db.Model):
	id        = db.Column(db.Integer, primary_key=True)
	username  = db.Column(db.String(15), unique=True)
	password  = db.Column(db.String(128))
	salt      = db.Column(db.String(32))
	is_admin  = db.Column(db.Boolean)

	# Initiates the user
	def __init__(self, username, plain):
		self.username  = username
		self.salt      = genSalt()
		self.password  = hashPassword(plain, self.salt)
		self.is_admin  = False

	# Authenticate the user
	def authenticate(self, plain):
		hash = hashPassword(plain, self.salt)
		return (hash == self.password)

class Server(db.Model):
	id        = db.Column(db.Integer, primary_key=True)
	name      = db.Column(db.String(15), unique=True)
	worldname = db.Column(db.String(30))
	debuglog  = db.Column(db.String(30), default="debug.txt")
	desc      = db.Column(db.String(64), default="")
	port      = db.Column(db.Integer, unique=True, default=30000)
	is_on     = db.Column(db.Boolean, default=False)
	ownerId   = db.Column(db.Integer, db.ForeignKey('user.id'))
	owner     = db.relationship('User', backref = db.backref('servers', lazy='dynamic'))

	@validates('worldname')
	def validate_worldname(self, key, address):
		import re
		assert not bool(re.compile(r'[^a-zA-Z0-9_]').search(address))
		return address

	def __init__(self, owner, name, worldname):
		self.owner = owner
		self.name = name
		self.worldname = worldname

	def getWorldPath(self):
		return app.config['MINETEST_WORLDS'] + self.worldname

	def getDebugLogPath(self):
		import os

		log = self.debuglog or "debug.txt"
		if app.config['SANDBOX']:
			log = os.path.normpath('/' + log).lstrip('/')
			log = os.path.join(self.getWorldPath(), "server", log)
			return log
		else:
			log = os.path.join(self.getWorldPath(), "server", log)
			return log

class ServerLogEntry(db.Model):
	id         = db.Column(db.Integer, primary_key=True)
	title      = db.Column(db.String(80))
	additional = db.Column(db.Text, nullable=True)
	mtype      = db.Column(db.Enum('warning', 'error', 'mod', 'plain', name='logtype'))
	serverId   = db.Column(db.Integer, db.ForeignKey('server.id'))
	server     = db.relationship('Server', backref = db.backref('log', lazy='dynamic'))
	created    = db.Column(db.DateTime)

	def __init__(self, server, mtype, title, additional):
		self.server     = server
		self.title      = title
		if additional:
			additional = additional.strip()
		self.additional = additional
		self.mtype      = mtype
		self.created    = datetime.utcnow()

class ServerChatEntry(db.Model):
	id         = db.Column(db.Integer, primary_key=True)
	username   = db.Column(db.String(80))
	message    = db.Column(db.Text, nullable=True)
	webpanel   = db.Column(db.Boolean)
	serverId   = db.Column(db.Integer, db.ForeignKey('server.id'))
	server     = db.relationship('Server', backref = db.backref('chat', lazy='dynamic'))
	created    = db.Column(db.DateTime)

	def __init__(self, server, username, message):
		self.server     = server
		self.username   = username
		self.message    = message
		self.created    = datetime.utcnow()
		self.webpanel   = False
