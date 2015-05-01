from web_panel import app
from web_panel.models import db
import subprocess
servers = {}

class MinetestProcess:
	def __init__(self, id, process):
		print("Server " + str(id) + " started!")
		self.process = process
		self.id = id

	def check(self):
		if self.process is None:
			return False
		retval = self.process.poll()
		if retval is None:
			return True

		return False

	def stop(self):
		print("Stopping " + str(self.id))
		self.process.terminate()

def start(server):
	try:
		mt = servers["sid_" + str(server.id)]
		return False
	except KeyError:
		params = [app.config['MINETEST_EXE'], "--worldname", server.worldname]
		additional_params = app.config['MINETEST_EXE_PARAMS'] or []
		for param in additional_params:
			params.append(param)

		proc = subprocess.Popen(params)
		servers["sid_" + str(server.id)] = MinetestProcess(server.id, proc)
		server.is_on = True
		db.session.commit()
		return proc.poll() is None

def stop(server):
	try:
		mt = servers["sid_" + str(server.id)]

		if mt.check():
			mt.stop()
			server.is_on = False
			db.session.commit()

		del servers["sid_" + str(server.id)]
	except KeyError:
		pass

def socket_is_up(address, port):
	import sys, time, socket

	try:
		start = time.time()
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.settimeout(0.5)
		buf = "\x4f\x45\x74\x03\x00\x00\x00\x01"
		sock.sendto(buf, (address, port))
		data, addr = sock.recvfrom(1000)
		if data:
			peer_id = data[12:14]
			buf = "\x4f\x45\x74\x03" + peer_id + "\x00\x00\x03"
			sock.sendto(buf, (address, port))
			sock.close()
			end = time.time()
			return True
		else:
			return False
	except:
		return False

def status(server):
	is_up = socket_is_up("localhost", server.port)

	try:
		mt = servers["sid_" + str(server.id)]
		if mt and mt.check():
			if is_up:
				return "on"
			else:
				return "starting"
	except KeyError:
		pass

	if is_up:
		return "blocked"
	else:
		return "off"
