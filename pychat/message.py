import pickle
import struct

# Message types, stored under "t"
TEXT = 0    # a chat message, the text is under "m"
STATUS = 1  # a status update about a previous message, the status is under "s"

# Status values, stored under "s"
RECEIVED = 0
READ = 1

# Binary header: two unsigned 16-bit integers in network byte order
HEADER = struct.Struct("!HH")

class NetworkMessage:
  """A message as transmitted over the network between client and server.

  This is NOT what is shown on the screen: see interface.DisplayMessage.
  """
  def __init__(self, t=TEXT, s=RECEIVED, m=None) -> None:
    self.msg = {
      "t": t, # TEXT (0) or STATUS (1)
      "s": s, # RECEIVED (0) or READ (1), used by STATUS messages
      "m": m  # the text (a string), used by TEXT messages
    }

  # Encoding with pickle. Simple, but only use it with peers you trust:
  # unpickling data received from the network can execute arbitrary code.
  def encode(self):
    return pickle.dumps(self.msg)

  def decode(self, data):
    self.msg = pickle.loads(data)

  # Binary encoding:
  #   TEXT:   | type (2 bytes) | length L (2 bytes) | L bytes of UTF-8 text |
  #   STATUS: | type (2 bytes) | status (2 bytes)   |
  def encode_bytes(self):
    if self.msg["t"] == TEXT:
      text = self.msg["m"].encode("utf-8")
      return HEADER.pack(TEXT, len(text)) + text
    return HEADER.pack(STATUS, self.msg["s"])

  def decode_bytes(self, data):
    """Decode the message at the beginning of `data`.

    Returns the number of bytes consumed. Raises ValueError if `data` does not
    contain a full message.
    """
    if len(data) < HEADER.size:
      raise ValueError("Incomplete header")
    t, value = HEADER.unpack_from(data)
    if t == TEXT:
      end = HEADER.size + value
      if len(data) < end:
        raise ValueError("Incomplete text")
      self.msg = {"t": TEXT, "s": RECEIVED, "m": data[HEADER.size:end].decode("utf-8")}
      return end
    if t == STATUS:
      self.msg = {"t": STATUS, "s": value, "m": None}
      return HEADER.size
    raise ValueError(f"Unknown message type {t}")
