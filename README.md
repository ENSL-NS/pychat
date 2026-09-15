# pychat

Material for a seminar on network programming in Python: a few basic socket examples and a minimal WhatsApp-like terminal chat built on top of them.

## Contents

- [examples/](examples/): minimal echo client/server pairs to get familiar with sockets.
  - [echo_server_tcp.py](examples/echo_server_tcp.py) / [echo_client_tcp.py](examples/echo_client_tcp.py): TCP (`SOCK_STREAM`) echo on `127.0.0.1:20001`.
  - [echo_server_udp.py](examples/echo_server_udp.py) / [echo_client_udp.py](examples/echo_client_udp.py): UDP (`SOCK_DGRAM`) echo on `127.0.0.1:20001`.
- [pychat/](pychat/): the chat itself. See [pychat/README.md](pychat/README.md) for details.
  - `interface.py`: colored terminal display with WhatsApp-style check marks (`DisplayMessage`, `Interface`).
  - `message.py`: the messages exchanged over the network (`NetworkMessage`), encoded with pickle or a binary format.
  - `test_interface.py`: demo of the interface alone.
  - `server_skeleton.py` / `client_skeleton.py`: a turn-based chat over TCP, to be extended.

## Quick start

```bash
pip install colorama

# the echo examples (start the server first, in its own terminal)
python examples/echo_server_tcp.py
python examples/echo_client_tcp.py

# the chat interface demo
python pychat/test_interface.py

# the chat (two terminals, server first)
python pychat/server_skeleton.py
python pychat/client_skeleton.py
```

## License

GPL-3.0, see [LICENSE](LICENSE).
