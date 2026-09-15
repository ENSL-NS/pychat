import socket
import pychat.message as message
from pychat import interface

iface = interface.Interface("client")

msgFromClient       = "Hello TCP Server"
bytesToSend         = str.encode(msgFromClient)

serverAddressPort   = ("127.0.0.1", 20003)
bufferSize          = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(serverAddressPort)

while 1:
  # Send new message
  response = input("Write message: ")
  msg = message.DictMessage()
  msg.msg["t"] = 0
  msg.msg["m"] = response
  s.send(msg.encode()) 
  sm = iface.add_message("client", response)
  
  # Get notification that it was read
  data = s.recv(bufferSize)
  if not data: break
  msg = message.DictMessage()
  msg.decode(data)
  if msg.msg["t"] != 1:
    raise Exception("Bad order")
  if msg.msg["s"] != 1:
    raise Exception("Bad status")
  iface.update_message(sm, "read")

  # Receive message
  data = s.recv(bufferSize)
  if not data: break
  msg = message.DictMessage()
  msg.decode(data)
  if msg.msg["t"] != 0:
    raise Exception("Bad order")
  cm = iface.add_message("server", msg.msg["m"])
  
  # Send answer back to say it was read
  ans = message.DictMessage()
  ans.msg["t"] = 1
  ans.msg["s"] = 1
  s.send(ans.encode()) 

s.close()