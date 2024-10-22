import json
import sys
import socket

HOST = 'localhost'
PORT = 5950

try:
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
#   sys.stderr.write("[ERROR] %s\n" % msg[1])
  sys.exit(1)

try:
  sock.connect((HOST, PORT))
except socket.error:
#   sys.stderr.write("[ERROR] %s\n" % msg[1])
  sys.exit(2)

print('sending')
msg = {'@message': 'python test message', '@tags': ['python', 'test']}

sock.sendall(json.dumps(msg).encode("utf8"))

sock.close()
sys.exit(0)