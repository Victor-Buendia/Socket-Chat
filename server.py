import socket
import select
import sys
import threading

s = socket.socket()
s.connect(('localhost', 1234))

def limparBuffer():
	print('> ', end = '')
	sys.stdout.flush()

threading.Thread(target=limparBuffer).start()
while True:
	readers, _, _ = select.select([sys.stdin, s], [], [])
	for reader in readers:
		if reader is s:
			print('< ' + s.recv(1000).decode('utf8') + '\n')
		else:
			threading.Thread(target=limparBuffer).start()
			msg = sys.stdin.readline()
			s.send(msg.encode('utf8'))
