from web_panel import app
from web_panel.models import db, Server, ServerLogEntry
import subprocess
servers = {}

def check_processes():
	print("Checking servers!")
	for key in servers.keys():
		value = servers[key]
		print("Checking " + key)
		if value.check():
			print("- ok!")
		else:
			print("- exited!")
			if value.retval != 0:
				server = Server.query.filter_by(id=value.id).first()
				if server:
					db.session.add(ServerLogEntry(server, "error",
							"Server Crashed!", value.getEndOfLog()))
			del servers[key]
	db.session.commit()

class MinetestProcess:
	def __init__(self, id, process, port):
		print("Server " + str(id) + " started!")
		self.process = process
		self.id = id
		self.retval = None
		self.port = port

	def getEndOfLog(self):
		return "last 20 lines of debug.txt will be here."

	def check(self):
		if self.process is None:
			return False
		retval = self.process.poll()
		if retval is None:
			return True

		self.process = None
		self.retval = retval
		print("Process stopped with " + str(retval))
		return False

	def kill(self):
		print("Killing " + str(self.id))
		self.process.terminate()

def start(server):
	try:
		mt = servers["sid_" + str(server.id)]
		return False
	except KeyError:
		# Build Parameters
		debuglog = server.getDebugLogPath()
		params = [app.config['MINETEST_EXE']]
		additional_params = app.config['MINETEST_EXE_PARAMS'] or []
		for param in additional_params:
			params.append(param)
		params.append("--worldname")
		params.append(server.worldname)
		params.append("--logfile")
		params.append(debuglog)
		params.append("--port")
		params.append(str(server.port))

		# Create directories in debug path
		import os
		if not os.path.exists(os.path.dirname(debuglog)):
			os.makedirs(os.path.dirname(debuglog))

		# Debug: Print Parameters
		outval = ""
		for param in params:
			outval += " " + param
		print(outval.strip())

		# Start Process
		proc = subprocess.Popen(params)
		servers["sid_" + str(server.id)] = MinetestProcess(server.id, proc, server.port)
		server.is_on = True
		db.session.commit()
		return proc.poll() is None

def stop(server):
	# TODO: send /shutdown command, don't kill it
	kill(server)

def kill(server):
	try:
		mt = servers["sid_" + str(server.id)]

		if mt.check():
			mt.kill()
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
	check_processes()

	try:
		mt = servers["sid_" + str(server.id)]

		if mt and mt.check():
			is_up = socket_is_up("localhost", mt.port)
			if is_up:
				if mt.port != server.port:
					return "restart-required"
				else:
					return "on"
			else:
				return "no-connect"
	except KeyError:
		pass


	is_up = socket_is_up("localhost", server.port)

	if is_up:
		return "blocked"
	else:
		return "off"
