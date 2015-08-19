"""

HTTP Delievery Mechanism
========================

Communications with server are done over HTTP requests.
Isn't ideal, but is the simplist socket to implement. (python side)

"""

from flask import *
from flask import flash as push_message
from web_panel import app
import minetest, models, json

@app.route("/api/<key>/<sid>/server_update/", methods=['GET', 'POST'])
def api_server_update(key, sid):
	# Get server database record
	server = models.Server.query.filter_by(id=sid).first()
	if not server:
		abort(404)

	# Get server process
	mt = minetest.get_process(server.id)
	if not mt:
		return "offline"

	# Check authentication key
	if mt.key != key:
		return "auth"

	# Handle GETs
	if request.method == "GET":
		retval = mt.toserver
		mt.toserver = []

		return json.dumps(retval)

	# Handle POSTs
	else:
		mt.process_data(json.loads(request.form['data']), server)
		return "ok"
