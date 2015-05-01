from flask import *
from flask import flash as push_message
app = Flask(__name__)
app.config.from_pyfile('../config.cfg')

import minetest, models, functools

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
def dashboard(sid):
	server = models.Server.query.filter_by(id=sid).first()

	if not server:
		abort(404)

	status = minetest.status(server)

	return render_template('dashboard.html', user=current_user,
			server=server, status=status)

@app.route("/<sid>/start/")
@login_required
def server_start(sid):
	server = models.Server.query.filter_by(id=sid).first()

	if not server:
		abort(404)

	minetest.stop(server)
	minetest.start(server)
	return redirect(url_for('dashboard', sid=sid))

@app.route("/<sid>/stop/")
@login_required
def server_stop(sid):
	server = models.Server.query.filter_by(id=sid).first()

	if not server:
		abort(404)

	minetest.stop(server)
	return redirect(url_for('dashboard', sid=sid))
