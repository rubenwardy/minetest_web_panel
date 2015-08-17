from flask import *
from flask import flash as push_message
from sqlalchemy import desc
from web_panel import app
import minetest, minetest_mech_http
import models, functools, views

def login_required(func):
	@functools.wraps(func)
	def inner(*args, **kwargs):
		global current_user
		if not "username" in session:
			current_user = None
			path = request.path
			if path == "/":
				path = None
			return redirect(url_for('login', r=path))

		current_user = models.User.query.filter_by(username=session["username"]).first()

		if not current_user:
			session.pop('username', None)
			return redirect(url_for('login', r=request.path))

		return func(*args, **kwargs)
	return inner

def ownership_required(func):
	@functools.wraps(func)
	def inner(*args, **kwargs):
		# TODO: check that the user is authorised to manage this server
		return func(*args, **kwargs)
	return inner

@app.route('/login/', methods=['GET', 'POST'])
def login():
	r = request.args.get('r')
	if "username" in session:
		return redirect(url_for('index'))

	if request.method == 'POST':
		user = models.User.query.filter_by(username=request.form["username"]).first()

		if user is None:
			push_message("No such user.")
			return redirect(url_for("login", r=r))
		else:
			if not user.authenticate(request.form["password"]):
				push_message("Incorrect Password.")
				return redirect(url_for("login", r=r))
			else:
				session['username'] = request.form['username']
				if r:
					return redirect(r)
				else:
					return redirect(url_for('index'))
	else:
		return render_template('login.html', redirect=r)

@app.route('/logout/')
def logout():
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route("/")
@login_required
def index():
	return render_template('index.html', servers=models.Server.query.all(), user=current_user)

@app.route("/<sid>/")
@login_required
@ownership_required
def dashboard(sid):
	server = models.Server.query.filter_by(id=sid).first()

	if not server:
		abort(404)

	status = minetest.status(server)

	log = models.ServerLogEntry.query.filter_by(server=server).\
			order_by(desc(models.ServerLogEntry.created)).limit(10).all()

	return render_template('dashboard.html', user=current_user,
			server=server, status=status, log=log)

@app.route("/<sid>/clear_logs/")
@login_required
@ownership_required
def clear_logs(sid):
	server = models.Server.query.filter_by(id=sid).first()

	if not server:
		abort(404)

	status = minetest.status(server)

	res = models.ServerLogEntry.query.filter_by(server=server)
	for item in res:
		models.db.session.delete(item)

	models.db.session.commit()

	return redirect(url_for('dashboard', sid=sid))

@app.route("/<sid>/debuglog/")
@login_required
@ownership_required
def debuglog(sid):
	n = int(request.args.get('n') or 30)
	i = request.args.get('i')
	server = models.Server.query.filter_by(id=sid).first()

	if not server:
		abort(404)

	status = minetest.status(server)

	return render_template('debuglog.html', user=current_user,
			server=server, status=status, debuglog=minetest.get_log(server, n, i), n=n, inc=i)

@app.route("/<sid>/start/")
@login_required
@ownership_required
def server_start(sid):
	server = models.Server.query.filter_by(id=sid).first()

	if not server:
		abort(404)

	minetest.kill(server)
	minetest.start(server)
	return redirect(url_for('dashboard', sid=sid))

@app.route("/<sid>/stop/")
@login_required
@ownership_required
def server_stop(sid):
	server = models.Server.query.filter_by(id=sid).first()

	if not server:
		abort(404)

	minetest.stop(server, current_user.username)
	return redirect(url_for('dashboard', sid=sid))

@app.route("/<sid>/kill/")
@login_required
@ownership_required
def server_kill(sid):
	server = models.Server.query.filter_by(id=sid).first()

	if not server:
		abort(404)

	minetest.kill(server)
	return redirect(url_for('dashboard', sid=sid))

@app.route("/<sid>/chat/", methods=['GET', 'POST'])
@login_required
@ownership_required
def chat(sid):
	server = models.Server.query.filter_by(id=sid).first()

	if not server:
		abort(404)

	status = minetest.status(server)

	if request.method == "GET":
		entries = models.ServerChatEntry.query.filter_by(serverId=sid).limit(30).all()
		return render_template('chat.html', user=current_user,
				server=server, status=status, entries=entries)
	else:
		minetest.send_chat_or_cmd(server, current_user.username, request.form['msg'], True)
		return redirect(url_for('chat', sid=sid))

@app.route("/api/<token>/<sid>/chat/", methods=['GET'])
@login_required
@ownership_required
def chat_api(token, sid):
	server = models.Server.query.filter_by(id=sid).first()
	if not server:
		abort(404)

	mt = minetest.get_process(sid)
	if not mt:
		abort(404)

	entries = models.ServerChatEntry.query.filter_by(serverId=sid).limit(30).all()
	entries_flat = []
	for e in entries:
		entries_flat.append({
			"username": e.username,
			"message" : e.message})

	return json.dumps(entries_flat)


def isDirSafe(ch):
	return ch.isalpha() or ch.isdigit() or ch=='_' or ch=='-'

@app.route("/<sid>/settings/", methods=['GET', 'POST'])
@login_required
@ownership_required
def settings(sid):
	server = models.Server.query.filter_by(id=sid).first()

	if not server:
		abort(404)

	status = minetest.status(server)

	if request.method == "GET":
		return render_template('settings.html', user=current_user,
				server=server, status=status)
	else:
		# Get values
		name = request.form['name'].strip()
		port = request.form['port'].strip()
		worldname = request.form['worldname'].strip()
		debuglog = request.form['debug'].strip()

		# Validate values
		try:
			port = int(port)
			if port < 2 or port >= 65535:
				port = server.port
		except ValueError:
			port = server.port
		if not name or name == "" or not worldname or worldname == "":
			return render_template('settings.html', user=current_user,
					server=server, status=status)

		# Strip bad characters out
		name = ''.join(ch for ch in name if (ch.isalpha() or ch.isdigit()\
		 		or ch==' ' or ch=='_')).strip()
		if app.config['SANDBOX']:
			worldname = ''.join(ch for ch in worldname if isDirSafe(ch)).strip()
			debuglog = ''.join(ch for ch in debuglog if (isDirSafe(ch) or ch==".")).strip()

		print(name, port, worldname, debuglog)

		server.name = name
		server.port = port
		server.worldname = worldname
		server.debuglog = debuglog
		models.db.session.commit()

		return redirect(url_for('dashboard', sid=sid))
