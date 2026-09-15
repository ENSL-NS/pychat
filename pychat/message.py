import pickle
import socket

class DictMessage:
  def __init__(self) -> None:
    self.msg = {
      "t": 0, # 0 message, 1 status update
      "s": 0, # 0 received, 1 read
      "m": None # This is the string
    }
    
  def encode(self):
    return pickle.dumps(self.msg)
  
  def decode(self, msg):
    self.msg = pickle.loads(msg)
    
  def encode_bytes(self):
    if self.msg["t"] == 0:
      b = bytes(socket.htons(0)) + bytes(socket.htons(len(self.msg["m"]))) + bytes(self.msg["m"])
      return b
    else:
      b = bytes(socket.htons(1)) + bytes(socket.htons(self.msg["s"]))
  
  def decode_bytes(self, b):
    self.msg["t"] = socket.ntons(b[0:2])
    if self.msg["t"] == 0:
      ml = socket.ntons(b[2:4])
      if len(b) - 4 < ml: 
        raise Exception()