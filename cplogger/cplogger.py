# This is the ComputePods NATS logger (cplogger) tool

# This tool reads in a cploggerConfig.yaml file describing the NATS server
# to logger as well as the list of subjects to be monitored.

import asyncio
import argparse
import datetime
import logging
import signal
import traceback
import yaml

import cplogger.loadConfiguration
from   cputils.natsClient import NatsClient

argparser = argparse.ArgumentParser(description="Log the messages from various NATS subjects")
argparser.add_argument('-c', '--config',
  help="Load configuration from file")
argparser.add_argument('-P', '--port',
  help="The NATs server's port")
argparser.add_argument('-H', '--host',
  help="The NATs server's host")
argparser.add_argument('-v', '--verbose',
  action=argparse.BooleanOptionalAction,
  help="Report additional information about what is happening")

cliArgs = argparser.parse_args()

#logging.basicConfig(filename='inotify2nats.log', encoding='utf-8', level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)

class SignalException(Exception):
  def __init__(self, message):
    super(SignalException, self).__init__(message)

def signalHandler(signum, frame) :
  msg = "SignalHandler: Caught signal {}".format(signum)
  logging.info(msg)
  raise SignalException(msg)

signal.signal(signal.SIGTERM, signalHandler)
signal.signal(signal.SIGHUP, signalHandler)

async def sleepLoop() :
  print("starting sleep loop")
  while True :
    print(datetime.datetime.now())
    await asyncio.sleep(10)

def logMessage(origSubject, theSubject, theMessage) :
  print(f"subject: {theSubject}({origSubject})")
  print(f"message: [{yaml.dump(theMessage)}]")

async def main(config) :
  natsClient = NatsClient("cpLogger", 10)
  await natsClient.connectToServers()

  try:
    logging.info("Listening to NATS subjects:")
    listeners = [sleepLoop()]
    for aSubject in config['subjects'] :
      print("  "+aSubject)
      listeners.append(natsClient.listenToSubject(aSubject, logMessage))
    await asyncio.gather(*listeners)
  except SignalException as err :
    logging.info("Shutting down: {}".format(str(err)))
  except KeyboardInterrupt as err :
    logging.info("Shutting down: {}".format(str(err)))
  except Exception as err :
    msg = "\n ".join(traceback.format_exc().split("\n"))
    logging.info("Shutting down after exception: \n {}".format(msg))
  finally:
    await natsClient.closeConnection()

def cli() :
  configFile = './cploggerConfig.yaml'
  if cliArgs.config  : configFile = cliArgs.config
  verbose    = False
  if cliArgs.verbose : verbose = cliArgs.verbose
  config = cplogger.loadConfiguration.loadConfig(configFile, verbose)

  logging.info("ComputePods NATS logger starting")

  try :
    asyncio.run(main(config))
  except SignalException as err :
    print("")
    logging.info("Shutting down: {}".format(str(err)))
  except KeyboardInterrupt as err :
    print("")
    logging.info("Shutting down from KeyboardInterrupt: {}".format(str(err)))
  except Exception as err :
    msg = "\n ".join(traceback.format_exc().split("\n"))
    logging.info("Shutting down after exception: \n {}".format(msg))

  logging.info("ComputePods NATS logger stopping")

