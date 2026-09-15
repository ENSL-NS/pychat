# pychat

A minimal WhatsApp-like chat that runs in the terminal. It is split into:

- a **display layer** that prints colored messages with check marks (`v`, `vv`) and updates them in place,
- a **network layer** that defines what client and server exchange over a socket,
- a **client and a server skeleton** that combine the two into a (very basic) working chat.

## Requirements

Python 3 and [colorama](https://pypi.org/project/colorama/):

```bash
pip install colorama
```

## Files

| File | What it contains |
| --- | --- |
| [interface.py](interface.py) | `Interface`, which draws the chat on the terminal, and `DisplayMessage`, a message as shown on screen. |
| [message.py](message.py) | `NetworkMessage`, a message as sent over the network, with two encodings (pickle and binary). |
| [test_interface.py](test_interface.py) | Standalone demo of `Interface`, no network involved. |
| [server_skeleton.py](server_skeleton.py) | TCP server that chats with one client at a time. |
| [client_skeleton.py](client_skeleton.py) | TCP client that connects to the server. |

## Two kinds of messages

The code deliberately keeps two separate classes, because what you show to a user and what you transmit are different things:

| | `interface.DisplayMessage` | `message.NetworkMessage` |
| --- | --- | --- |
| Purpose | Remember what is printed on screen, so it can be redrawn | Carry information between client and server |
| Contains | id, author, date, text, status (`"sent"`, `"received"`, `"read"`) | type (text or status update), status, text |
| Created by | `Interface.add_message` (you never build one yourself) | Your client/server code |

For example, when the server gets a text, it creates a `DisplayMessage` to show it and sends back a *different* `NetworkMessage` of type `STATUS` saying it was read. The client then updates its own `DisplayMessage` to show blue checks.

## The interface: `interface.py`

The interface uses three main functions. See [test_interface.py](test_interface.py) for a working example:

```bash
python test_interface.py
```

First, create an `Interface` object. This clears the screen. The parameter is the username of the local user: messages from this user get check marks next to them.

```python
iface = interface.Interface("Francesco")
```

`add_message` adds a line with a new message. The first parameter is the username of who wrote the message, and the second is the text to display. It returns a message identifier. Each user gets a random color.

```python
i1 = iface.add_message("Francesco", "Is this WhatsApp?")
```

`update_message` changes the checks next to a message that is already on screen. Valid states are `"sent"` (the default set at creation, green `v`), `"received"` (green `vv`) and `"read"` (blue `vv`).

```python
iface.update_message(i1, "received")
```

`read_input` reads a line from the keyboard. Use it instead of `input()` when you also use the interface (see below).

```python
text = iface.read_input("Write message: ")
```

### How it works (and its limits)

The interface uses [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code) (listed at the bottom of `interface.py`). To update message `i`, it moves the cursor up `message_counter - i` lines, clears that line, redraws it and moves back down. This only works if **every message takes exactly one line on screen**. As a result:

- Anything else printed to the terminal shifts the count. That is why `read_input` erases its prompt after you press Enter. Avoid `print()` while the interface is active.
- Messages longer than the terminal width wrap onto several lines, and messages containing `\n` span several lines too. Updating messages printed *before* those lands on the wrong line.
- Messages that scrolled off the top of the terminal cannot be updated.

## Network messages: `message.py`

A `NetworkMessage` stores its content in the dictionary `msg`:

| Key | Meaning | Values |
| --- | --- | --- |
| `"t"` | type | `message.TEXT` (0) for a chat message, `message.STATUS` (1) for a status update |
| `"s"` | status (used by `STATUS` messages) | `message.RECEIVED` (0), `message.READ` (1) |
| `"m"` | text (used by `TEXT` messages) | a string |

```python
import message

text = message.NetworkMessage(t=message.TEXT, m="Hello!")
ack = message.NetworkMessage(t=message.STATUS, s=message.READ)
```

Two encodings are provided.

**Pickle** (`encode` / `decode`) serializes the dictionary with Python's `pickle`. It is the simplest option and is used by the skeletons. Warning: unpickling data can run arbitrary code, so never use it with peers you don't trust.

```python
data = text.encode()          # bytes, ready for sock.sendall(data)
received = message.NetworkMessage()
received.decode(data)
```

**Binary** (`encode_bytes` / `decode_bytes`) is a custom format in which every integer is 2 bytes in network byte order (big endian):

```
TEXT:    | type = 0 (2 bytes) | length L (2 bytes) | L bytes of UTF-8 text |
STATUS:  | type = 1 (2 bytes) | status   (2 bytes) |
```

`decode_bytes` decodes the message at the beginning of a buffer and returns how many bytes it consumed. It raises `ValueError` if the buffer doesn't contain a complete message yet. The length field tells the receiver where a message ends, so the format works with TCP streams (see the limits below).

```python
data = text.encode_bytes()    # b'\x00\x00\x00\x06Hello!'
received = message.NetworkMessage()
used = received.decode_bytes(data)
```

## Client and server skeletons

The skeletons implement a strict turn-based chat over TCP on `127.0.0.1:20003`. Run them in two terminals from this folder, starting with the server:

```bash
python server_skeleton.py     # terminal 1
python client_skeleton.py     # terminal 2
```

The client writes first, then the two sides take turns. Each text message is answered with a `STATUS`/`READ` message, which turns the sender's checks blue:

```
client                                   server
  | read_input, add_message (v)            |
  |---- TEXT "hello" --------------------->| add_message
  |<--- STATUS READ -----------------------|
  | update_message -> "read" (vv)          | read_input, add_message (v)
  |<--- TEXT "hi" -------------------------|
  | add_message                            |
  |---- STATUS READ ---------------------->| update_message -> "read" (vv)
  | ... and again from the top ...         |
```

If a message arrives out of this order, the programs raise `Exception("Bad order")`. When the client disconnects, the server waits for a new client. Stop either program with `Ctrl+C`.

### What the skeletons don't do (starting points for exercises)

They are skeletons: they work in the happy case but deliberately leave out a lot.

- **Strict turns.** Both programs block on either `input` or `recv`, so you can't send two messages in a row or receive while typing. Fixing this needs threads, `select`, or `asyncio`.
- **No message framing.** Each `recv(1024)` is assumed to return exactly one pickled message. TCP is a byte stream: a single `recv` can return half a message or two messages glued together (for example, texts longer than about 1000 bytes break). The length field of the binary encoding solves this: buffer the received bytes and call `decode_bytes` until it stops raising `ValueError`.
- **The `received` state is never used.** A peer could send `STATUS`/`RECEIVED` when a message arrives and `STATUS`/`READ` when it is displayed. However, `STATUS` messages don't say *which* message they refer to. That works with strict turns but not otherwise, so you would need to add a message id to the protocol.
- **One client at a time, and hard-coded names** (`"client"` and `"server"`). There is no way to pick a username or talk to several people.
- **Pickle over the network** is insecure (see above). Switching the skeletons to `encode_bytes` / `decode_bytes` fixes it.
