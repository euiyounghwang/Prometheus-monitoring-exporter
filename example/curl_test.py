
"""
import subprocess

# The command you would type in the terminal
command = ["curl", "-v", "telnet", "localhost:29092"]

# Run the command
result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Get the output and error message (if any)
output = result.stdout
error = result.stderr

# Check if it was successful
if result.returncode == 0:
    print("Success:")
    print(output)
else:
    print("Error:")
    print(error)


# curl -X GET -H "Accept: application/vnd.kafka.binary.v1+json" http://localhost:29092
"""


import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('localhost',22181))
if result == 0:
   print("Port is open")
else:
   print("Port is not open")
sock.close()