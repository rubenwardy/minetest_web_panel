"""

HTTP Delievery Mechanism
========================

Communications with server are done over HTTP requests.
Isn't ideal, but is the simplist socket to implement. (python side)

"""

from web_panel import app
import minetest, models

@app.route("/api/<key>/<sid>/server_update/", methods=['GET'])
def api_server_update(sid, key):
	server = models.Server.query.filter_by(id=sid).first()

	if not server:
		abort(404)

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

	return retval + "}\n"
