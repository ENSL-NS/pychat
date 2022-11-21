# pychat
Just a simple WhatsApp like message marking interface.

## Usage
The library uses three main functions to control the interface.

First, create an `Interface` object to initialize the interface. This sets up all the required tweaks by coloroma. The passed parameter specifies the username of the user of the

```
iface = interface.Interface("Francesco")
```

`add_message` adds a line with a new message. The first parameter specifies
the username of who wrote the message. The second parameter is the message to
display. If the username corresponds to the local user, the message is
treated accordingly.
The function returns a message identifier.

```
i1 = iface.add_message("Francesco", "Is this WhatsApp?")
```

`update_message` updates the status of a message, i.e., it updates the checks next to the message. Valid states for the message are "sent" (the default set at message creation, "received", and "read").
```
iface.update_message(i1, "received") 
```

See [test_interface.py](test_interface.py) for a working example 
