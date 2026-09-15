import socket

msgFromClient       = "Hello TCP Server"
bytesToSend         = str.encode(msgFromClient)

serverAddressPort   = ("127.0.0.1", 20001)
bufferSize          = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(serverAddressPort)

s.send(bytesToSend)
msgFromServer = s.recv(bufferSize)
s.close()

msg = "Message from Server {}".format(msgFromServer)
print(msg)