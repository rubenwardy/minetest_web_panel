from web_panel import app

def is_up(address, port=30000):
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
