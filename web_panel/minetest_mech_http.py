"""

HTTP Delievery Mechanism
========================

Communications with server are done over HTTP requests.
Isn't ideal, but is the simplist socket to implement. (python side)

"""

from flask import *
from flask import flash as push_message
from web_panel import app
import minetest, models

@app.route("/api/<key>/<sid>/server_update/", methods=['GET', 'POST'])
def api_server_update(key, sid):
	server = models.Server.query.filter_by(id=sid).first()

	if not server:
		abort(404)

	print(request.method)
	if request.method == "GET":
		print("sending")
		toserver = minetest.flush(server, key)

		if isinstance(toserver, str):
			return toserver

		retval = "return {\n"
		for item in toserver:
			retval += "\t{"
			retval += "\t\tmode = \"" + item['mode'] + "\",\n"
			retval += "\t\tcontent = \"" + item['content'] + "\",\n"
			if item['username']:
				retval += "\t\tusername = \"" + item['username'] + "\",\n"
			retval += "\t},\n"

		print("sent")

		return retval + "}\n"

	else:
		print("wrong)")
		data = request.form['data']
		mt = minetest.get_process(sid)
		if mt and mt.check():
			mt.process_data(json.loads(data), server)
			return "ok"
		else:
			abort(404)
