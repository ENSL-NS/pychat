import socket
import message
import interface

serverAddressPort   = ("127.0.0.1", 20003)
bufferSize          = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(serverAddressPort)

iface = interface.Interface("client")

while True:
  # Send new message
  text = iface.read_input("Write message: ")
  s.sendall(message.NetworkMessage(t=message.TEXT, m=text).encode())
  sent_id = iface.add_message("client", text)

  # Get notification that it was read
  data = s.recv(bufferSize)
  if not data: break
  msg = message.NetworkMessage()
  msg.decode(data)
  if msg.msg["t"] != message.STATUS:
    raise Exception("Bad order")
  if msg.msg["s"] != message.READ:
    raise Exception("Bad status")
  iface.update_message(sent_id, "read")

  # Receive message
  data = s.recv(bufferSize)
  if not data: break
  msg = message.NetworkMessage()
  msg.decode(data)
  if msg.msg["t"] != message.TEXT:
    raise Exception("Bad order")
  iface.add_message("server", msg.msg["m"])

  # Send answer back to say it was read
  s.sendall(message.NetworkMessage(t=message.STATUS, s=message.READ).encode())

s.close()
