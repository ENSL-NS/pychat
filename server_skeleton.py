import socket
import pychat.message as message

from pychat import interface

localIP = "127.0.0.1"
localPort = 20003
bufferSize = 1024  # Normally 1024, but we want fast response. Why?

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((localIP, localPort))
s.listen(1) # What is 1?

iface = interface.Interface("server")

while(True):
  conn, addr = s.accept()
  # print('Connection address:', addr)
  while 1:
    # Receive message
    data = conn.recv(bufferSize)
    if not data: break
    msg = message.DictMessage()
    msg.decode(data)
    if msg.msg["t"] != 0:
      raise Exception("Bad order")
    cm = iface.add_message("client", msg.msg["m"])
    
    # Send answer back to say it was read
    ans = message.DictMessage()
    ans.msg["t"] = 1
    ans.msg["s"] = 1
    conn.send(ans.encode()) 
    
    # Send new message
    response = input("Write message: ")
    msg = message.DictMessage()
    msg.msg["t"] = 0
    msg.msg["m"] = response
    conn.send(msg.encode()) 
    sm = iface.add_message("server", response)
    
    # Get notification that it was read
    data = conn.recv(bufferSize)
    if not data: break
    msg = message.DictMessage()
    msg.decode(data)
    if msg.msg["t"] != 1:
      raise Exception("Bad order")
    if msg.msg["s"] != 1:
      raise Exception("Bad status")
    iface.update_message(sm, "read")
  conn.close()