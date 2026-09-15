import socket
import message
import interface

localIP = "127.0.0.1"
localPort = 20003
bufferSize = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Allow restarting the server right away without "Address already in use"
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((localIP, localPort))
s.listen(1) # What is 1?

iface = interface.Interface("server")

while True:
  conn, addr = s.accept()
  while True:
    # Receive message
    data = conn.recv(bufferSize)
    if not data: break
    msg = message.NetworkMessage()
    msg.decode(data)
    if msg.msg["t"] != message.TEXT:
      raise Exception("Bad order")
    iface.add_message("client", msg.msg["m"])

    # Send answer back to say it was read
    conn.sendall(message.NetworkMessage(t=message.STATUS, s=message.READ).encode())

    # Send new message
    text = iface.read_input("Write message: ")
    conn.sendall(message.NetworkMessage(t=message.TEXT, m=text).encode())
    sent_id = iface.add_message("server", text)

    # Get notification that it was read
    data = conn.recv(bufferSize)
    if not data: break
    msg = message.NetworkMessage()
    msg.decode(data)
    if msg.msg["t"] != message.STATUS:
      raise Exception("Bad order")
    if msg.msg["s"] != message.READ:
      raise Exception("Bad status")
    iface.update_message(sent_id, "read")
  conn.close()
