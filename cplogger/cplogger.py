"""
This is the ComputePods NATS logger (cplogger) tool

This tool reads in a cploggerConfig.yaml file describing the NATS server
to logger as well as the list of subjects to be monitored.
"""

import asyncio
import argparse
import datetime
import json
import signal
import sys
import traceback
import yaml

import cplogger.loadConfiguration
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

async def natsClientError(err) :
  """natsClientError is called whenever there is a general erorr
  associated with the NATS client or it connection to the NATS message
  system."""

  print("Error: {err}".format(err=err))

async def natsClientClosedConn() :
  """natsClientClosedConn is called whenever the NATS client closes its
  connection to the NATS message system."""
  print("")
  print("connection to NATS server is now closed.")

async def natsClientReconnected() :
  """natsClientRecconnected is called whenever the NATS client reconnects
  to the NATS message system."""

  print("reconnected to NATS server.")

class SignalException(Exception):
  def __init__(self, message):
    super(SignalException, self).__init__(message)

def signalHandler(signum, frame) :
  msg = "SignalHandler: Caught signal {}".format(signum)
  print(msg)
  raise SignalException(msg)

signal.signal(signal.SIGTERM, signalHandler)
signal.signal(signal.SIGHUP, signalHandler)

async def sleepLoop() :
  print("starting sleep loop")
  while True :
    print("")
    print(datetime.datetime.now())
    await asyncio.sleep(10)

async def listenToSubject(nc, rawMessages, aSubject) :

  def subjectCallback(aNATSMessage) :
    theSubject = aNATSMessage.subject
    theJSONMsg = aNATSMessage.data.decode()
    theMsg = theJSONMsg

    theEncoding = "raw"
    if not rawMessages :
      theEncoding = "json"
      try :
        theMsg = json.loads(theJSONMsg)
      except :
        theEncoding = "raw"
    if type(theMsg) != str :
      theMsg = "\n"+yaml.dump(theMsg)
    print("")
    print(f"  subject: {theSubject}({aSubject})")
    print(f"  message: [{theMsg}]")
    print(f" encoding: {theEncoding}")

  await nc.subscribe(aSubject, cb=subjectCallback)

async def main(config) :
  natsServer = config['natsServer']
  someServers = [ "nats://{}:{}".format(natsServer['host'], natsServer['port']) ]
  natsClient = NATS()
  await natsClient.connect(
    servers=someServers,
    error_cb=natsClientError,
    closed_cb=natsClientClosedConn,
    reconnected_cb=natsClientReconnected
  )

  try:
    if 'send' in config :
      aSubject = config['send']['subject']
      aMsg     = config['send']['message']
      encoding = 'raw'
      msgStr = aMsg
      if not config['rawMessages'] :
        try :
          if type(aMsg) == str :
            aMsg = json.loads(aMsg)
        except Exception as err :
          print("failed to load json")
          print(repr(err))
        msgStr = json.dumps(aMsg)
        encoding = 'json'
      print("  sending a message:")
      print("   subject: [{}]".format(aSubject))
      print("   message: [{}]".format(aMsg))
      print("  encoding: {}".format(encoding))
      await natsClient.publish(aSubject, bytes(msgStr, 'utf-8'))

    else :
      print("Listening to NATS subjects:")
      listeners = [sleepLoop()]
      for aSubject in config['subjects'] :
        print("  [{}]".format(aSubject))
        listeners.append(listenToSubject(natsClient, config['rawMessages'], aSubject))
      await asyncio.gather(*listeners)
  except SignalException as err :
    print("Shutting down: {}".format(str(err)))
  except KeyboardInterrupt as err :
    print("Shutting down: {}".format(str(err)))
  except Exception as err :
    msg = "\n ".join(traceback.format_exc().split("\n"))
    print("Shutting down after exception: \n {}".format(msg))
  finally:
    await natsClient.close()

def cli() :
  argparser = argparse.ArgumentParser(description="Log the messages from various NATS subjects")
  argparser.add_argument('-c', '--config',
    help="Load configuration from file")
  argparser.add_argument('-P', '--port',
    help="The NATs server's port")
  argparser.add_argument('-H', '--host',
    help="The NATs server's host")
  argparser.add_argument('-r', '--raw',
    action=argparse.BooleanOptionalAction,
    help="Send/Listen for RAW messages (default: wrap messages as json strings)")
  argparser.add_argument('words', metavar='WORD', type=str, nargs='*',
    help="A message to send")
  argparser.add_argument('-s', '--send',
    help="Send a message to this subject instead of listening")
  argparser.add_argument('-m', '--messageFile',
    help="Load the message to send from a YAML file")
  argparser.add_argument('-v', '--verbose',
    action=argparse.BooleanOptionalAction,
    help="Report additional information about what is happening")

  cliArgs = argparser.parse_args()

  if cliArgs.raw is None :
    cliArgs.raw = False

  if not cliArgs.config  : cliArgs.config = './cploggerConfig.yaml'
  if not cliArgs.verbose : cliArgs.verbose = False
  config = cplogger.loadConfiguration.loadConfig(cliArgs)

  print("ComputePods NATS tester starting")
  print("")

  try :
    asyncio.run(main(config))
  except SignalException as err :
    print("")
    print("Shutting down: {}".format(str(err)))
  except KeyboardInterrupt as err :
    print("")
    print("Shutting down from KeyboardInterrupt: {}".format(str(err)))
  except Exception as err :
    msg = "\n ".join(traceback.format_exc().split("\n"))
    print("Shutting down after exception: \n {}".format(msg))

  print("ComputePods NATS tester stopping")
