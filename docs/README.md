# ComputePods NATS logger

A simple NATS logger to send/listen for messages on selected channels.

```
usage: cplogger [-h] [-c CONFIG] [-P PORT] [-H HOST] [-r | --raw | --no-raw]
                [-s SEND] [-m MESSAGEFILE] [-v | --verbose | --no-verbose]
                [WORD ...]

Send or log messages to/from various NATS subjects

positional arguments:
  WORD                  A message to send (optional)

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Load configuration from file
  -P PORT, --port PORT  The NATs server's port
  -H HOST, --host HOST  The NATs server's host
  -r, --raw, --no-raw   Send/Listen for RAW messages (default: wrap messages
                        as json strings)
  -s SEND, --send SEND  Send a message to this subject instead of listening
  -m MESSAGEFILE, --messageFile MESSAGEFILE
                        Load the message to send from a YAML file
  -v, --verbose, --no-verbose
                        Report additional information about what is happening

```