import socket
import select
import sys

s = socket.socket()
s.connect(('localhost', 1234))

while True:
	readers, _, _ = select.select([sys.stdin, s], [], [])
	for reader in readers:
		if reader is s:
			print('< ' + s.recv(1000).decode('utf8'))
		else:
			msg = sys.stdin.readline()
			s.send(msg.encode('utf8'))
