import socket

localIP = "127.0.0.1"
localPort = 20001
bufferSize = 20  # Normally 1024, but we want fast response. Why?

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((localIP, localPort))
s.listen(1) # What is 1?

while(True):
  conn, addr = s.accept()
  print('Connection address:', addr)
  while 1:
    data = conn.recv(bufferSize)
    if not data: break
    print("received data: {}".format(data))
    conn.send(data)  # echo
  conn.close()