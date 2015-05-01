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
	port      = db.Column(db.Integer, unique=True)
	is_on     = db.Column(db.Boolean)

	@validates('worldname')
	def validate_worldname(self, key, address):
		import re
		assert not bool(re.compile(r'[^a-zA-Z0-9_]').search(address))
		return address

	def __init__(self, name, worldname):
		self.name = name
		self.worldname = worldname
		self.port = 30000

	def getWorldPath(self):
		return app.config['minetest_worlds'] + self.worldname
