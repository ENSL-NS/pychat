import sys
import random
from datetime import datetime
from colorama import Fore, just_fix_windows_console

# Enable ANSI escape sequences on Windows terminals (no-op elsewhere)
just_fix_windows_console()

# set the available colors
colors = [Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.LIGHTBLACK_EX,
    Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX,
    Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX,
    Fore.LIGHTYELLOW_EX, Fore.MAGENTA, Fore.RED, Fore.WHITE, Fore.YELLOW
]

check_color_not_read = Fore.LIGHTGREEN_EX
check_color_read = Fore.LIGHTBLUE_EX

class DisplayMessage():
  """A message as shown on the screen by the Interface.

  This is NOT what travels over the network: see message.NetworkMessage.
  """
  def __init__(self, message_id, user, date, text, status="sent") -> None:
    self.message_id = message_id
    self.user = user
    self.date = date
    self.text = text
    self.status = status

class Interface():
  separator_token = ": " # we will use this to separate the client name & message
  states = {
    "sent": f"{check_color_not_read}v",
    "received": f"{check_color_not_read}vv",
    "read": f"{check_color_read}vv"
  }

  def __init__(self, myname):
    self.users = {}         # username -> color
    self.myname = myname
    self.messages = {}      # message id -> DisplayMessage
    self.message_counter = 0
    # Clear the screen and move the cursor to the top-left corner
    print("\033[2J\033[H", end="", flush=True)

  def _format(self, entry):
    line = f"{self.users[entry.user]}[{entry.date}] {entry.user}{Interface.separator_token}{entry.text}"
    # Checks are only shown next to the messages written by the local user
    if entry.user == self.myname:
      line += "\t" + Interface.states[entry.status]
    return line + Fore.RESET

  def add_message(self, username, text):
    if username not in self.users:
      self.users[username] = random.choice(colors)
    message_id = self.message_counter
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    self.messages[message_id] = DisplayMessage(message_id, username, date_now, text)
    self.message_counter += 1
    print(self._format(self.messages[message_id]), flush=True)
    return message_id

  def update_message(self, message_id, status):
    if status not in Interface.states:
      raise ValueError(f"Invalid status {status!r}, expected one of {list(Interface.states)}")
    entry = self.messages[message_id]
    entry.status = status
    # The cursor sits on the line below the last message, so the message is
    # `lines` lines above it. Go up, clear the line, redraw it, come back down.
    lines = self.message_counter - message_id
    print(f"\033[{lines}A\r\033[2K{self._format(entry)}\r\033[{lines}B", end="", flush=True)

  def read_input(self, prompt="Write message: "):
    """Read a line from the keyboard and erase the prompt afterwards.

    Use this instead of input(): a leftover prompt line would shift the lines
    that update_message counts to find a message on the screen.
    """
    text = input(prompt)
    if sys.stdin.isatty():
      # Pressing Enter moved the cursor one line down: go back to the prompt line
      print("\033[1A", end="")
    print("\r\033[2K", end="", flush=True)
    return text

# cursor positioning
# ESC [ y;x H     # position cursor at x across, y down
# ESC [ y;x f     # position cursor at x across, y down
# ESC [ n A       # move cursor n lines up
# ESC [ n B       # move cursor n lines down
# ESC [ n C       # move cursor n characters forward
# ESC [ n D       # move cursor n characters backward

# clear the screen
# ESC [ mode J    # clear the screen (mode 2: whole screen)
# ESC [ mode K    # clear the line (mode 2: whole line)
